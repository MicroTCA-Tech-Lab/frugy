from frugy.types import fixed_field
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
