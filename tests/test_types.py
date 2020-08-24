#!/usr/bin/env python3

import unittest

from frugy.types import FixedField, FruArea


class TestFixedField(unittest.TestCase):
    def setUp(self):
        self.testField = FixedField('u2u2u4u16u32',
                                    (0x1, 0x2, 0x5, 0x1234, 0xdeadbeef))

    def test_size(self):
        self.assertEqual(self.testField.size(), 7, 'size mismatch')

    def test_serialize(self):
        self.assertEqual(self.testField.serialize(),
                         b'\x65\x34\x12\xef\xbe\xad\xde',
                         'serializer mismatch')

    def test_deserialize(self):
        tmp = FixedField('u16u32')
        remainder = tmp.deserialize(b'\x34\x12\x99\x88\x77\x66remainder')
        self.assertEqual(tmp.value, (0x1234, 0x66778899))
        self.assertEqual(remainder, b'remainder')


class FooArea(FruArea):
    _schema = [
        ('foo', FixedField('u4u4', value=(5, 7))),
        ('bar', FixedField('u8', value=42)),
        ('baz', FixedField('u16', value=0x1337)),
        ('foobar', FixedField('u16', value=0)),
    ]

    def __get_foobar(self):
        return self._get('foobar') ^ 0xffff

    def __set_foobar(self, value):
        self._set('foobar', value ^ 0xffff)


class TestFruArea(unittest.TestCase):
    def test_dict(self):
        foo = FooArea()
        ref = {
            'foo': [5, 7],
            'bar': 42,
            'baz': 0x1337,
            'foobar': 0
        }
        self.assertEqual(foo.__repr__(), ref.__repr__())

    def test_serialize(self):
        foo = FooArea()
        self.assertEqual(foo.size_payload(), 6)
        self.assertEqual(foo.size_total(), 8)
        self.assertEqual(foo.serialize(), b'\x57\x2a\x37\x13\x00\x00\x00\x35')


if __name__ == '__main__':
    unittest.main()
