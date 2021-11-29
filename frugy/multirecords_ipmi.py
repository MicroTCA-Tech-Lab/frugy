###########################################################################
#      ____  _____________  __    __  __ _           _____ ___   _        #
#     / __ \/ ____/ ___/\ \/ /   |  \/  (_)__ _ _ __|_   _/ __| /_\  (R)  #
#    / / / / __/  \__ \  \  /    | |\/| | / _| '_/ _ \| || (__ / _ \      #
#   / /_/ / /___ ___/ /  / /     |_|  |_|_\__|_| \___/|_| \___/_/ \_\     #
#  /_____/_____//____/  /_/      T  E  C  H  N  O  L  O  G  Y   L A B     #
#                                                                         #
#          Copyright 2021 Deutsches Elektronen-Synchrotron DESY.          #
#                  SPDX-License-Identifier: BSD-3-Clause                  #
#                                                                         #
###########################################################################

from frugy.types import FixedField, BytearrayField
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
fmc_voltages_total = [f'{p}_{v}' for p in ['P1', 'P2']
                      for v in fmc_voltages_per_port]
fmc_output_constants = {name: idx for idx,
                        name in enumerate(fmc_voltages_total)}


@ipmi_multirecord(0x01)
class DCOutput(MultirecordEntry):
    ''' Platform Management FRU Information Storage Definition, Table 18-2 '''

    # TODO: add unit metadata to fields
    _schema = [
        ('standby_enable', FixedField, 'u1'),
        ('_reserved', FixedField, 'u3', {'default': 0}),
        ('output_number', FixedField, 'u4', {
         'constants': fmc_output_constants}),
        ('nominal_voltage', FixedField, 'u16', {'div': 10}),     # 10mV
        ('max_neg_voltage', FixedField, 'u16', {'div': 10}),     # 10mV
        ('max_pos_voltage', FixedField, 'u16', {'div': 10}),     # 10mV
        ('max_noise_pk2pk', FixedField, 'u16'),     # mV
        ('min_current_draw', FixedField, 'u16'),    # mA
        ('max_current_draw', FixedField, 'u16'),    # mA
    ]


@ipmi_multirecord(0x02)
class DCLoad(MultirecordEntry):
    ''' Platform Management FRU Information Storage Definition, Table 18-4 '''

    _schema = [
        ('_reserved', FixedField, 'u4', {'default': 0}),
        ('output_number', FixedField, 'u4', {
         'constants': fmc_output_constants}),
        ('nominal_voltage', FixedField, 'u16', {'div': 10}),     # 10mV
        ('min_voltage', FixedField, 'u16', {'div': 10}),         # 10mV
        ('max_voltage', FixedField, 'u16', {'div': 10}),         # 10mV
        ('max_noise_pk2pk', FixedField, 'u16'),     # mV
        ('min_current_load', FixedField, 'u16'),    # mA
        ('max_current_load', FixedField, 'u16'),    # mA
    ]


@ipmi_multirecord(0x03)
class MgmtAccessRecord(MultirecordEntry):
    ''' Platform Management FRU Information Storage Definition, Table 18-6 '''

    _schema = [
        ('id', FixedField, 'u8', {'constants': {
            'sys_mgmt_url': 1,
            'sys_name': 2,
            'sys_ping_addr': 3,
            'comp_mgmt_url': 4,
            'comp_name': 5,
            'comp_ping_addr': 6,
            'sys_unique_id': 7
        }}),
        # TODO: edge case 'sys_unique_id' (GUID) needs conversion between string and GUID
        # For now we assume the blob is always a string
        ('blob', BytearrayField, None, {'hex': False}),
    ]
