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

import bitstruct
from collections import OrderedDict
from enum import Enum
from itertools import zip_longest
import uuid
from bidict import bidict
from ipaddress import IPv4Address
import logging

_format_version_default = 1
_en_decode='ISO-8859-1'

def _sizeAlign(size: int, alignment: int) -> int:
    ''' return number of padding bytes & total length after padding '''
    numPadBytes = -size % alignment
    return numPadBytes, size + numPadBytes


def _grouper(n, iterable, padvalue=None):
    "grouper(3, 'abcdefg', 'x') -> ('a','b','c'), ('d','e','f'), ('g','x','x')"
    return zip_longest(*[iter(iterable)]*n, fillvalue=padvalue)


def ser_6bit(val: str) -> bytearray:
    result = b''
    for chunk in _grouper(4, val.upper(), padvalue=' '):
        chunk = list(map(lambda x: ord(x) - 0x20, chunk))
        chunk.reverse()
        tmp = bitstruct.pack('u6'*4, *chunk)
        result += tmp[::-1]
    return result


def deser_6bit(val: bytearray) -> str:
    result = b''
    for chunk in _grouper(3, val, padvalue=' '):
        tmp = bitstruct.unpack('u6'*4, bytearray(reversed(chunk)))
        for x in tmp[::-1]:
            result += bytes((x + 0x20,))
    return result.decode(_en_decode)


def bin2hex_helper(val: bytearray):
    return ' '.join('%02x' % x for x in val)


class FixedField():
    ''' Fixed length field for numbers & bitfields '''
    _shortname = 'int'

    def __init__(self, format: str, parent=None, default=None, div=None, constants=None):
        self._format = format
        self._default = default
        self._value = default
        self._div = div
        self._constants_lookup = bidict(
            constants) if constants is not None else None

    def bit_fmt(self) -> str:
        return self._format

    def bit_size(self) -> int:
        return bitstruct.calcsize(self._format)

    def to_serialized(self):
        tmp = self._value
        if self._div is not None:
            tmp = int(tmp / self._div)
        return tmp

    def from_serialized(self, value):
        if self._div is not None:
            if self._div < 1:
                # Stupid hack that avoids rounding issues a la 7.6000000000000005
                value /= 1 / self._div
            else:
                value *= self._div
        self._value = value

    def to_dict(self):
        if self._constants_lookup is not None and self._value in self._constants_lookup.inverse:
            return self._constants_lookup.inverse[self._value]
        else:
            return self._value

    def update(self, value):
        if self._constants_lookup is not None and value in self._constants_lookup:
            self._value = self._constants_lookup[value]
        else:
            self._value = value

    def val_not_default(self):
        return self.to_dict() != self._default


class StringFmt(Enum):
    BIN = 0b00
    BCD_PLUS = 0b01
    ASCII_6BIT = 0b10
    ASCII_8BIT = 0b11


