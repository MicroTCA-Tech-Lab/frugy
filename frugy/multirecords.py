from frugy.types import FruAreaBase, fixed_field, GuidField, array_field
import bitstruct
from bidict import bidict


class MultirecordArea:
    ''' This is just a daisy-chain of MultirecordEntry objects '''

    def __init__(self, initdict=None):
        self.records = []
        if initdict is not None:
            self.update(initdict)
    
    def update(self, initdict):
        self.records = []
        for v in initdict:
            try:
                constructor = globals()[v['type']]
            except KeyError:
                raise RuntimeError(f"Unknown multirecord entry {v['type']}")
            self.records.append(constructor(v))
    
    def __repr__(self):
        return self.to_dict().__repr__()

    def to_dict(self):
        return [v.to_dict() for v in self.records]
    
    def serialize(self):
        result = b''
        for i, v in enumerate(self.records):
            v.end_of_list = 1 if i == len(self.records)-1 else 0
            result += v.serialize()
        return result
    
    def deserialize(self, input):
        self.records = []
        remainder = input
        while len(remainder):
            new_entry, remainder = MultirecordEntry.deserialize(remainder)
            if new_entry is not None:
                self.records.append(new_entry)
            if new_entry is None or new_entry.end_of_list:
                break

        return remainder

    def size_total(self):
        return sum([v.size_total() for v in self.records])


class MultirecordEntry(FruAreaBase):
    ''' Platform Management FRU Information Storage Definition, Table 16-1 '''

    _format_version = 2
    _multirecord_header_fmt = 'u8u1u3u4u8u8'

    def __init__(self, initdict=None):
        self.end_of_list = 0
        if initdict is not None:
            initdict.pop('type', None)  # for MultirecordEntry, type is used for type identification, not for the fields
        super().__init__(initdict=initdict)

    def size_payload(self):
        # Add header size
        return super().size_payload() + 5 + len(self._payload_prologue())
    
    def _payload_prologue(self):
        # data prepended before actual payload by subclasses
        return b''

    def to_dict(self):
        # save type identification
        result = {'type': self.__class__.__name__}
        result.update(super().to_dict())
        return result

    def serialize(self):
        payload = self._payload_prologue() + super().serialize()
        payload_cksum = (-sum(payload)) & 0xff
        header = bitstruct.pack(self._multirecord_header_fmt,
                                self._type_id,
                                self.end_of_list,
                                0,
                                self._format_version,
                                len(payload),
                                payload_cksum)
        header_cksum = (-sum(header)) & 0xff
        header += header_cksum.to_bytes(length=1, byteorder='little')
        return header + payload

    @classmethod
    def deserialize(cls, input):
        header_fmt_complt = MultirecordEntry._multirecord_header_fmt + 'u8'
        header_len = bitstruct.calcsize(header_fmt_complt) // 8
        type_id, end_of_list, _, format_version, \
        payload_len, payload_cksum, _ = bitstruct.unpack(header_fmt_complt, input)
        header, remainder = input[:header_len], input[header_len:]
        payload, remainder = remainder[:payload_len], remainder[payload_len:]

        try:
            if sum(header) & 0xff != 0:
                raise RuntimeError("MultirecordEntry header checksum invalid")
            if (sum(payload) + payload_cksum) & 0xff != 0:
                raise RuntimeError("MultirecordEntry payload checksum invalid")

            try:
                cls_id = globals()[_multirecord_types_lookup[type_id]]
            except KeyError:
                raise RuntimeError(f"Unknown multirecord type 0x{type_id:02x}")

            if hasattr(cls_id, 'from_payload'):
                new_entry = cls_id.from_payload(payload)
            else:
                new_entry = cls_id()
                new_entry._deserialize(payload)

            new_entry._type_id = type_id
            new_entry._format_version = format_version
            new_entry.end_of_list = end_of_list

        except RuntimeError as e:
            print(f"Failed to deserialize multirecord, type_id=0x{type_id:02x}, end_of_list={end_of_list}, "
                  f"format_version={format_version}, len={len(header)+len(payload)}")
            print(f"reason: {e}")
            print(f"header: {' '.join('%02x'%x for x in header)}, payload: {' '.join('%02x'%x for x in payload)}")
            new_entry = None

        return new_entry, remainder


# Lookup tables for multirecord type IDs

_multirecord_types_lookup = bidict({
    # Standard IPMI multirecord entries
    0x01: 'DCOutput',
    0x02: 'DCLoad',
    # 'OEM' (non-standard) multirecord entries
    # PICMG Advanced Mezzanine Card AMC.0 Specification R2.0
    0xc0: 'PicmgEntry',
    # ANSI/VITA 57.1 FPGA Mezzanine Card (FMC) Standard
    0xfa: 'FmcEntry',
})

