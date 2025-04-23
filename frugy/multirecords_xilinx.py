###########################################################################
#      ____  _____________  __    __  __ _           _____ ___   _        #
#     / __ \/ ____/ ___/\ \/ /   |  \/  (_)__ _ _ __|_   _/ __| /_\  (R)  #
#    / / / / __/  \__ \  \  /    | |\/| | / _| '_/ _ \| || (__ / _ \      #
#   / /_/ / /___ ___/ /  / /     |_|  |_|_\__|_| \___/|_| \___/_/ \_\     #
#  /_____/_____//____/  /_/      T  E  C  H  N  O  L  O  G  Y   L A B     #
#                                                                         #
#          Copyright 2021 Deutsches Elektronen-Synchrotron DESY.          #
#                    2025 Advanced Micro Devices, Inc.
#                  SPDX-License-Identifier: BSD-3-Clause                  #
#                                                                         #
###########################################################################

from frugy.types import *
from frugy.multirecords import ipmi_multirecord, MultirecordEntry
from frugy.fru_registry import FruRecordType, rec_register, rec_lookup_by_id


# IPMI standard multirecords


@ipmi_multirecord(0xd2)
class OemXilinxEntry(MultirecordEntry):
    ''' Xilinx proprietary, not published '''

    _xilinx_identifier = 0x10da

    def _payload_prologue(self):
        return self._xilinx_identifier.to_bytes(3, 'little') + self._record_id.to_bytes(length=1, byteorder='little')

    @classmethod
    def from_payload(cls, payload):
        xilinx_id, payload = payload[:3], payload[3:]
        xilinx_id = int.from_bytes(xilinx_id, 'little')
        rec_id, payload = payload[0], payload[1:]


        if xilinx_id != cls._xilinx_identifier:
            raise ValueError(
                f"FMC identifier mismatch: expected 0x{cls._xilinx_identifier:06x}, received 0x{xilinx_id:06x} ({xilinx_id})")
        try:
            cls_inst = rec_lookup_by_id(
                FruRecordType.xilinx_multirecord, rec_id)()
        except KeyError:
            raise RuntimeError(f"Unknown Xilinx entry 0x{rec_id:02x}")

        cls_inst._deserialize(payload)
        cls_inst._record_id = rec_id
        return cls_inst


@ipmi_multirecord(0xd3)
class OemXilinxD3Entry(MultirecordEntry):
    ''' Xilinx proprietary, not published '''

    _xilinx_identifier = 0x10da

    def _payload_prologue(self):
        return self._xilinx_identifier.to_bytes(3, 'little')

    @classmethod
    def from_payload(cls, payload):
        xilinx_id, payload = payload[:3], payload[3:]
        rec_id = 0xd3

        try:
            cls_inst = rec_lookup_by_id(
                FruRecordType.xilinx_multirecord, rec_id)()
        except KeyError:
            raise RuntimeError(f"Unknown Xilinx entry 0x{rec_id:02x}")

        cls_inst._deserialize(payload)
        cls_inst._record_id = rec_id
        return cls_inst

def xilinx_multirecord(rec_id):
    def register_and_set_id(cls):
        cls._record_id = rec_id
        rec_register(cls, FruRecordType.xilinx_multirecord, rec_id)
        return cls
    return register_and_set_id

@xilinx_multirecord(0x31)
class dut_xilinx_mac(OemXilinxEntry):
    _schema = [
        ('mac0', MacField),
        ('mac1', MacField, None),
        ('mac2', MacField, None),
        ('mac3', MacField, None),
    ]

    def to_dict(self):
        result = super().to_dict()
        new_result = {}
        for key, value in result.items():
            if (value != ''):
                new_result[key] = value
        return new_result



@xilinx_multirecord(0x11)
class sys_ctrl_xilinx_mac(OemXilinxEntry):
    _schema = [
        ('mac0', MacField),
        ('mac1', MacField, None),
        ('mac2', MacField, None),
        ('mac3', MacField, None),
    ]

    def to_dict(self):
        result = super().to_dict()
        new_result = {}
        for key, value in result.items():
            if (value != ''):
                new_result[key] = value
        return new_result

@xilinx_multirecord(0xd3)
class xilinx_oem_d3(OemXilinxD3Entry):
    _schema = [
        ('data', FixedStringField, 80, {'default': ''}),
    ]

