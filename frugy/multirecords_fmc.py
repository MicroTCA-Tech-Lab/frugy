from frugy.types import fixed_field
from frugy.multirecords import ipmi_multirecord, MultirecordEntry
from frugy.fru_registry import FruRecordType, rec_register, rec_lookup_by_id


@ipmi_multirecord(0xfa)
class FmcEntry(MultirecordEntry):
    ''' ANSI/VITA 57.1 FMC Standard '''
    ''' Superclass of all ANSI/VITA FMC OEM multirecords '''

    _fmc_identifier = b'\xa2\x12\x00'

    def _payload_prologue(self):
        return self._fmc_identifier + self._record_id.to_bytes(length=1, byteorder='little')
    
    @classmethod
    def from_payload(cls, payload):
        fmc_id, payload = payload[:len(cls._fmc_identifier)], payload[len(cls._fmc_identifier):]
        rec_id, payload = payload[0], payload[1:]

        if fmc_id != cls._fmc_identifier:
            raise RuntimeError(f"FMC identifier mismatch: expected {cls._fmc_identifier}, received {fmc_id}")

        try:
            cls_inst = rec_lookup_by_id(FruRecordType.fmc_multirecord, rec_id)()
        except KeyError:
            raise RuntimeError(f"Unknown FMC entry 0x{rec_id:02x}")

        cls_inst._deserialize(payload)
        cls_inst._record_id = rec_id
        return cls_inst


# FMC multirecords

def fmc_multirecord(rec_id):
    def register_and_set_id(cls):
        cls._record_id = rec_id
        rec_register(cls, FruRecordType.fmc_multirecord, rec_id)
        return cls
    return register_and_set_id

def fmc_secondary(cls):
    rec_register(cls, FruRecordType.fmc_secondary)
    return cls


@fmc_multirecord(0x00)
class FmcMainDefinition(FmcEntry):
    ''' ANSI/VITA 57.1 FMC Standard, Table 7 '''

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
            'm2c': 0b0,
            'c2m': 0b1,
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