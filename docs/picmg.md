
# PICMG records


## ModuleCurrentRequirements
PICMG AMC.0 Specification R2.0, Table 3-10

|Name                     |Type                |Opt                                                         
|-------------------------|--------------------|------------------------------------------------------------|
|`current_draw`           |int (u8)            |                                                            |

## PointToPointConnectivity
PICMG AMC.0 Specification R2.0, Table 3-16

|Name                     |Type                |Opt                                                         
|-------------------------|--------------------|------------------------------------------------------------|
|`guids`                  |array (GuidField)   |                                                            |
|`record_type`            |int (u1)            |amc_module, on_carrier_device                               |
|`connected_dev_id`       |int (u4)            |                                                            |
|`channel_descriptors`    |array (AmcChannelDescriptor)|                                                            |
|`link_descriptors`       |array (AmcLinkDescriptor)|                                                            |

## ClockConfig
PICMG AMC.0 Specification R2.0, Table 3-35

|Name                     |Type                |Opt                                                         
|-------------------------|--------------------|------------------------------------------------------------|
|`resource_type`          |int (u2)            |on_carrier, amc_module, backplane                           |
|`dev_id`                 |int (u4)            |                                                            |
|`conf_desc`              |array (ClockConfigDescriptor)|                                                            |

## Zone3InterfaceCompatibility
PICMG MicroTCA.4 Enhancements for Rear I/O and Timing R1.0, Table 3-3

|Name                     |Type                |Opt                                                         
|-------------------------|--------------------|------------------------------------------------------------|
|`identifier_type`        |int (u8)            |PICMG_IRTM0_REP, PICMG_OTHER, GUID, OEM, MTCA4_REP          |
|`identifier_body`        |bytes               |                                                            |

## FruPartition
PICMG Specification MTCA.0 R1.0, Table 3-10

|Name                     |Type                |Opt                                                         
|-------------------------|--------------------|------------------------------------------------------------|
|`descriptors`            |array (PartitionDescriptor)|                                                            |

## CarrierManagerIPLink
PICMG Specification MTCA.0 R1.0, Table 3-12

|Name                     |Type                |Opt                                                         
|-------------------------|--------------------|------------------------------------------------------------|
|`shelf_manager_ip`       |ipv4                |                                                            |
|`carrier_manager_ip`     |ipv4                |                                                            |
|`mch1_ip`                |ipv4                |                                                            |
|`mch2_ip`                |ipv4                |                                                            |
|`subnet`                 |ipv4                |                                                            |
|`gateway0`               |ipv4                |                                                            |
|`gateway1`               |ipv4                |                                                            |
|`username`               |str                 |                                                            |
|`password`               |str                 |                                                            |

## MtcaCarrierInformation
PICMG Specification MTCA.0 R1.0, Table 3-16

|Name                     |Type                |Opt                                                         
|-------------------------|--------------------|------------------------------------------------------------|
|`number`                 |int (u8)            |                                                            |
|`orientation`            |int (u1)            |l2r, b2t                                                    |
|`slot_entries`           |array (SlotEntry)   |                                                            |

## PowerPolicyRecord
PICMG Specification MTCA.0 R1.0, Table 3-23

|Name                     |Type                |Opt                                                         
|-------------------------|--------------------|------------------------------------------------------------|
|`descriptors`            |array (PowerPolicyDescriptor)|                                                            |

## MtcaCarrierActivationPm
PICMG Specification MTCA.0 R1.0, Table 3-25

|Name                     |Type                |Opt                                                         
|-------------------------|--------------------|------------------------------------------------------------|
|`readiness_allowance`    |int (u8)            |                                                            |
|`descriptors`            |array (MtcaCarrierActivCurrDescriptor)|                                                            |

## CarrierP2pConnectivity
PICMG AMC.0 Specification R2.0, Table 3-13

|Name                     |Type                |Opt                                                         
|-------------------------|--------------------|------------------------------------------------------------|
|`resource_descriptors`   |array (P2pAmcResourceDescriptor)|                                                            |

