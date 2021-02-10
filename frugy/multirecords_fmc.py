"""
SPDX-License-Identifier: BSD-3-Clause
Copyright (c) 2020 Deutsches Elektronen-Synchrotron DESY.
See LICENSE.txt for license details.
"""

from frugy.types import FixedField
from frugy.multirecords import ipmi_multirecord, MultirecordEntry
from frugy.fru_registry import FruRecordType, rec_register, rec_lookup_by_id

import bitstruct

@ipmi_multirecord(0xfa)
class FmcEntry(MultirecordEntry):
    ''' ANSI/VITA 57.1 FMC Standard '''
    ''' Superclass of all ANSI/VITA FMC OEM multirecords '''

    _fmc_identifier = 0x12a2

    def _payload_prologue(self):
        return self._fmc_identifier.to_bytes(3, 'little') + self._record_id.to_bytes(length=1, byteorder='little')
    
    @classmethod
    def from_payload(cls, payload):
        if not MultirecordEntry.opalkelly_workaround_enabled:
            # Opal Kelly FMC records seem to skip the manufacturer ID ...
            fmc_id, payload = payload[:3], payload[3:]
            rec_id, payload = payload[0], payload[1:]
            fmc_id = int.from_bytes(fmc_id, 'little')

            if fmc_id != cls._fmc_identifier:
                raise ValueError(f"FMC identifier mismatch: expected 0x{cls._fmc_identifier:06x}, received 0x{fmc_id:06x} ({fmc_id})")
        else:
            # Opal Kelly FMC records seem to have the rec_id as _last_ instead of first byte
            rec_id, payload = payload[-1], payload[:-1]


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
        ('module_size', FixedField, 'u2', {'constants': {
            'single_width': 0b00,
            'double_width': 0b01
        }}),
        ('p1_connector_size', FixedField, 'u2', {'constants': {
            'lpc': 0b00,
            'hpc': 0b01
        }}),
        ('p2_connector_size', FixedField, 'u2', {'constants': {
            'lpc': 0b00,
            'hpc': 0b01,
            'not_fitted': 0b11,
        }}),
        ('clock_direction', FixedField, 'u1', {'constants': {
            'm2c': 0b0,
            'c2m': 0b1,
        }}),
        ('_reserved', FixedField, 'u1', {'default': 0}),
        ('p1_a_num_signals', FixedField, 'u8'),
        ('p1_b_num_signals', FixedField, 'u8'),
        ('p2_a_num_signals', FixedField, 'u8'),
        ('p2_b_num_signals', FixedField, 'u8'),
        ('p1_gbt_num_trcv', FixedField, 'u4'),
        ('p2_gbt_num_trcv', FixedField, 'u4'),
        ('tck_max_clock', FixedField, 'u8')
    ]


@fmc_multirecord(0x01)
class FmcPlusMainDefinition(FmcEntry):
    ''' ANSI/VITA 57.4-2018 FMC+ Standard, Table 5.3.1-1 '''

    _schema = [
        ('module_size', FixedField, 'u2', {'constants': {
            'single_width': 0b00,
            'double_width': 0b01
        }}),
        ('p1_p3_connector_size', FixedField, 'u2', {'constants': {
            'lpc': 0b00,
            'hpc': 0b01,
            'hspc': 0b10,
            'p1_hspc_p3_hspce': 0b11,
        }}),
        ('p2_p4_connector_size', FixedField, 'u3', {'constants': {
            'lpc': 0b000,
            'hpc': 0b001,
            'hspc': 0b010,
            'p2_hspc_p4_hspce': 0b011,
            'not_fitted': 0b111,
        }}),
        ('clock_direction', FixedField, 'u1', {'constants': {
            'm2c': 0b0,
            'c2m': 0b1,
        }}),
        ('p1_a_num_signals', FixedField, 'u8'),
        ('p2_a_num_signals', FixedField, 'u8'),
        ('_p2_b_num_sig_1_0', FixedField, 'u2'),
        ('p1_b_num_signals', FixedField, 'u6'),
        ('_p1_gbt_num_trcv_3_0', FixedField, 'u4'),
        ('_p2_b_num_sig_5_2', FixedField, 'u4'),
        ('p2_gbt_num_trcv', FixedField, 'u6'),
        ('_p1_gbt_num_trcv_5_4', FixedField, 'u2'),
        ('tck_max_clock', FixedField, 'u8')
    ]

    # Convert FMC+ bit-twiddled fields to / from plain values

    def to_dict(self):
        result = super().to_dict()
        # re-order dict items so the result looks nice
        p2nt, tck = result['p2_gbt_num_trcv'], result['tck_max_clock']
        del result['p2_gbt_num_trcv']
        del result['tck_max_clock']
        result['p2_b_num_signals'] = ord(bitstruct.pack(
            'u2u4u2',
            0,
            self['_p2_b_num_sig_5_2'],
            self['_p2_b_num_sig_1_0']
        ))
        result['p1_gbt_num_trcv'] = ord(bitstruct.pack(
            'u2u2u4',
            0,
            self['_p1_gbt_num_trcv_5_4'],
            self['_p1_gbt_num_trcv_3_0']
        ))
        result['p2_gbt_num_trcv'] = p2nt
        result['tck_max_clock'] = tck
        return result
    
    def update(self, val):
        _, self['_p2_b_num_sig_5_2'], self['_p2_b_num_sig_1_0'] = bitstruct.unpack(
            'u2u4u2',
            int.to_bytes(val['p2_b_num_signals'], 1, byteorder='little')
        )
        _, self['_p1_gbt_num_trcv_5_4'], self['_p1_gbt_num_trcv_3_0'] = bitstruct.unpack(
            'u2u2u4',
            int.to_bytes(val['p1_gbt_num_trcv'], 1, byteorder='little')
        )
        del val['p2_b_num_signals']
        del val['p1_gbt_num_trcv']
        super().update(val)
