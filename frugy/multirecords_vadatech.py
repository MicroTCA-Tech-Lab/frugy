# Copyright 2026 Atom Computing, Inc.
# SPDX-License-Identifier: BSD-3-Clause

from frugy.types import BytearrayField
from frugy.multirecords import oem_multirecord, MultirecordEntry


# VadaTech OEM multirecords
#
# IANA Enterprise Number 23858 (0x005d32) is registered to VadaTech, Inc.
# Their proprietary multirecord layouts are not published, so we cannot
# decode the payload into structured fields. Instead we round-trip it as
# an opaque hex blob so that FRU images containing VadaTech records can be
# parsed, edited and re-emitted without losing the vendor data.

VADATECH_IDENTIFIER = 0x005d32


class _OemVadatechBase(MultirecordEntry):
    ''' Base class for opaque VadaTech OEM multirecords (hex blob). '''

    _schema = [
        ('data', BytearrayField, None, {'hex': True}),
    ]

    def _payload_prologue(self):
        return VADATECH_IDENTIFIER.to_bytes(3, 'little')

    @classmethod
    def from_payload(cls, payload):
        # IANA prologue already validated by the OEM router; just skip it.
        payload = payload[3:]
        cls_inst = cls()
        cls_inst._deserialize(payload)
        return cls_inst


@oem_multirecord(0xc0, VADATECH_IDENTIFIER)
class OemVadatechC0Entry(_OemVadatechBase):
    ''' VadaTech proprietary OEM multirecord (type 0xC0), opaque hex payload '''
    pass
