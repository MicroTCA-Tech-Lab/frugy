
# FMC records


## FmcMainDefinition
ANSI/VITA 57.1 FMC Standard, Table 7

|Name                                    |Type                |Opt                           
|----------------------------------------|--------------------|------------------------------|
|`module_size`                           |int (u2)            |`single_width`, `double_width`|
|`p1_connector_size`                     |int (u2)            |`lpc`, `hpc`                  |
|`p2_connector_size`                     |int (u2)            |`lpc`, `hpc`, `not_fitted`    |
|`clock_direction`                       |int (u1)            |`m2c`, `c2m`                  |
|`p1_a_num_signals`                      |int (u8)            |                              |
|`p1_b_num_signals`                      |int (u8)            |                              |
|`p2_a_num_signals`                      |int (u8)            |                              |
|`p2_b_num_signals`                      |int (u8)            |                              |
|`p1_gbt_num_trcv`                       |int (u4)            |                              |
|`p2_gbt_num_trcv`                       |int (u4)            |                              |
|`tck_max_clock`                         |int (u8)            |                              |

<br>


## FmcPlusMainDefinition
ANSI/VITA 57.4-2018 FMC+ Standard, Table 5.3.1-1

|Name                                    |Type                |Opt                           
|----------------------------------------|--------------------|------------------------------|
|`module_size`                           |int (u2)            |`single_width`, `double_width`|
|`p1_p3_connector_size`                  |int (u2)            |`lpc`, `hpc`, `hspc`, `p1_hspc_p3_hspce`|
|`p2_p4_connector_size`                  |int (u3)            |`lpc`, `hpc`, `hspc`, `p2_hspc_p4_hspce`, `not_fitted`|
|`clock_direction`                       |int (u1)            |`m2c`, `c2m`                  |
|`p1_a_num_signals`                      |int (u8)            |                              |
|`p2_a_num_signals`                      |int (u8)            |                              |
|`p1_b_num_signals`                      |int (u6)            |                              |
|`p2_gbt_num_trcv`                       |int (u6)            |                              |
|`tck_max_clock`                         |int (u8)            |                              |

<br>