class StringField():
    ''' Variable length field for strings'''
    _shortname = 'str'

    def __init__(self, default='', format: StringFmt = StringFmt.ASCII_8BIT, parent=None):
        if default is None:
            print(f'ERROR: {parent.__class__.__name__}')
        self._format = format
        self._default = default
        self._value = default

    bcdplus_lookup = bidict({
        '0': 0, '1': 1, '2': 2, '3': 3, '4': 4, '5': 5, '6': 6, '7': 7,
        '8': 8, '9': 9, ' ': 10, '-': 11, '.': 12
    })

    def bit_size(self) -> int:
        def size_plain(val: str) -> int:
            return len(val)

        def size_6bit(val: str) -> int:
            _, n = _sizeAlign(len(val), 4)
            return (n // 4) * 3

        def size_bcd_plus(val: str) -> int:
            _, n = _sizeAlign(len(val), 2)
            return n // 2

        size_fn = {
            StringFmt.BIN: size_plain,
            StringFmt.BCD_PLUS: size_bcd_plus,
            StringFmt.ASCII_6BIT: size_6bit,
            StringFmt.ASCII_8BIT: size_plain
        }[self._format]
        return (size_fn(self._value) + 1) * 8

    def size_total(self) -> int:
        return self.bit_size() // 8

    def serialize(self) -> bytearray:
        def ser_plain(val: str) -> bytearray:
            return val.encode(_en_decode)

        def ser_bcd_plus(val: str) -> bytearray:
            result = b''
            for chunk in _grouper(2, val, padvalue=' '):
                chunk = map(lambda x: self.bcdplus_lookup[x], chunk)
                result += bitstruct.pack('u4'*2, *chunk)
            return result

        def ser_type_length(val: str) -> int:
            return bitstruct.pack('u2u6', self._format.value, len(val))

        ser_fn = {
            StringFmt.BIN: ser_plain,
            StringFmt.BCD_PLUS: ser_bcd_plus,
            StringFmt.ASCII_6BIT: ser_6bit,
            StringFmt.ASCII_8BIT: ser_plain
        }[self._format]
        result = ser_fn(self._value)
        return ser_type_length(result) + result

    def deserialize(self, input: bytearray) -> bytearray:
        def deser_plain(val: bytearray) -> str:
            return val.decode(_en_decode)

        def deser_bcd_plus(val: bytearray) -> str:
            result = ''
            for v in val:
                tmp = bitstruct.unpack('u4'*2, bytes((v,)))
                for x in tmp:
                    result += self.bcdplus_lookup.inverse[x]
            return result

        fmt_int, payload_len = bitstruct.unpack('u2u6', input[0:1])
        self._format = StringFmt(fmt_int)
        logging.debug(
            f'{self.__class__.__name__}: string format: {self._format.name}, length: {payload_len}')
        remainder = input[1:]
        payload, remainder = remainder[:payload_len], remainder[payload_len:]

        deser_fn = {
            StringFmt.BIN: deser_plain,
            StringFmt.BCD_PLUS: deser_bcd_plus,
            StringFmt.ASCII_6BIT: deser_6bit,
            StringFmt.ASCII_8BIT: deser_plain
        }[self._format]
        self._value = deser_fn(payload)

        logging.debug(
            f'{self.__class__.__name__}: val: {self._value}, remainder: {bin2hex_helper(remainder[:10])}...')
        return remainder

    def to_dict(self):
        return self._value

    def update(self, value):
        self._value = value

    def val_not_default(self):
        return self.to_dict() != self._default


class BytearrayField():
    ''' Variable length field containing a transparent bytearray, to handle stupid ambiguous multirecord payloads '''
    ''' (e.g. "Zone 3 Interface Compatibility record") '''
    _shortname = 'bytes'

    def __init__(self, default='', num_elems_field=None, hex=True, parent=None):
        self._parent = parent
        self._num_elems_field = num_elems_field
        self._default = default
        self._value = default
        self._hex = hex

    def bit_size(self) -> int:
        return len(self._value) * 8

    def pre_serialize(self):
        ''' Set number of elements in parent record, _before_ serializing it '''
        if self._num_elems_field:
            self._parent._set(self._num_elems_field, len(self._value))

    def serialize(self) -> bytearray:
        return self._value

    def deserialize(self, input: bytearray) -> bytearray:
        if self._num_elems_field:
            num_elems = self._parent._get(self._num_elems_field)
            self._value = input[:num_elems]
            return input[num_elems:]
        else:
            self._value = input
            return b''

    def to_dict(self):
        return bin2hex_helper(self._value) if self._hex else self._value.decode(_en_decode)

    def update(self, value):
        self._value = bytearray.fromhex(
            value) if self._hex else value.encode(_en_decode)

    def val_not_default(self):
        return self.to_dict() != self._default


class FixedStringField():
    ''' Null-terminated string with fixed size buffer '''
    _shortname = 'str'

    _null_term = b'\x00'

    def __init__(self, bufsize, default='', parent=None):
        self._bufsize = bufsize
        self._default = default
        self._value = default

    def bit_size(self) -> int:
        return self._bufsize * 8

    def serialize(self) -> bytearray:
        return self._value[:self._bufsize-1].encode(_en_decode) + self._null_term

    def deserialize(self, input: bytearray) -> bytearray:
        tmp, remainder = input[:self._bufsize], input[self._bufsize:]
        if self._null_term in tmp:
            pos = tmp.index(self._null_term)
            tmp = tmp[:pos]
        self._value = tmp.decode(_en_decode)
        return remainder

    def to_dict(self):
        return self._value

    def update(self, value):
        self._value = value

    def val_not_default(self):
        return self.to_dict() != self._default


class CustomStringArray:
    ''' Platform Management FRU Information Storage Definition, Table 10-1, 11-1, 12-1 '''
    ''' This is a daisy-chain of StringField objects, delimited with 0xc1 '''
    _shortname = 'strarray'

    _delimiter = b'\xc1'

    def __init__(self, initdict=None, parent=None):
        self.strings = []
        if initdict is not None:
            self.update(initdict)

    def update(self, initdict):
        self.strings = [StringField(v, format = StringFmt.BIN) for v in initdict]

    def __repr__(self):
        return self.to_dict().__repr__()

    def to_dict(self):
        return [v.to_dict() for v in self.strings]

    def serialize(self):
        result = b''
        for v in self.strings:
            result += v.serialize()
        return result + self._delimiter

    def deserialize(self, input):
        self.strings = []
        remainder = input
        while len(remainder):
            if remainder[0:1] == self._delimiter:
                remainder = remainder[1:]
                break
            tmp = StringField(format = StringFmt.BIN)
            remainder = tmp.deserialize(remainder)
            self.strings.append(tmp)

        logging.debug(
            f'{self.__class__.__name__}: parsed {len(self.strings)} strings')
        return remainder

    def size_total(self):
        # add one for the delimiter
        return sum([v.size_total() for v in self.strings]) + 1

    def bit_size(self) -> int:
        return self.size_total() * 8

    def val_not_default(self):
        return len(self.strings) != 0


class IpV4Field():
    ''' Field containing a IPv4 address '''
    _shortname = 'ipv4'

    _num_bytes = 4

    def __init__(self, default='0.0.0.0', parent=None):
        self._default = default
        self._value = IPv4Address(default)

    def bit_size(self) -> int:
        return self._num_bytes * 8

    def serialize(self) -> bytearray:
        return int(self._value).to_bytes(self._num_bytes, 'big')

    def deserialize(self, input: bytearray) -> bytearray:
        tmp, remainder = input[:self._num_bytes], input[self._num_bytes:]
        tmp = int.from_bytes(tmp, 'big')
        self._value = IPv4Address(tmp)
        return remainder

    def to_dict(self):
        return str(self._value)

    def update(self, value):
        self._value = IPv4Address(value)

    def val_not_default(self):
        return self.to_dict() != self._default


class GuidField():
    ''' Field containing a 128-bit GUID '''
    _shortname = 'guid'

    _uuid_len = 16

    def __init__(self, value=None, parent=None):
        self._value = uuid.UUID(value) if value is not None else uuid.uuid4()

    def bit_size(self) -> int:
        return GuidField._uuid_len * 8

    def size_total(self) -> int:
        return GuidField._uuid_len

    def serialize(self) -> bytearray:
        return self._value.bytes_le

    def deserialize(self, input: bytearray) -> bytearray:
        payload, remainder = input[:GuidField._uuid_len], input[GuidField._uuid_len:]
        self._value = uuid.UUID(bytes_le=payload)
        return remainder

    def to_dict(self):
        return str(self._value)

    def update(self, value):
        self._value = uuid.UUID(value)


class ArrayField():
    ''' Field containing an array of instances of another record '''
    _shortname = 'array'

    def __init__(self, cls, parent=None, initdict=None, num_elems_field=None):
        self._parent = parent
        self._cls = cls
        self._records = []
        self._num_elems_field = num_elems_field
        if initdict is not None:
            self.update(initdict)

    def update(self, initdict):
        self._records = []
        for v in initdict:
            self._records.append(self._cls(v))

    def __repr__(self):
        return self.to_dict().__repr__()

    def to_dict(self):
        return [v.to_dict() for v in self._records]

    def pre_serialize(self):
        ''' Set number of elements in parent record, _before_ serializing it '''
        if self._num_elems_field:
            self._parent._set(self._num_elems_field, self.num_elems())

    def serialize(self):
        result = b''
        for f in self._records:
            result += f.serialize()
        return result

    def deserialize(self, input):
        self._records = []
        remainder = input
        num_elems = None
        if self._num_elems_field:
            num_elems = self._parent._get(self._num_elems_field)

        while len(remainder) and num_elems != 0:
            record = self._cls()
            remainder = record.deserialize(remainder)
            self._records.append(record)
            if num_elems is not None:
                num_elems -= 1

        return remainder

    def bit_size(self):
        return self.size_total() * 8

    def size_total(self):
        return sum([v.size_total() for v in self._records])

    def num_elems(self):
        return len(self._records)

    def val_not_default(self):
        return self.num_elems() != 0


class FruAreaBase:
    ''' Common base class for FRU areas '''

    _mergeBitfield = False

    def __init__(self, initdict=None):
        self._dict = OrderedDict()
        for v in self._schema:
            kwargs = v[3] if len(v) > 3 else {}
            obj = v[1]
            if len(v) > 2:
                obj = obj(v[2], parent=self, **kwargs)
            else:
                obj = obj(parent=self, **kwargs)
            self._dict[v[0]] = obj

        if initdict is not None:
            self.update(initdict)

    # dict interface

    def __getitem__(self, key):
        # check for special accessor
        fname = f'_get_{key}'
        if hasattr(self, fname):
            return getattr(self, fname)()
        else:
            # use generic accessor
            return self._get(key)

    def __setitem__(self, key, value):
        # check for special accessor
        fname = f'_set_{key}'
        if hasattr(self, fname):
            getattr(self, fname)(value)
        else:
            # use generic accessor
            self._set(key, value)

    def __contains__(self, key):
        return hasattr(self, f'_set_{key}') or key in self._dict

    def __repr__(self):
        return repr(self.to_dict())

    def update(self, src):
        for k, v in src.items():
            self[k] = v

    def to_dict(self):
        # Fields starting with _ are ignored by convention (reserved values).
        return {
            k: self[k] for k in self._dict.keys()
            if not k.startswith('_') and self._dict[k].val_not_default()
        }

    # accessors

    def _get(self, key):
        return self._dict[key].to_dict()

    def _set(self, key, value):
        self._dict[key].update(value)

    # Fixed point integer helpers

    def _set_div(self, key, value, div):
        self._set(key, int(value / div))

    def _get_div(self, key, div):
        return float(self._get(key)) * div

    # (de)serializing

    def size_payload(self) -> int:
        return sum([v.bit_size() for v in self._dict.values()]) // 8

    def size_total(self) -> int:
        return self.size_payload()

    def _serialize(self) -> bytearray:
        for v in self._dict.values():
            if hasattr(v, 'pre_serialize'):
                v.pre_serialize()

        result = b''
        bit_fmt = ''
        bit_values = []

        def serialize_bitfield():
            nonlocal bit_fmt, bit_values
            if bit_fmt == '':
                return b''
            if not self._mergeBitfield:
                bits = bitstruct.pack(bit_fmt + '<', *bit_values)
            else:
                bits = bitstruct.pack(bit_fmt, *bit_values)[::-1]
            bit_fmt = ''
            bit_values = []
            return bits

        for v in self._dict.values():
            if hasattr(v, 'bit_fmt'):
                bit_fmt += v.bit_fmt()
                bit_values.append(v.to_serialized())
            else:
                # before any other type is serialized, serialize bitfield first
                result += serialize_bitfield()
                result += v.serialize()
        # finish serializing bitfield, if anything is left
        result += serialize_bitfield()
        return result

    def serialize(self) -> bytearray:
        return self._serialize()

    def _deserialize(self, input: bytearray):
        remainder = input
        bit_fmt = ''
        bit_fields = []

        def deserialize_bitfield():
            nonlocal bit_fmt, bit_fields, remainder
            if bit_fmt == '':
                return
            bit_length = bitstruct.calcsize(bit_fmt) // 8
            bit_data, remainder = remainder[:bit_length], remainder[bit_length:]
            logging.debug(
                f'{self.__class__.__name__}: parse {bit_fmt} from {bin2hex_helper(bit_data)}')
            if not self._mergeBitfield:
                values = bitstruct.unpack(bit_fmt + '<', bit_data)
            else:
                values = bitstruct.unpack(bit_fmt, bit_data[::-1])
            for f, v in zip(bit_fields, values):
                f.from_serialized(v)
            bit_fmt = ''
            bit_fields = []

        for k, v in self._dict.items():
            logging.debug(f'{self.__class__.__name__}: parsing {k}')
            if hasattr(v, 'bit_fmt'):
                bit_fmt += v.bit_fmt()
                bit_fields.append(v)
            else:
                # before any other type is deserialized, deserialize bitfield first
                deserialize_bitfield()
                logging.debug(
                    f'{self.__class__.__name__}: parse {v} {bin2hex_helper(remainder[:10])}...')
                remainder = v.deserialize(remainder)
        # finish deserializing bitfield, if anything is left
        deserialize_bitfield()
        return remainder

    def deserialize(self, input: bytearray):
        return self._deserialize(input)


class FruAreaChecksummed(FruAreaBase):
    ''' FRU area featuring a checksum in the epilogue '''

    ignore_checksum_errors = False

    def _prologue(self) -> bytearray:
        return b''

    def _epilogue(self, payload: bytearray) -> bytearray:
        ''' return data to append (checksum and padding to 64 bit alignment) '''
        numPadBytes, _ = _sizeAlign(len(payload) + 1, 8)
        result = b'\x00' * numPadBytes
        cksum = (-sum(payload)) & 0xff
        result += cksum.to_bytes(length=1, byteorder='little')
        return result

    def size_total(self) -> int:
        # add one byte for checksum
        _, n = _sizeAlign(self.size_payload() + 1, 8)
        return n

    def serialize(self) -> bytearray:
        payload = self._prologue()
        payload += self._serialize()
        return payload + self._epilogue(payload)

    def _verify_epilogue(self, input: bytearray, offs: int) -> bytearray:
        payload = input[:offs]
        ep = self._epilogue(payload)
        vfy, remainder = input[offs:offs+len(ep)], input[offs+len(ep):]
        if ep != vfy and not self.ignore_checksum_errors:
            raise RuntimeError(
                f'padding or checksum verify error in {self.__class__.__name__}: expected {bin2hex_helper(ep)}, received {bin2hex_helper(vfy)}')
        return remainder

    def deserialize(self, input: bytearray):
        remainder = self._deserialize(input)
        return self._verify_epilogue(input, len(input) - len(remainder))


class FruAreaVersioned(FruAreaChecksummed):
    ''' FRU area featuring a version field '''

    def __init__(self, initdict=None):
        self._format_version = _format_version_default
        super().__init__(initdict=initdict)

    def _set_format_version(self, val):
        self._format_version = val

    def _get_format_version(self):
        return self._format_version

    def _prologue(self) -> bytearray:
        ''' return data to prepend (format version) '''
        return super()._prologue() + self._format_version.to_bytes(1, 'little')

    def size_payload(self) -> int:
        # add one byte for format version
        return super().size_payload() + 1

    def deserialize(self, input: bytearray):
        self._format_version = input[0]
        remainder = self._deserialize(input[1:])
        return self._verify_epilogue(input, len(input) - len(remainder))


class FruAreaSized(FruAreaVersioned):
    ''' FRU area featuring version and length fields '''

    def _set_area_length(self, val):
        if (val % 8) != 0:
            raise ValueError(f'area length {val} not 64-bit aligned')
        self._area_length = val // 8

    def _get_area_length(self):
        return self._area_length * 8

    def size_payload(self) -> int:
        # add one byte for size field
        return super().size_payload() + 1

    def _prologue(self) -> bytearray:
        ''' return data to prepend (size field) '''
        self._set_area_length(self.size_total())
        return super()._prologue() + self._area_length.to_bytes(1, 'little')

    def deserialize(self, input: bytearray):
        self._format_version = input[0]
        self._area_length = input[1]
        area_len = self._get_area_length()
        logging.debug(
            f'{self.__class__.__name__}: parse {bin2hex_helper(input[:10])}...')
        self._deserialize(input[2:area_len])
        # The remainder may have arbitrary padding, so just check the last byte, and return only stuff that's behind our area
        cksum = (-sum(input[:area_len])) & 0xff
        if cksum != 0 and not self.ignore_checksum_errors:
            raise RuntimeError(
                f'{self.__class__.__name__}: checksum doesn\'t add up to zero')
        return input[area_len:]
