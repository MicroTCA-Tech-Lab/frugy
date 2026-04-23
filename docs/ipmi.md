
# IPMI records


## CommonHeader
Platform Management FRU Information Storage Definition, Table 8-1

|Name                                    |Type                |Opt                           
|----------------------------------------|--------------------|------------------------------|
|`internal_use_offs`                     |int (u8)            |                              |
|`chassis_info_offs`                     |int (u8)            |                              |
|`board_info_offs`                       |int (u8)            |                              |
|`product_info_offs`                     |int (u8)            |                              |
|`multirecord_offs`                      |int (u8)            |                              |

<br>


## ChassisInfo
Platform Management FRU Information Storage Definition, Table 10-1

|Name                                    |Type                |Opt                           
|----------------------------------------|--------------------|------------------------------|
|`type`                                  |int (u8)            |                              |
|`part_number`                           |str                 |                              |
|`serial_number`                         |str                 |                              |
|`custom_info_fields`                    |strarray            |                              |

<br>


## BoardInfo
Platform Management FRU Information Storage Definition, Table 11-1

|Name                                    |Type                |Opt                           
|----------------------------------------|--------------------|------------------------------|
|`language_code`                         |int (u8)            |                              |
|`mfg_date_time`                         |int (u24)           |                              |
|`manufacturer`                          |str                 |                              |
|`product_name`                          |str                 |                              |
|`serial_number`                         |str                 |                              |
|`part_number`                           |str                 |                              |
|`fru_file_id`                           |str                 |                              |
|`custom_info_fields`                    |strarray            |                              |

<br>


## ProductInfo
Platform Management FRU Information Storage Definition, Table 12-1

|Name                                    |Type                |Opt                           
|----------------------------------------|--------------------|------------------------------|
|`language_code`                         |int (u8)            |                              |
|`manufacturer`                          |str                 |                              |
|`product_name`                          |str                 |                              |
|`part_number`                           |str                 |                              |
|`version`                               |str                 |                              |
|`serial_number`                         |str                 |                              |
|`asset_tag`                             |str                 |                              |
|`fru_file_id`                           |str                 |                              |
|`custom_info_fields`                    |strarray            |                              |

<br>


## InternalUse
Platform Management FRU Information Storage Definition, Table 9-1

|Name                                    |Type                |Opt                           
|----------------------------------------|--------------------|------------------------------|
|`data`                                  |bytes               |                              |

<br>


## PowerSupplyInformation
Platform Management FRU Information Storage Definition, Table 18-1

|Name                                    |Type                |Opt                           
|----------------------------------------|--------------------|------------------------------|
|`predictive_fail_lower_thresh`          |int (u8)            |                              |
|`combined_wattage`                      |int (u16)           |`no_combined_voltages`        |
|`voltage1`                              |int (u4)            |`12v`, `-12v`, `5v`, `3.3v`   |
|`voltage2`                              |int (u4)            |`12v`, `-12v`, `5v`, `3.3v`   |
|`holdup_time`                           |int (u4)            |                              |
|`peak_capacity`                         |int (u12)           |`unspecified`                 |
|`pin_polarity`                          |int (u1)            |                              |
|`hot_swap`                              |int (u1)            |                              |
|`autoswitch`                            |int (u1)            |                              |
|`pfc`                                   |int (u1)            |                              |
|`predictive_fail_support`               |int (u1)            |                              |
|`dropout_tolerance`                     |int (u8)            |                              |
|`high_freq`                             |int (u8)            |`only_dc`                     |
|`low_freq`                              |int (u8)            |`accepts_dc`                  |
|`high_input_voltage_2`                  |int (s16)           |                              |
|`low_input_voltage_2`                   |int (s16)           |                              |
|`high_input_voltage_1`                  |int (s16)           |                              |
|`low_input_voltage_1`                   |int (s16)           |                              |
|`inrush_interval`                       |int (u8)            |                              |
|`inrush_current`                        |int (u8)            |`unspecified`                 |
|`peak_va`                               |int (u16)           |`unspecified`                 |
|`overall_capacity`                      |int (u12)           |                              |

<br>


## DCOutput
Platform Management FRU Information Storage Definition, Table 18-2

|Name                                    |Type                |Opt                           
|----------------------------------------|--------------------|------------------------------|
|`standby_enable`                        |int (u1)            |                              |
|`output_number`                         |int (u4)            |`P1_VADJ`, `P1_3P3V`, `P1_12P0V`, `P1_VIO_B_M2C`, `P1_VREF_A_M2C`, `P1_VREF_B_M2C`, `P2_VADJ`, `P2_3P3V`, `P2_12P0V`, `P2_VIO_B_M2C`, `P2_VREF_A_M2C`, `P2_VREF_B_M2C`|
|`nominal_voltage`                       |int (u16)           |                              |
|`max_neg_voltage`                       |int (u16)           |                              |
|`max_pos_voltage`                       |int (u16)           |                              |
|`max_noise_pk2pk`                       |int (u16)           |                              |
|`min_current_draw`                      |int (u16)           |                              |
|`max_current_draw`                      |int (u16)           |                              |

<br>


## DCLoad
Platform Management FRU Information Storage Definition, Table 18-4

|Name                                    |Type                |Opt                           
|----------------------------------------|--------------------|------------------------------|
|`output_number`                         |int (u4)            |`P1_VADJ`, `P1_3P3V`, `P1_12P0V`, `P1_VIO_B_M2C`, `P1_VREF_A_M2C`, `P1_VREF_B_M2C`, `P2_VADJ`, `P2_3P3V`, `P2_12P0V`, `P2_VIO_B_M2C`, `P2_VREF_A_M2C`, `P2_VREF_B_M2C`|
|`nominal_voltage`                       |int (u16)           |                              |
|`min_voltage`                           |int (u16)           |                              |
|`max_voltage`                           |int (u16)           |                              |
|`max_noise_pk2pk`                       |int (u16)           |                              |
|`min_current_load`                      |int (u16)           |                              |
|`max_current_load`                      |int (u16)           |                              |

<br>


## MgmtAccessRecord
Platform Management FRU Information Storage Definition, Table 18-6

|Name                                    |Type                |Opt                           
|----------------------------------------|--------------------|------------------------------|
|`id`                                    |int (u8)            |`sys_mgmt_url`, `sys_name`, `sys_ping_addr`, `comp_mgmt_url`, `comp_name`, `comp_ping_addr`, `sys_unique_id`|
|`blob`                                  |bytes               |                              |

<br>

