"""
SPDX-License-Identifier: BSD-3-Clause
Copyright (c) 2020 Deutsches Elektronen-Synchrotron DESY.
See LICENSE.txt for license details.
"""

from frugy.types import fixed_field, bytearray_field
from frugy.multirecords import ipmi_multirecord, MultirecordEntry


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


@ipmi_multirecord(0x01)
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


@ipmi_multirecord(0x02)
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


@ipmi_multirecord(0x03)
class MgmtAccessRecord(MultirecordEntry):
    ''' Platform Management FRU Information Storage Definition, Table 18-6 '''

    _schema = [
        ('id', fixed_field('u8', constants={
            'sys_mgmt_url': 1,
            'sys_name': 2,
            'sys_ping_addr': 3,
            'comp_mgmt_url': 4,
            'comp_name': 5,
            'comp_ping_addr': 6,
            'sys_unique_id': 7
        })),
        # TODO: edge case 'sys_unique_id' (GUID) needs conversion between string and GUID
        # For now we assume the blob is always a string
        ('blob', bytearray_field(hex=False)),
    ]
