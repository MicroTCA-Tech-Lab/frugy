from frugy.types import FruAreaBase, FixedField, GuidField, ArrayField
import bitstruct


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
            self.records.append(new_entry)
            if new_entry.end_of_list:
                break

        return remainder

    def size_total(self):
        return sum([v.size_total() for v in self.records])


class MultirecordEntry(FruAreaBase):
    ''' Platform Management FRU Information Storage Definition, Table 16-1 '''

    _multirecord_header_fmt = 'u8u1u3u4u8u8'

    def __init__(self, type_id: int, schema, initdict=None, format_version=2):
        self.type_id = type_id
        self.end_of_list = 0
        self.format_version = format_version
        if initdict is not None:
            initdict.pop('type', None)  # for MultirecordEntry, type is used for type identification, not for the fields
        super().__init__(schema, initdict=initdict)

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
                                self.type_id,
                                self.end_of_list,
                                0,
                                self.format_version,
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

        new_entry.type_id = type_id
        new_entry.format_version = format_version
        new_entry.end_of_list = end_of_list

        return new_entry, remainder


class PicmgEntry(MultirecordEntry):
    ''' PICMG Advanced Mezzanine Card AMC.0 Specification R2.0 '''
    ''' This stuff is shared between all instances of PICMG OEM multirecord entries '''

    _picmg_identifier = b'\x5a\x31\x00'

    def __init__(self, record_id, schema, initdict=None, format_version=2):
        self.record_id = record_id
        super().__init__(_multirecord_types_lookup_rev['PicmgEntry'],
                         schema, initdict=initdict, format_version=format_version)
    
    def _payload_prologue(self):
        return self._picmg_identifier + self.record_id.to_bytes(length=1, byteorder='little') + b'\x00'
    
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


class FmcEntry(MultirecordEntry):
    ''' This stuff is shared between all instances of ANSI/VITA FMC OEM multirecord entries '''

    _fmc_identifier = b'\xa2\x12\x00'

    def __init__(self, record_id, schema, initdict=None, format_version=2):
        self.record_id = record_id
        super().__init__(_multirecord_types_lookup_rev['FmcEntry'],
                         schema, initdict=initdict, format_version=format_version)
    
    def _payload_prologue(self):
        return self._fmc_identifier + self.record_id.to_bytes(length=1, byteorder='little')
    
    @classmethod
    def from_payload(cls, payload):
        fmc_id, payload = payload[:len(cls._fmc_identifier)], payload[len(cls._fmc_identifier):]
        rec_id, payload = payload[:1], payload[1:]
        if fmc_id != cls._fmc_identifier:
            print(f"FMC identifier mismatch: expected {cls._fmc_identifier}, received {fmc_id}")
        rec_id = int.from_bytes(rec_id, byteorder='little')
        try:
            cls_inst = globals()[_fmc_types_lookup[rec_id]]()
        except KeyError:
            raise RuntimeError(f"Unknown FMC entry 0x{rec_id:02x}")
        cls_inst._deserialize(payload)
        return cls_inst


# Lookup tables for multirecords

_multirecord_types_lookup = {
    # Standard IPMI multirecord entries
    0x01: 'DCOutput',
    0x02: 'DCLoad',
    # 'OEM' (non-standard) multirecord entries
    # PICMG Advanced Mezzanine Card AMC.0 Specification R2.0
    0xc0: 'PicmgEntry',
    # ANSI/VITA 57.1 FPGA Mezzanine Card (FMC) Standard
    0xfa: 'FmcEntry',
}

_multirecord_types_lookup_rev = {
    v: k for k, v in _multirecord_types_lookup.items()
}


_picmg_types_lookup = {
    0x16: 'ModuleCurrentRequirements',
    0x19: 'PointToPointConnectivity'
}

_picmg_types_lookup_rev = {
    v: k for k, v in _picmg_types_lookup.items()
}

_fmc_types_lookup = {
    0x00: 'FmcMainDefinition'
}

_fmc_types_lookup_rev = {
    v: k for k, v in _fmc_types_lookup.items()
}

# IPMI standard multirecords

class DCOutput(MultirecordEntry):
    ''' Platform Management FRU Information Storage Definition, Table 18-2 '''

    def __init__(self, initdict=None):
        super().__init__(_multirecord_types_lookup_rev[self.__class__.__name__], [
            ('standby_enable', FixedField('u1')),
            ('_reserved', FixedField('u3', value=0)),
            ('output_number', FixedField('u4')),
            ('nominal_voltage', FixedField('u16', div=10)),     # 10mV
            ('max_neg_voltage', FixedField('u16', div=10)),     # 10mV
            ('max_pos_voltage', FixedField('u16', div=10)),     # 10mV
            ('max_noise_pk2pk', FixedField('u16')),     # mV
            ('min_current_draw', FixedField('u16')),    # mA
            ('max_current_draw', FixedField('u16')),    # mA
        ], initdict)


class DCLoad(MultirecordEntry):
    ''' Platform Management FRU Information Storage Definition, Table 18-4 '''

    def __init__(self, initdict=None):
        super().__init__(_multirecord_types_lookup_rev[self.__class__.__name__], [
            ('_reserved', FixedField('u4', value=0)),
            ('output_number', FixedField('u4')),
            ('nominal_voltage', FixedField('u16', div=10)),     # 10mV
            ('min_voltage', FixedField('u16', div=10)),         # 10mV
            ('max_voltage', FixedField('u16', div=10)),         # 10mV
            ('max_noise_pk2pk', FixedField('u16')),     # mV
            ('min_current_load', FixedField('u16')),    # mA
            ('max_current_load', FixedField('u16')),    # mA
        ], initdict)


