
# VITA records


## ChassisAddressTable
ANSI/VITA 46.11-2022, Table 10.3.1-1

|Name                                    |Type                |Opt                           
|----------------------------------------|--------------------|------------------------------|
|`chassis_identifier`                    |str (20)            |                              |
|`entries`                               |array (ChassisAddressTableEntry)|                              |

<br>


## ChassisManagerIpConnection
ANSI/VITA 46.11-2022, Table 10.3.2-1

|Name                                    |Type                |Opt                           
|----------------------------------------|--------------------|------------------------------|
|`ip_address`                            |ipv4                |                              |
|`default_gateway`                       |ipv4                |                              |
|`subnet_mask`                           |ipv4                |                              |

<br>


## ChassisAddressTableEntry
ANSI/VITA 46.11-2022, Table 10.3.1-2

|Name                                    |Type                |Opt                           
|----------------------------------------|--------------------|------------------------------|
|`hardware_address`                      |int (u8)            |                              |
|`site_number`                           |int (u8)            |                              |
|`site_type`                             |int (u8)            |`front_loading_vpx_module`, `power_entry_module`, `chassis_fru_information_module`, `dedicated_chassis_manager`, `fan_tray`, `fan_tray_filter`, `alarm_panel`, `xmc`, `vpx_rtm`, `front_loading_vme_module`, `front_loading_vxs_module`, `power_supply`, `front_loading_vita62_module`, `vita71_module`, `fmc`, `unknown`|

<br>

