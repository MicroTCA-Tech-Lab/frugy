
# picmg_secondary records


## AmcChannelDescriptor

|Name                     |Type                |Opt                                                         
|-------------------------|--------------------|------------------------------------------------------------|

## AmcLinkDescriptor

|Name                     |Type                |Opt                                                         
|-------------------------|--------------------|------------------------------------------------------------|
|asymm_match              |int (u2)            |match_exact, match_10b, match_01b                           |
|grouping_id              |int (u8)            |                                                            |
|link_type_ext            |int (u4)            |                                                            |
|link_type                |int (u8)            |pcie, pcie_advanced, pci_advanced_1, ethernet, serial_rapidio, storage, oem_guid_0, oem_guid_1, oem_guid_2, oem_guid_3, oem_guid_4, oem_guid_5, oem_guid_6, oem_guid_7, oem_guid_8, oem_guid_9, oem_guid_10, oem_guid_11, oem_guid_12, oem_guid_13, oem_guid_14|
|channel_id               |int (u8)            |                                                            |

## DirectClockDescriptor

|Name                     |Type                |Opt                                                         
|-------------------------|--------------------|------------------------------------------------------------|
|pll_connect              |int (u1)            |                                                            |
|asymm_match              |int (u1)            |clk_source, clk_receiver                                    |
|family                   |int (u8)            |unspecified, sonet_sdh_pdh, pcie_reserved                   |
|accuracy                 |int (u8)            |                                                            |
|frequency                |int (u32)           |                                                            |
|freq_min                 |int (u32)           |                                                            |
|freq_max                 |int (u32)           |                                                            |

## IndirectClockDescriptor

|Name                     |Type                |Opt                                                         
|-------------------------|--------------------|------------------------------------------------------------|
|pll_connect              |int (u1)            |                                                            |
|asymm_match              |int (u1)            |clk_src, clk_recv                                           |
|dep_clk_id               |int (u8)            |                                                            |

## ClockConfigDescriptor

|Name                     |Type                |Opt                                                         
|-------------------------|--------------------|------------------------------------------------------------|
|clk_id                   |int (u8)            |TCLKA, TCLKB, TCLKC, TCLKD, FCLKA                           |
|activation               |int (u1)            |by_carrier, by_application                                  |
|indirect_clk_desc        |array (IndirectClockDescriptor)|                                                            |
|direct_clk_desc          |array (DirectClockDescriptor)|                                                            |

## PartitionDescriptor

|Name                     |Type                |Opt                                                         
|-------------------------|--------------------|------------------------------------------------------------|
|offset                   |int (u16)           |                                                            |
|length                   |int (u16)           |                                                            |

## SlotEntry

|Name                     |Type                |Opt                                                         
|-------------------------|--------------------|------------------------------------------------------------|
|site_no                  |int (u8)            |                                                            |
|site_type                |int (u8)            |cooling_unit, advanced_mc, rtm, mtca_carrier_hub, power_module, unknown, oem_module_0, oem_module_1, oem_module_2, oem_module_3, oem_module_4, oem_module_5, oem_module_6, oem_module_7, oem_module_8, oem_module_9, oem_module_10, oem_module_11, oem_module_12, oem_module_13, oem_module_14, oem_module_15|
|slot_no                  |int (u8)            |                                                            |
|tier_no                  |int (u8)            |                                                            |
|slot_org_y               |int (u16)           |                                                            |
|slot_org_x               |int (u16)           |                                                            |

## PowerPolicyDescriptor

|Name                     |Type                |Opt                                                         
|-------------------------|--------------------|------------------------------------------------------------|
|site_no                  |int (u8)            |                                                            |
|max_current_override     |int (u16)           |                                                            |
|pm_role                  |int (u8)            |primary, redundant, unspecified                             |

## MtcaCarrierActivCurrDescriptor

|Name                     |Type                |Opt                                                         
|-------------------------|--------------------|------------------------------------------------------------|
|site_type                |int (u8)            |cooling_unit, advanced_mc, rtm, mtca_carrier_hub, power_module, unknown, oem_module_0, oem_module_1, oem_module_2, oem_module_3, oem_module_4, oem_module_5, oem_module_6, oem_module_7, oem_module_8, oem_module_9, oem_module_10, oem_module_11, oem_module_12, oem_module_13, oem_module_14, oem_module_15|
|site_no                  |int (u8)            |                                                            |
|pwr_ch                   |int (u8)            |                                                            |
|max_current              |int (u8)            |                                                            |
|activation_ctrl          |int (u2)            |reserved, shelf_mgr, carrier_mgr, system_mgr                |
|pwr_delay                |int (u6)            |                                                            |
|deactivation_ctrl        |int (u2)            |reserved, shelf_mgr, carrier_mgr, system_mgr                |

## P2pPortDescriptor

|Name                     |Type                |Opt                                                         
|-------------------------|--------------------|------------------------------------------------------------|
|local_port               |int (u5)            |                                                            |
|remote_port              |int (u5)            |                                                            |
|resource_type            |int (u1)            |amc, carrier                                                |
|site_no                  |int (u4)            |                                                            |

## P2pAmcResourceDescriptor

|Name                     |Type                |Opt                                                         
|-------------------------|--------------------|------------------------------------------------------------|
|resource_type            |int (u1)            |amc, carrier                                                |
|site_no                  |int (u4)            |                                                            |
|port_descriptors         |array (P2pPortDescriptor)|                                                            |

## P2pClockConnectionDescriptor

|Name                     |Type                |Opt                                                         
|-------------------------|--------------------|------------------------------------------------------------|
|local_clock_id           |int (u8)            |TCLKA, TCLKB, TCLKC, TCLKD, FCLKA                           |
|remote_clock_id          |int (u8)            |TCLKA, TCLKB, TCLKC, TCLKD, FCLKA                           |
|resource_type            |int (u2)            |on_carrier, amc_module, backplane                           |
|dev_id                   |int (u4)            |                                                            |

## ClockP2pResourceDescriptor

|Name                     |Type                |Opt                                                         
|-------------------------|--------------------|------------------------------------------------------------|
|resource_type            |int (u2)            |on_carrier, amc_module, backplane                           |
|dev_id                   |int (u4)            |                                                            |
|p2p_clk_conn_descriptors |array (P2pClockConnectionDescriptor)|                                                            |