## CarrierClkP2pConnectivity
PICMG AMC.0 Specification R2.0, Table 3-29

|Name                     |Type                |Opt                                                         
|-------------------------|--------------------|------------------------------------------------------------|
|`clk_p2p_resource_descriptors`|array (ClockP2pResourceDescriptor)|                                                            |

## Zone3InterfaceDocumentation
PICMG MicroTCA.4 Enhancements for Rear I/O and Timing R1.0, Table 3-15

|Name                     |Type                |Opt                                                         
|-------------------------|--------------------|------------------------------------------------------------|
|`url`                    |bytes               |                                                            |

## AmcChannelDescriptor
PICMG AMC.0 Specification R2.0, Table 3-17

|Name                     |Type                |Opt                                                         
|-------------------------|--------------------|------------------------------------------------------------|

## AmcLinkDescriptor
PICMG AMC.0 Specification R2.0, Table 3-19

|Name                     |Type                |Opt                                                         
|-------------------------|--------------------|------------------------------------------------------------|
|`asymm_match`            |int (u2)            |match_exact, match_10b, match_01b                           |
|`grouping_id`            |int (u8)            |                                                            |
|`link_type_ext`          |int (u4)            |                                                            |
|`link_type`              |int (u8)            |pcie, pcie_advanced, pci_advanced_1, ethernet, serial_rapidio, storage, oem_guid_0, oem_guid_1, oem_guid_2, oem_guid_3, oem_guid_4, oem_guid_5, oem_guid_6, oem_guid_7, oem_guid_8, oem_guid_9, oem_guid_10, oem_guid_11, oem_guid_12, oem_guid_13, oem_guid_14|
|`channel_id`             |int (u8)            |                                                            |

## DirectClockDescriptor
PICMG AMC.0 Specification R2.0, Table 3-38

|Name                     |Type                |Opt                                                         
|-------------------------|--------------------|------------------------------------------------------------|
|`pll_connect`            |int (u1)            |                                                            |
|`asymm_match`            |int (u1)            |clk_source, clk_receiver                                    |
|`family`                 |int (u8)            |unspecified, sonet_sdh_pdh, pcie_reserved                   |
|`accuracy`               |int (u8)            |                                                            |
|`frequency`              |int (u32)           |                                                            |
|`freq_min`               |int (u32)           |                                                            |
|`freq_max`               |int (u32)           |                                                            |

## IndirectClockDescriptor
PICMG AMC.0 Specification R2.0, Table 3-37

|Name                     |Type                |Opt                                                         
|-------------------------|--------------------|------------------------------------------------------------|
|`pll_connect`            |int (u1)            |                                                            |
|`asymm_match`            |int (u1)            |clk_src, clk_recv                                           |
|`dep_clk_id`             |int (u8)            |                                                            |

## ClockConfigDescriptor
PICMG AMC.0 Specification R2.0, Table 3-36

|Name                     |Type                |Opt                                                         
|-------------------------|--------------------|------------------------------------------------------------|
|`clk_id`                 |int (u8)            |TCLKA, TCLKB, TCLKC, TCLKD, FCLKA                           |
|`activation`             |int (u1)            |by_carrier, by_application                                  |
|`indirect_clk_desc`      |array (IndirectClockDescriptor)|                                                            |
|`direct_clk_desc`        |array (DirectClockDescriptor)|                                                            |

## PartitionDescriptor
PICMG Specification MTCA.0 R1.0, Table 3-11

|Name                     |Type                |Opt                                                         
|-------------------------|--------------------|------------------------------------------------------------|
|`offset`                 |int (u16)           |                                                            |
|`length`                 |int (u16)           |                                                            |

## SlotEntry
PICMG Specification MTCA.0 R1.0, Table 3-17