# PICMG AMC.0 multirecords

class ModuleCurrentRequirements(PicmgEntry):
    ''' PICMG AMC.0 Specification R2.0, Module Current Requirements record, Table 3-10 '''

    def __init__(self, initdict=None):
        super().__init__(_picmg_types_lookup_rev[self.__class__.__name__], [
            ('current_draw', FixedField('u8', value=0, div=0.1))
        ], initdict)


# Array entry classes for PointToPointConnectivity

class AmcChannelDescriptor(FruAreaBase):
    ''' PICMG AMC.0 Specification R2.0, AMC Channel Descriptor, Table 3-17 '''

    _lanes = [f'_lane{n}_port' for n in range(4)]
    _lane_unused = 0b11111

    def __init__(self, initdict=None):
        super().__init__([
            ('_reserved', FixedField('u4', value=0b1111)),
            ('_lane3_port', FixedField('u5', value=AmcChannelDescriptor._lane_unused)),
            ('_lane2_port', FixedField('u5', value=AmcChannelDescriptor._lane_unused)),
            ('_lane1_port', FixedField('u5', value=AmcChannelDescriptor._lane_unused)),
            ('_lane0_port', FixedField('u5', value=AmcChannelDescriptor._lane_unused)),
        ], initdict, mergeBitfield=True)
    
    def to_dict(self):
        return [self[l] for l in AmcChannelDescriptor._lanes if self[l] != AmcChannelDescriptor._lane_unused]
    
    def update(self, val):
        for i, l in enumerate(AmcChannelDescriptor._lanes):
            self[l] = val[i] if i < len(val) else AmcChannelDescriptor._lane_unused


class AmcLinkDescriptor(FruAreaBase):
    ''' PICMG AMC.0 Specification R2.0, AMC Link Descriptor, Table 3-19 '''

    _lane_flag_names = [f'_lane{n}_flag' for n in range(4)]

    def __init__(self, initdict=None):
        link_type_constants = {
                'pcie': 0x02,
                'pcie_advanced': 0x03,
                'pci_advanced_1': 0x04,
                'ethernet': 0x05,
                'serial_rapidio': 0x06,
                'storage': 0x07
        }
        link_type_constants.update({
            f'oem_guid_{n}': n+0xf0 for n in range(15)
        })
        super().__init__([
            ('_reserved', FixedField('u6', value=0b111111)),
            ('asymm_match', FixedField('u2', constants={
                'match_exact': 0b00,
                'match_10b': 0b01,
                'match_01b': 0b10
            })),
            ('grouping_id', FixedField('u8')),
            ('link_type_ext', FixedField('u4')),
            ('link_type', FixedField('u8', constants=link_type_constants)),
            ('_lane3_flag', FixedField('u1')),
            ('_lane2_flag', FixedField('u1')),
            ('_lane1_flag', FixedField('u1')),
            ('_lane0_flag', FixedField('u1')),
            ('channel_id', FixedField('u8')),
        ], initdict, mergeBitfield=True)

    def to_dict(self):
        result = super().to_dict()
        result['lane_flags'] = [self[f] for f in self._lane_flag_names]
        return result
    
    def update(self, val):
        for n, f in enumerate(self._lane_flag_names):
            self[f] = val['lane_flags'][n]
        del val['lane_flags']
        super().update(val)


class PointToPointConnectivity(PicmgEntry):
    ''' PICMG AMC.0 Specification R2.0, AdvancedMC Point-to-Point Connectivity record, Table 3-16 '''

    def __init__(self, initdict=None):
        super().__init__(_picmg_types_lookup_rev[self.__class__.__name__], [
            ('_guid_count', FixedField('u8', value=0)),
            ('guids', ArrayField(GuidField, num_elems_getter=lambda: self['_guid_count'])),
            ('amc_module_flag', FixedField('u1')),
            ('_reserved', FixedField('u3', value=0)),
            ('conn_dev_id', FixedField('u4', value=0)),
            ('_channel_desc_count', FixedField('u8', value=0)),
            ('channel_descriptors', ArrayField(AmcChannelDescriptor, num_elems_getter=lambda:self['_channel_desc_count'])),
            ('link_descriptors', ArrayField(AmcLinkDescriptor)),
        ], initdict)
    
    def serialize(self):
        self['_guid_count'] = self._dict['guids'].num_elems()
        self['_channel_desc_count'] = self._dict['channel_descriptors'].num_elems()
        return super().serialize()


# FMC multirecords

class FmcMainDefinition(FmcEntry):
    ''' ANSI/VITA 57.1 FMC Standard, Table 7. Subtype 0: Base Definition (fixed length and mandatory) '''

    def __init__(self, initdict=None):
        super().__init__(_fmc_types_lookup_rev[self.__class__.__name__], [
            ('module_size', FixedField('u2')),
            ('p1_connector_size', FixedField('u2')),
            ('p2_connector_size', FixedField('u2')),
            ('clock_direction', FixedField('u1')),
            ('_reserved', FixedField('u1', value=0)),
            ('p1_a_num_signals', FixedField('u8')),
            ('p1_b_num_signals', FixedField('u8')),
            ('p2_a_num_signals', FixedField('u8')),
            ('p2_b_num_signals', FixedField('u8')),
            ('p1_gbt_num_trcv', FixedField('u4')),
            ('p2_gbt_num_trcv', FixedField('u4')),
            ('tck_max_clock', FixedField('u8'))
        ], initdict)
