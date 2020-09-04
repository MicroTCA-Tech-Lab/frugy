
# FMC records


## FmcMainDefinition
ANSI/VITA 57.1 FMC Standard, Table 7

|Name                     |Type                |Opt                                                         
|-------------------------|--------------------|------------------------------------------------------------|
|`module_size`            |int (u2)            |single_width, double_width                                  |
|`p1_connector_size`      |int (u2)            |lpc, hpc                                                    |
|`p2_connector_size`      |int (u2)            |lpc, hpc, not_fitted                                        |
|`clock_direction`        |int (u1)            |m2c, c2m                                                    |
|`p1_a_num_signals`       |int (u8)            |                                                            |
|`p1_b_num_signals`       |int (u8)            |                                                            |
|`p2_a_num_signals`       |int (u8)            |                                                            |
|`p2_b_num_signals`       |int (u8)            |                                                            |
|`p1_gbt_num_trcv`        |int (u4)            |                                                            |
|`p2_gbt_num_trcv`        |int (u4)            |                                                            |
|`tck_max_clock`          |int (u8)            |                                                            |
