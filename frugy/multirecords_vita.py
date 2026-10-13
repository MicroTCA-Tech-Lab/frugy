# Copyright 2026 Kontron Europe GmbH
# SPDX-License-Identifier: BSD-3-Clause

from frugy.types import FruAreaBase, FixedField, FixedTypeLengthStringField, ArrayField, IpV4Field
from frugy.multirecords import oem_multirecord, MultirecordEntry
from frugy.fru_registry import FruRecordType, rec_register, rec_lookup_by_id


# ANSI/VITA 46.11 records: OEM multirecords (type 0xC0) with the VITA
# manufacturer ID, a VITA record ID and a record format version, like the
# PICMG records

VITA_IDENTIFIER = 0x0081ac


@oem_multirecord(0xc0, VITA_IDENTIFIER)
class VitaEntry(MultirecordEntry):
    ''' ANSI/VITA 46.11-2022, Section 10.3 '''
    ''' Superclass of all VITA 46.11 OEM multirecords '''

    def format_version(self):
        return 0x00

    def _payload_prologue(self):
        return VITA_IDENTIFIER.to_bytes(3, 'little') \
            + self._record_id.to_bytes(length=1, byteorder='little') \
            + self.format_version().to_bytes(length=1, byteorder='little')

    @classmethod
    def from_payload(cls, payload):
        # IANA prologue already validated by the OEM router; just skip it.
        payload = payload[3:]
        rec_id, rec_fmt_version, payload = payload[0], payload[1], payload[2:]

        if rec_fmt_version != 0x00:
            raise RuntimeError(
                f"Unexpected record format version: 0x{rec_fmt_version:02x}")

        try:
            cls_inst = rec_lookup_by_id(
                FruRecordType.vita_multirecord, rec_id)()
        except KeyError:
            raise RuntimeError(f"Unknown VITA 46.11 entry 0x{rec_id:02x}")

        if len(payload) == 0:
            raise EOFError(
                f"Skipping creation of {cls_inst.__class__.__name__} due to empty payload")

        cls_inst._deserialize(payload)
        return cls_inst


def vita_multirecord(rec_id):
    def register_and_set_id(cls):
        cls._record_id = rec_id
        rec_register(cls, FruRecordType.vita_multirecord, rec_id)
        return cls
    return register_and_set_id


def vita_secondary(cls):
    rec_register(cls, FruRecordType.vita_secondary)
    return cls


# Site types, ANSI/VITA 46.11-2022, Table 4.1.4.3-1; 0xC0-0xCF are OEM
_site_type_constants = {
    'front_loading_vpx_module': 0x00,
    'power_entry_module': 0x01,
    'chassis_fru_information_module': 0x02,
    'dedicated_chassis_manager': 0x03,
    'fan_tray': 0x04,
    'fan_tray_filter': 0x05,
    'alarm_panel': 0x06,
    'xmc': 0x07,
    'vpx_rtm': 0x09,
    'front_loading_vme_module': 0x0a,
    'front_loading_vxs_module': 0x0b,
    'power_supply': 0x0c,
    'front_loading_vita62_module': 0x0d,
    'vita71_module': 0x0e,
    'fmc': 0x0f,
    'unknown': 0xff,
}


@vita_secondary
class ChassisAddressTableEntry(FruAreaBase):
    ''' ANSI/VITA 46.11-2022, Table 10.3.1-2 '''

    _schema = [
        # the IPMB address is twice the hardware address
        ('hardware_address', FixedField, 'u8', {'default': 0}),
        # 0 for a front loading VPX module or an RTM: given by the hardware
        # address
        ('site_number', FixedField, 'u8', {'default': 0}),
        ('site_type', FixedField, 'u8', {
            'default': 0, 'constants': _site_type_constants}),
    ]


@vita_multirecord(0x10)
class ChassisAddressTable(VitaEntry):
    ''' ANSI/VITA 46.11-2022, Table 10.3.1-1 '''

    _schema = [
        ('chassis_identifier', FixedTypeLengthStringField, 20, {'default': ''}),
        ('_entry_count', FixedField, 'u8', {'default': 0}),
        ('entries', ArrayField, ChassisAddressTableEntry,
         {'num_elems_field': '_entry_count'}),
    ]

    def serialize(self):
        num_entries = len(self._get('entries'))
        if num_entries > 0xff:
            raise ValueError(
                f'{num_entries} chassis address table entries, at most 255 allowed')
        return super().serialize()


@vita_multirecord(0x13)
class ChassisManagerIpConnection(VitaEntry):
    ''' ANSI/VITA 46.11-2022, Table 10.3.2-1 '''

    # 0.0.0.0: not defined
    _schema = [
        ('ip_address', IpV4Field),
        ('default_gateway', IpV4Field),
        ('subnet_mask', IpV4Field),
    ]