def multirecord(cls):
    cls._type_id = _multirecord_types_lookup.inverse[cls.__name__]
    return cls

@multirecord
class PicmgEntry(MultirecordEntry):
    ''' PICMG Advanced Mezzanine Card AMC.0 Specification R2.0 '''
    ''' This stuff is shared between all instances of PICMG OEM multirecord entries '''

    _picmg_identifier = b'\x5a\x31\x00'

    def _payload_prologue(self):
        return self._picmg_identifier + self._record_id.to_bytes(length=1, byteorder='little') + b'\x00'
    
    @classmethod
    def from_payload(cls, payload):
        picmg_id, payload = payload[:len(cls._picmg_identifier)], payload[len(cls._picmg_identifier):]
        rec_id, payload = payload[:1], payload[1:]
        zero_byte, payload = payload[:1], payload[1:]
        if picmg_id != cls._picmg_identifier:
            raise RuntimeError(f"PICMG identifier mismatch: expected {cls._picmg_identifier}, received {picmg_id}")
        if zero_byte != b'\x00':
            raise RuntimeError("PICMG zero byte not found")
        rec_id = int.from_bytes(rec_id, byteorder='little')
        try:
            cls_inst = globals()[_picmg_types_lookup[rec_id]]()
        except KeyError:
            raise RuntimeError(f"Unknown PICMG entry 0x{rec_id:02x}")
        cls_inst._deserialize(payload)
        return cls_inst

@multirecord
class FmcEntry(MultirecordEntry):
    ''' This stuff is shared between all instances of ANSI/VITA FMC OEM multirecord entries '''

    _fmc_identifier = b'\xa2\x12\x00'

    def _payload_prologue(self):
        return self._fmc_identifier + self._record_id.to_bytes(length=1, byteorder='little')
    
    @classmethod
    def from_payload(cls, payload):
        fmc_id, payload = payload[:len(cls._fmc_identifier)], payload[len(cls._fmc_identifier):]
        rec_id, payload = payload[:1], payload[1:]
        if fmc_id != cls._fmc_identifier:
            raise RuntimeError(f"FMC identifier mismatch: expected {cls._fmc_identifier}, received {fmc_id}")
        rec_id = int.from_bytes(rec_id, byteorder='little')
        try:
            cls_inst = globals()[_fmc_types_lookup[rec_id]]()
        except KeyError:
            raise RuntimeError(f"Unknown FMC entry 0x{rec_id:02x}")
        cls_inst._deserialize(payload)
        cls_inst._record_id = rec_id
        return cls_inst


# Lookup tables for OEM multirecord record IDs

_picmg_types_lookup = bidict({
    0x16: 'ModuleCurrentRequirements',
    0x19: 'PointToPointConnectivity',
    0x2d: 'ClockConfigRecord'
})

def picmg_record(cls):
    cls._record_id = _picmg_types_lookup.inverse[cls.__name__]
    return cls

_fmc_types_lookup = bidict({
    0x00: 'FmcMainDefinition'
})

def fmc_record(cls):
    cls._record_id = _fmc_types_lookup.inverse[cls.__name__]
    return cls

# IPMI standard multirecords

fmc_voltages_per_port = [
    'VADJ',
    '3P3V',
    '12P0V',
    'VIO_B_M2C',
    'VREF_A_M2C',
    'VREF_B_M2C'
]
fmc_voltages_total = [f'{p}_{v}' for p in ['P1', 'P2'] for v in fmc_voltages_per_port]
fmc_output_constants = {name: idx for idx, name in enumerate(fmc_voltages_total)}

@multirecord
class DCOutput(MultirecordEntry):
    ''' Platform Management FRU Information Storage Definition, Table 18-2 '''

    _schema = [
        ('standby_enable', fixed_field('u1')),
        ('_reserved', fixed_field('u3', default=0)),
        ('output_number', fixed_field('u4', constants=fmc_output_constants)),
        ('nominal_voltage', fixed_field('u16', div=10)),     # 10mV
        ('max_neg_voltage', fixed_field('u16', div=10)),     # 10mV
        ('max_pos_voltage', fixed_field('u16', div=10)),     # 10mV
        ('max_noise_pk2pk', fixed_field('u16')),     # mV
        ('min_current_draw', fixed_field('u16')),    # mA
        ('max_current_draw', fixed_field('u16')),    # mA
    ]

