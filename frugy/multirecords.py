###########################################################################
#      ____  _____________  __    __  __ _           _____ ___   _        #
#     / __ \/ ____/ ___/\ \/ /   |  \/  (_)__ _ _ __|_   _/ __| /_\  (R)  #
#    / / / / __/  \__ \  \  /    | |\/| | / _| '_/ _ \| || (__ / _ \      #
#   / /_/ / /___ ___/ /  / /     |_|  |_|_\__|_| \___/|_| \___/_/ \_\     #
#  /_____/_____//____/  /_/      T  E  C  H  N  O  L  O  G  Y   L A B     #
#                                                                         #
#          Copyright 2021 Deutsches Elektronen-Synchrotron DESY.          #
#                  SPDX-License-Identifier: BSD-3-Clause                  #
#                                                                         #
###########################################################################

from frugy.types import FruAreaBase, FixedField, FixedStringField, GuidField, ArrayField, BytearrayField, IpV4Field, bin2hex_helper
import bitstruct
from frugy.fru_registry import FruRecordType, rec_register, rec_lookup_by_id, rec_lookup_by_name
from frugy.areas import ipmi_area
import logging
import frugy.fru


@ipmi_area
class MultirecordArea:
    ''' Platform Management FRU Information Storage Definition, Table 16-1 '''
    ''' This is a daisy-chain of MultirecordEntry objects '''

    def __init__(self, initdict=None):
        self.records = []
        if initdict is not None:
            self.update(initdict)

    def update(self, initdict):
        self.records = []
        for v in initdict:
            try:
                constructor = rec_lookup_by_name(v['type'])
            except KeyError:
                raise RuntimeError(f"Unknown multirecord entry {v['type']}")
            self.records.append(constructor(v))

    def __repr__(self):
        return self.to_dict().__repr__()

    def to_dict(self):
        return [v.to_dict() for v in self.records]

    def serialize(self):
        result = b''
        for i, v in enumerate(self.records):
            v.end_of_list = 1 if i == len(self.records)-1 else 0
            result += v.serialize()
        return result

    def deserialize(self, input):
        self.records = []
        remainder = input
        while len(remainder):
            new_entry, remainder, end_of_list = MultirecordEntry.deserialize(
                remainder)
            if new_entry is not None:
                self.records.append(new_entry)
            if end_of_list:
                break

        return remainder

    def size_total(self):
        return sum([v.size_total() for v in self.records])


class MultirecordEntry(FruAreaBase):
    _format_version = 2
    _multirecord_header_fmt = 'u8u1u3u4u8u8'

    opalkelly_workaround_enabled = False

    def __init__(self, initdict=None):
        self.end_of_list = 0
        if initdict is not None:
            # for MultirecordEntry, type is used for type identification, not for the fields
            initdict.pop('type', None)
        super().__init__(initdict=initdict)

    def size_payload(self):
        # Add header size
        return super().size_payload() + 5 + len(self._payload_prologue())

    def _payload_prologue(self):
        # data prepended before actual payload by subclasses
        return b''

    def to_dict(self):
        # save type identification
        result = {'type': self.__class__.__name__}
        result.update(super().to_dict())
        return result

    def serialize(self):
        payload = self._payload_prologue() + super().serialize()
        payload_cksum = (-sum(payload)) & 0xff
        header = bitstruct.pack(self._multirecord_header_fmt,
                                self._type_id,
                                self.end_of_list,
                                0,
                                self._format_version,
                                len(payload),
                                payload_cksum)
        header_cksum = (-sum(header)) & 0xff
        header += header_cksum.to_bytes(length=1, byteorder='little')
        return header + payload

    @classmethod
    def deserialize(cls, input):
        header_fmt_complt = MultirecordEntry._multirecord_header_fmt + 'u8'
        header_len = bitstruct.calcsize(header_fmt_complt) // 8
        type_id, end_of_list, _, format_version, \
            payload_len, payload_cksum, _ = bitstruct.unpack(
                header_fmt_complt, input)
        header, remainder = input[:header_len], input[header_len:]
        payload, remainder = remainder[:payload_len], remainder[payload_len:]

        logging.debug(
            f"{cls.__name__}: Trying to deserialize multirecord type_id=0x{type_id:02x}, len={len(header)+len(payload)}")
        logging.debug(
            f"{cls.__name__}: header: {bin2hex_helper(header)}, payload: {bin2hex_helper(payload)}")

        try:
            if sum(header) & 0xff != 0:
                end_of_list = 1
                raise RuntimeError("MultirecordEntry header checksum invalid")

            if cls.opalkelly_workaround_enabled and len(payload) == 0:
                # Opal Kelly seems to mark the end of list with an empty payload multirecord
                end_of_list = 1
                return None, remainder, end_of_list

            if (sum(payload) + payload_cksum) & 0xff != 0:
                end_of_list = 1
                raise RuntimeError("MultirecordEntry payload checksum invalid")

            try:
                cls_id = rec_lookup_by_id(
                    FruRecordType.ipmi_multirecord, type_id)
            except KeyError:
                raise RuntimeError(f"Unknown multirecord type 0x{type_id:02x}")

            if hasattr(cls_id, 'from_payload'):
                new_entry = cls_id.from_payload(payload)
            else:
                new_entry = cls_id()
                new_entry._deserialize(payload)

            new_entry._type_id = type_id
            new_entry._format_version = format_version
            new_entry.end_of_list = end_of_list

        except RuntimeError as e:
            logging.warning(f"Failed to deserialize multirecord, type_id=0x{type_id:02x}, end_of_list={end_of_list}, "
                            f"format_version={format_version}, len={len(header)+len(payload)}")
            logging.warning(f"reason: {e}")
            logging.warning(
                f"header: {bin2hex_helper(header)}, payload: {bin2hex_helper(payload)}")
            frugy.fru.import_log(
                f'Failed to deserialize multirecord 0x{type_id:02x} ({e})')
            new_entry = None

        except ValueError as e:
            # Vendor ID mismatch: Don't issue a warning, just ignore it
            logging.debug(f"{e}")
            logging.debug(
                f"Silently ignoring private / proprietary multirecord")
            frugy.fru.import_log(
                f'Ignored private / proprietary multirecord ({e})')
            new_entry = None

        except EOFError as e:
            # Empty payload: Issue warning, but try to proceed
            logging.warning(f"{e}")
            new_entry = None

        return new_entry, remainder, end_of_list


def ipmi_multirecord(rec_id):
    def register_and_set_id(cls):
        cls._type_id = rec_id
        rec_register(cls, FruRecordType.ipmi_multirecord, rec_id)
        return cls
    return register_and_set_id
