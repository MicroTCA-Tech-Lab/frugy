
# picmg_multirecord records


## ModuleCurrentRequirements

|Name                     |Type                |Opt                                                         
|-------------------------|--------------------|------------------------------------------------------------|
|current_draw             |int (u8)            |                                                            |

## PointToPointConnectivity

|Name                     |Type                |Opt                                                         
|-------------------------|--------------------|------------------------------------------------------------|
|guids                    |array (GuidField)   |                                                            |
|record_type              |int (u1)            |amc_module, on_carrier_device                               |
|connected_dev_id         |int (u4)            |                                                            |
|channel_descriptors      |array (AmcChannelDescriptor)|                                                            |
|link_descriptors         |array (AmcLinkDescriptor)|                                                            |

## ClockConfig

|Name                     |Type                |Opt                                                         
|-------------------------|--------------------|------------------------------------------------------------|
|resource_type            |int (u2)            |on_carrier, amc_module, backplane                           |
|dev_id                   |int (u4)            |                                                            |
|conf_desc                |array (ClockConfigDescriptor)|                                                            |

## Zone3InterfaceCompatibility

|Name                     |Type                |Opt                                                         
|-------------------------|--------------------|------------------------------------------------------------|
|identifier_type          |int (u8)            |PICMG_IRTM0_REP, PICMG_OTHER, GUID, OEM, MTCA4_REP          |
|identifier_body          |bytes               |                                                            |

## FruPartition

|Name                     |Type                |Opt                                                         
|-------------------------|--------------------|------------------------------------------------------------|
|descriptors              |array (PartitionDescriptor)|                                                            |

## CarrierManagerIPLink

|Name                     |Type                |Opt                                                         
|-------------------------|--------------------|------------------------------------------------------------|
|shelf_manager_ip         |ipv4                |                                                            |
|carrier_manager_ip       |ipv4                |                                                            |
|mch1_ip                  |ipv4                |                                                            |
|mch2_ip                  |ipv4                |                                                            |
|subnet                   |ipv4                |                                                            |
|gateway0                 |ipv4                |                                                            |
|gateway1                 |ipv4                |                                                            |
|username                 |str                 |                                                            |
|password                 |str                 |                                                            |

## MtcaCarrierInformation

|Name                     |Type                |Opt                                                         
|-------------------------|--------------------|------------------------------------------------------------|
|number                   |int (u8)            |                                                            |
|orientation              |int (u1)            |l2r, b2t                                                    |
|slot_entries             |array (SlotEntry)   |                                                            |

## PowerPolicyRecord

|Name                     |Type                |Opt                                                         
|-------------------------|--------------------|------------------------------------------------------------|
|descriptors              |array (PowerPolicyDescriptor)|                                                            |

## MtcaCarrierActivationPm

|Name                     |Type                |Opt                                                         
|-------------------------|--------------------|------------------------------------------------------------|
|readiness_allowance      |int (u8)            |                                                            |
|descriptors              |array (MtcaCarrierActivCurrDescriptor)|                                                            |

## CarrierP2pConnectivity

|Name                     |Type                |Opt                                                         
|-------------------------|--------------------|------------------------------------------------------------|
|resource_descriptors     |array (P2pAmcResourceDescriptor)|                                                            |

## CarrierClkP2pConnectivity

|Name                     |Type                |Opt                                                         
|-------------------------|--------------------|------------------------------------------------------------|
|clk_p2p_resource_descriptors|array (ClockP2pResourceDescriptor)|                                                            |