@multirecord
class DCLoad(MultirecordEntry):
    ''' Platform Management FRU Information Storage Definition, Table 18-4 '''

    _schema = [
        ('_reserved', fixed_field('u4', default=0)),
        ('output_number', fixed_field('u4', constants=fmc_output_constants)),
        ('nominal_voltage', fixed_field('u16', div=10)),     # 10mV
        ('min_voltage', fixed_field('u16', div=10)),         # 10mV
        ('max_voltage', fixed_field('u16', div=10)),         # 10mV
        ('max_noise_pk2pk', fixed_field('u16')),     # mV
        ('min_current_load', fixed_field('u16')),    # mA
        ('max_current_load', fixed_field('u16')),    # mA
    ]


# PICMG AMC.0 multirecords

@picmg_record
class ModuleCurrentRequirements(PicmgEntry):
    ''' PICMG AMC.0 Specification R2.0, Module Current Requirements record, Table 3-10 '''

    _schema = [
        ('current_draw', fixed_field('u8', div=0.1))
    ]

# Array entry classes for PointToPointConnectivity

class AmcChannelDescriptor(FruAreaBase):
    ''' PICMG AMC.0 Specification R2.0, AMC Channel Descriptor, Table 3-17 '''

    _lanes = [f'_lane{n}_port' for n in range(4)]
    _lane_unused = 0b11111

    _schema = [
        ('_reserved', fixed_field('u4', default=0b1111)),
        ('_lane3_port', fixed_field('u5', default=_lane_unused)),
        ('_lane2_port', fixed_field('u5', default=_lane_unused)),
        ('_lane1_port', fixed_field('u5', default=_lane_unused)),
        ('_lane0_port', fixed_field('u5', default=_lane_unused)),
    ]
    _mergeBitfield = True
    
    def to_dict(self):
        return [self[l] for l in AmcChannelDescriptor._lanes if self[l] != AmcChannelDescriptor._lane_unused]
    
    def update(self, val):
        for i, l in enumerate(AmcChannelDescriptor._lanes):
            self[l] = val[i] if i < len(val) else AmcChannelDescriptor._lane_unused


class AmcLinkDescriptor(FruAreaBase):
    ''' PICMG AMC.0 Specification R2.0, AMC Link Descriptor, Table 3-19 '''

    _lane_flag_names = [f'_lane{n}_flag' for n in range(4)]

    _link_type_standard_constants = {
            'pcie': 0x02,
            'pcie_advanced': 0x03,
            'pci_advanced_1': 0x04,
            'ethernet': 0x05,
            'serial_rapidio': 0x06,
            'storage': 0x07
    }
    _link_type_oem_constants = {
        f'oem_guid_{n}': n+0xf0 for n in range(15)
    }

    _schema = [
        ('_reserved', fixed_field('u6', default=0b111111)),
        ('asymm_match', fixed_field('u2', constants={
            'match_exact': 0b00,
            'match_10b': 0b01,
            'match_01b': 0b10
        })),
        ('grouping_id', fixed_field('u8')),
        ('link_type_ext', fixed_field('u4', default=0)),
        ('link_type', fixed_field('u8', constants={
            **_link_type_standard_constants,
            **_link_type_oem_constants
        })),
        ('_lane3_flag', fixed_field('u1')),
        ('_lane2_flag', fixed_field('u1')),
        ('_lane1_flag', fixed_field('u1')),
        ('_lane0_flag', fixed_field('u1')),
        ('channel_id', fixed_field('u8')),
    ]
    _mergeBitfield = True

    def to_dict(self):
        result = super().to_dict()
        result['lane_flags'] = [self[f] for f in self._lane_flag_names]
        return result
    
    def update(self, val):
        for n, f in enumerate(self._lane_flag_names):
            self[f] = val['lane_flags'][n]
        del val['lane_flags']
        super().update(val)


@picmg_record
class PointToPointConnectivity(PicmgEntry):
    ''' PICMG AMC.0 Specification R2.0, AdvancedMC Point-to-Point Connectivity record, Table 3-16 '''

    _schema = [
        ('_guid_count', fixed_field('u8', default=0)),
        ('guids', array_field(GuidField, num_elems_field='_guid_count')),
        ('record_type', fixed_field('u1', constants={
            'amc_module': 1,
            'on_carrier_device': 0
        })),
        ('_reserved', fixed_field('u3', default=0)),
        ('connected_dev_id', fixed_field('u4', default=0)),
        ('_channel_desc_count', fixed_field('u8', default=0)),
        ('channel_descriptors', array_field(AmcChannelDescriptor, num_elems_field='_channel_desc_count')),
        ('link_descriptors', array_field(AmcLinkDescriptor)),
    ]


