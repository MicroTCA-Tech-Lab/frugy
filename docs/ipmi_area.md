
# ipmi_area records


## CommonHeader

|Name                     |Type                |Opt                                                         
|-------------------------|--------------------|------------------------------------------------------------|
|internal_use_offs        |int (u8)            |                                                            |
|chassis_info_offs        |int (u8)            |                                                            |
|board_info_offs          |int (u8)            |                                                            |
|product_info_offs        |int (u8)            |                                                            |
|multirecord_offs         |int (u8)            |                                                            |

## ChassisInfo

|Name                     |Type                |Opt                                                         
|-------------------------|--------------------|------------------------------------------------------------|
|type                     |int (u8)            |                                                            |
|part_number              |str                 |                                                            |
|serial_number            |str                 |                                                            |
|custom_info_fields       |strarray            |                                                            |

## BoardInfo

|Name                     |Type                |Opt                                                         
|-------------------------|--------------------|------------------------------------------------------------|
|language_code            |int (u8)            |                                                            |
|mfg_date_time            |int (u24)           |                                                            |
|manufacturer             |str                 |                                                            |
|product_name             |str                 |                                                            |
|serial_number            |str                 |                                                            |
|part_number              |str                 |                                                            |
|fru_file_id              |str                 |                                                            |
|custom_info_fields       |strarray            |                                                            |

## ProductInfo

|Name                     |Type                |Opt                                                         
|-------------------------|--------------------|------------------------------------------------------------|
|language_code            |int (u8)            |                                                            |
|manufacturer             |str                 |                                                            |
|product_name             |str                 |                                                            |
|part_number              |str                 |                                                            |
|version                  |str                 |                                                            |
|serial_number            |str                 |                                                            |
|asset_tag                |str                 |                                                            |
|fru_file_id              |str                 |                                                            |
|custom_info_fields       |strarray            |                                                            |

## MultirecordArea

N/A
