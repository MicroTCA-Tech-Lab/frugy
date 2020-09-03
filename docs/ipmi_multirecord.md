
# ipmi_multirecord records


## DCOutput

|Name                     |Type                |Opt                                                         
|-------------------------|--------------------|------------------------------------------------------------|
|standby_enable           |int (u1)            |                                                            |
|output_number            |int (u4)            |P1_VADJ, P1_3P3V, P1_12P0V, P1_VIO_B_M2C, P1_VREF_A_M2C, P1_VREF_B_M2C, P2_VADJ, P2_3P3V, P2_12P0V, P2_VIO_B_M2C, P2_VREF_A_M2C, P2_VREF_B_M2C|
|nominal_voltage          |int (u16)           |                                                            |
|max_neg_voltage          |int (u16)           |                                                            |
|max_pos_voltage          |int (u16)           |                                                            |
|max_noise_pk2pk          |int (u16)           |                                                            |
|min_current_draw         |int (u16)           |                                                            |
|max_current_draw         |int (u16)           |                                                            |

## DCLoad

|Name                     |Type                |Opt                                                         
|-------------------------|--------------------|------------------------------------------------------------|
|output_number            |int (u4)            |P1_VADJ, P1_3P3V, P1_12P0V, P1_VIO_B_M2C, P1_VREF_A_M2C, P1_VREF_B_M2C, P2_VADJ, P2_3P3V, P2_12P0V, P2_VIO_B_M2C, P2_VREF_A_M2C, P2_VREF_B_M2C|
|nominal_voltage          |int (u16)           |                                                            |
|min_voltage              |int (u16)           |                                                            |
|max_voltage              |int (u16)           |                                                            |
|max_noise_pk2pk          |int (u16)           |                                                            |
|min_current_load         |int (u16)           |                                                            |
|max_current_load         |int (u16)           |                                                            |

## MgmtAccessRecord

|Name                     |Type                |Opt                                                         
|-------------------------|--------------------|------------------------------------------------------------|
|id                       |int (u8)            |sys_mgmt_url, sys_name, sys_ping_addr, comp_mgmt_url, comp_name, comp_ping_addr, sys_unique_id|
|blob                     |bytes               |                                                            |

## PicmgEntry

N/A

## FmcEntry

N/A