|Name                     |Type                |Opt                                                         
|-------------------------|--------------------|------------------------------------------------------------|
|`site_no`                |int (u8)            |                                                            |
|`site_type`              |int (u8)            |cooling_unit, advanced_mc, rtm, mtca_carrier_hub, power_module, unknown, oem_module_0, oem_module_1, oem_module_2, oem_module_3, oem_module_4, oem_module_5, oem_module_6, oem_module_7, oem_module_8, oem_module_9, oem_module_10, oem_module_11, oem_module_12, oem_module_13, oem_module_14, oem_module_15|
|`slot_no`                |int (u8)            |                                                            |
|`tier_no`                |int (u8)            |                                                            |
|`slot_org_y`             |int (u16)           |                                                            |
|`slot_org_x`             |int (u16)           |                                                            |

## PowerPolicyDescriptor
PICMG Specification MTCA.0 R1.0, Table 3-24

|Name                     |Type                |Opt                                                         
|-------------------------|--------------------|------------------------------------------------------------|
|`site_no`                |int (u8)            |                                                            |
|`max_current_override`   |int (u16)           |                                                            |
|`pm_role`                |int (u8)            |primary, redundant, unspecified                             |

## MtcaCarrierActivCurrDescriptor
PICMG Specification MTCA.0 R1.0, Table 3-26

|Name                     |Type                |Opt                                                         
|-------------------------|--------------------|------------------------------------------------------------|
|`site_type`              |int (u8)            |cooling_unit, advanced_mc, rtm, mtca_carrier_hub, power_module, unknown, oem_module_0, oem_module_1, oem_module_2, oem_module_3, oem_module_4, oem_module_5, oem_module_6, oem_module_7, oem_module_8, oem_module_9, oem_module_10, oem_module_11, oem_module_12, oem_module_13, oem_module_14, oem_module_15|
|`site_no`                |int (u8)            |                                                            |
|`pwr_ch`                 |int (u8)            |                                                            |
|`max_current`            |int (u8)            |                                                            |
|`activation_ctrl`        |int (u2)            |reserved, shelf_mgr, carrier_mgr, system_mgr                |
|`pwr_delay`              |int (u6)            |                                                            |
|`deactivation_ctrl`      |int (u2)            |reserved, shelf_mgr, carrier_mgr, system_mgr                |

## P2pPortDescriptor
PICMG AMC.0 Specification R2.0, Table 3-15

|Name                     |Type                |Opt                                                         
|-------------------------|--------------------|------------------------------------------------------------|
|`local_port`             |int (u5)            |                                                            |
|`remote_port`            |int (u5)            |                                                            |
|`resource_type`          |int (u1)            |amc, carrier                                                |
|`site_no`                |int (u4)            |                                                            |

## P2pAmcResourceDescriptor
PICMG AMC.0 Specification R2.0, Table 3-14

|Name                     |Type                |Opt                                                         
|-------------------------|--------------------|------------------------------------------------------------|
|`resource_type`          |int (u1)            |amc, carrier                                                |
|`site_no`                |int (u4)            |                                                            |
|`port_descriptors`       |array (P2pPortDescriptor)|                                                            |

## P2pClockConnectionDescriptor
PICMG AMC.0 Specification R2.0, Table 3-32

|Name                     |Type                |Opt                                                         
|-------------------------|--------------------|------------------------------------------------------------|
|`local_clock_id`         |int (u8)            |TCLKA, TCLKB, TCLKC, TCLKD, FCLKA                           |
|`remote_clock_id`        |int (u8)            |TCLKA, TCLKB, TCLKC, TCLKD, FCLKA                           |
|`resource_type`          |int (u2)            |on_carrier, amc_module, backplane                           |
|`dev_id`                 |int (u4)            |                                                            |

## ClockP2pResourceDescriptor
PICMG AMC.0 Specification R2.0, Table 3-30

|Name                     |Type                |Opt                                                         
|-------------------------|--------------------|------------------------------------------------------------|
|`resource_type`          |int (u2)            |on_carrier, amc_module, backplane                           |
|`dev_id`                 |int (u4)            |                                                            |
|`p2p_clk_conn_descriptors`|array (P2pClockConnectionDescriptor)|                                                            |