class DirectClockDescriptor(FruAreaBase):
    ''' PICMG AMC.0 Specification R2.0, Direct Clock descriptor, Table 3-38 '''

    _schema = [
        ('_reserved', fixed_field('u6', default=0)),
        ('pll_connect', fixed_field('u1')),
        ('asymm_match', fixed_field('u1', constants={
            'clk_source': 1,
            'clk_receiver': 0
        })),
        ('family', fixed_field('u8', constants={
            'unspecified': 0,
            'sonet_sdh_pdh': 1,
            'pcie_reserved': 2
        })),
        ('accuracy', fixed_field('u8')),
        ('frequency', fixed_field('u32')),
        ('freq_min', fixed_field('u32')),
        ('freq_max', fixed_field('u32')),
    ]

class IndirectClockDescriptor(FruAreaBase):
    ''' PICMG AMC.0 Specification R2.0, Indirect Clock descriptor, Table 3-37 '''

    _schema = [
        ('_reserved', fixed_field('u6', default=0)),
        ('pll_connect', fixed_field('u1')),
        ('asymm_match', fixed_field('u1', constants={
            'clk_src': 1,
            'clk_recv': 0
        })),
        ('dep_clk_id', fixed_field('u8')),
    ]

class ClockConfigDescriptor(FruAreaBase):
    ''' PICMG AMC.0 Specification R2.0, Clock Configuration descriptor, Table 3-36 '''
    
    _schema = [
        ('clk_id', fixed_field('u8', constants={
            # Predefined Clock IDs for AMC clocks (Table 3-33)
            # TODO: Are these enough, or do we also need the ATCA Backplane clocks (Table 3-34)?
            'TCLKA': 1,
            'TCLKB': 2,
            'TCLKC': 3,
            'TCLKD': 4,
            'FCLKA': 5,
        })),
        ('_reserved', fixed_field('u7')),
        ('activation', fixed_field('u1', constants={
            'by_carrier': 0,
            'by_application': 1
        })),
        ('_indirect_clk_desc_count', fixed_field('u8', default=0)),
        ('_direct_clk_desc_count', fixed_field('u8', default=0)),
        ('indirect_clk_desc', array_field(IndirectClockDescriptor, num_elems_field='_indirect_clk_desc_count')),
        ('direct_clk_desc', array_field(DirectClockDescriptor, num_elems_field='_direct_clk_desc_count')),
    ]

@picmg_record
class ClockConfigRecord(PicmgEntry):
    ''' PICMG AMC.0 Specification R2.0, Clock Configuration record, Table 3-35 '''

    _schema = [
        # first 8 bits is 'Clock Resource ID', Table 3-31
        ('resource_type', fixed_field('u2', constants={
            'on_carrier': 0b00,
            'amc_module': 0b01,
            'backplane': 0b10
        })),
        ('_reserved', fixed_field('u2', default=0)),
        ('dev_id', fixed_field('u4')),
        ('_conf_desc_count', fixed_field('u8', default=0)),
        ('conf_desc', array_field(ClockConfigDescriptor, num_elems_field='_conf_desc_count')),
    ]


# FMC multirecords

@fmc_record
class FmcMainDefinition(FmcEntry):
    ''' ANSI/VITA 57.1 FMC Standard, Table 7. Subtype 0: Base Definition (fixed length and mandatory) '''

    _schema = [
        ('module_size', fixed_field('u2', constants={
            'single_width': 0b00,
            'double_width': 0b01
        })),
        ('p1_connector_size', fixed_field('u2', constants={
            'lpc': 0b00,
            'hpc': 0b01
        })),
        ('p2_connector_size', fixed_field('u2', constants={
            'lpc': 0b00,
            'hpc': 0b01,
            'not_fitted': 0b11,
        })),
        ('clock_direction', fixed_field('u1', constants={
            'mezzanine_to_carrier': 0b0,
            'carrier_to_mezzanine': 0b1,
        })),
        ('_reserved', fixed_field('u1', default=0)),
        ('p1_a_num_signals', fixed_field('u8')),
        ('p1_b_num_signals', fixed_field('u8')),
        ('p2_a_num_signals', fixed_field('u8')),
        ('p2_b_num_signals', fixed_field('u8')),
        ('p1_gbt_num_trcv', fixed_field('u4')),
        ('p2_gbt_num_trcv', fixed_field('u4')),
        ('tck_max_clock', fixed_field('u8'))
    ]
