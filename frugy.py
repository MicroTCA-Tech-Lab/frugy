#!/usr/bin/env python3

import yaml
from dataclasses import dataclass
import bitstruct
from typing import Any
from collections import OrderedDict


# fixed length FRU field
@dataclass
class FruFieldFixed():
    # format must be suitable for bitstruct module
    format: str
    value: Any = None

    def serialize(self) -> bytearray:
        if type(self.value) is tuple:
            return bitstruct.pack(self.format, *self.value)
        else:
            return bitstruct.pack(self.format, self.value)

    def deserialize(self, input: bytearray):
        numBits = bitstruct.calcsize(self.format)
        if numBits % 8 != 0:
            raise RuntimeError("Bitfield not aligned to bytes")
        n = int(numBits / 8)
        tmp, remainder = input[:n], input[n:]
        result = bitstruct.unpack(self.format, tmp)
        if len(result) > 1:
            self.value = result
        else:
            self.value = result[0]
        return remainder


class FruArea:
    _schema = OrderedDict([
        ('foo', FruFieldFixed('u4u4')),
        ('bar', FruFieldFixed('u4u4')),
        ('baz', FruFieldFixed('u8')),
    ])

    def __init__(self, initdict=None):
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
        return hasattr(self, f'_set_{key}') or key in self._schema

    def __repr__(self):
        return repr({k: self[k] for k in self._schema.keys()})

    def update(self, src):
        for k, v in src.items():
            self[k] = v

    # accessors

    def _get(self, key):
        v = self._schema[key].value
        if type(v) is tuple:
            return list(v)
        else:
            return v

    def _set(self, key, value):
        self._schema[key].value = value if type(value) is not list else tuple(value)

    def _get_baz(self):
        return self._get('baz') ^ 0xff

    def _set_baz(self, value):
        self._set('baz', value ^ 0xff)

    # (de)serializing

    def serialize(self) -> bytearray:
        return b''.join([v.serialize() for v in self._schema.values()])

    def deserialize(self, input: bytearray):
        remainder = input
        for v in self._schema.values():
            remainder = v.deserialize(remainder)


with open("test.yml", "r") as infile:
    conf = yaml.safe_load(infile)
print(conf)

test = FruArea(conf)

b = test.serialize()
print(b)

test1 = FruArea()
test1.deserialize(b)
print(test1)
