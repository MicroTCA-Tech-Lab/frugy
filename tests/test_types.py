"""
SPDX-License-Identifier: BSD-3-Clause
Copyright (c) 2020 Deutsches Elektronen-Synchrotron DESY.
See LICENSE.txt for license details.
"""

import unittest

from frugy.types import FixedField, StringField, StringFmt, GuidField, ArrayField, FruAreaBase


class TestString(unittest.TestCase):
    def test_null(self):
        nul = StringField()
        ser = nul.serialize()
        self.assertEqual(ser, b'\xc0')
        ser += b'remainder'
        tmp = StringField()
        self.assertEqual(tmp.deserialize(ser), b'remainder')
        self.assertEqual(tmp.to_dict(), '')

    def test_plain(self):
        testStr = 'Hello world'
        tmp = StringField(testStr, format=StringFmt.ASCII_8BIT)
        self.assertEqual(tmp.bit_size(), 12 * 8)
        ser = tmp.serialize()
        self.assertEqual(ser, b'\xcbHello world')
        ser += b'remainder'
        tmp2 = StringField()
        self.assertEqual(tmp2.deserialize(ser), b'remainder')
        self.assertEqual(tmp2.to_dict(), testStr)

    def test_bcd_plus(self):
        testStr = '123.45-67 890'
        tmp = StringField(testStr, format=StringFmt.BCD_PLUS)
        self.assertEqual(tmp.bit_size(), 8 * 8)
        ser = tmp.serialize()
        self.assertEqual(ser, b'\x47\x12\x3c\x45\xb6\x7a\x89\x0a')
        ser += b'remainder'
        tmp2 = StringField()
        self.assertEqual(tmp2.deserialize(ser), b'remainder')
        self.assertEqual(tmp2.to_dict(), testStr + ' ')  # append padding space

    def test_ascii_6bit(self):
        testStr = 'IPMI Hello world'
        tmp = StringField(testStr, format=StringFmt.ASCII_6BIT)
        self.assertEqual(tmp.bit_size(), 13 * 8)
        ser = tmp.serialize()
        self.assertEqual(ser,
                         b'\x8c\x29\xdc\xa6\x00Z\xb2\xec\x0b\xdc\xaf\xcc\x92')
        ser += b'remainder'
        tmp2 = StringField()
        self.assertEqual(tmp2.deserialize(ser), b'remainder')
        self.assertEqual(tmp2.to_dict(), 'IPMI HELLO WORLD')


class ArrayTest(FruAreaBase):
    _schema = [
        ('first_byte', FixedField, 'u8', {'default': 0}),
        ('second_byte', FixedField, 'u8', {'default': 0}),
        ('bits1', FixedField, 'u4', {'default': 0}),
        ('bits2', FixedField, 'u4', {'default': 0}),
    ]

class TestMisc(unittest.TestCase):
    def test_uuid(self):
        testUid = 'cafebabe-1234-5678-d00f-deadbeef4711'
        tmp = GuidField(testUid)
        self.assertEqual(tmp.bit_size(), 128)
        ser = tmp.serialize()
        self.assertEqual(ser, b'\xbe\xba\xfe\xca4\x12xV\xd0\x0f\xde\xad\xbe\xefG\x11')
        ser += b'remainder'
        tmp2 = GuidField()
        self.assertEqual(tmp2.deserialize(ser), b'remainder')
        self.assertEqual(tmp2.to_dict(), testUid)

    def test_array(self):
        tmp = ArrayField(ArrayTest, initdict=[
            { 'first_byte': 1, 'second_byte': 2, 'bits1': 3, 'bits2': 4, },
            { 'first_byte': 5, 'second_byte': 6, 'bits1': 7, 'bits2': 8, },
            { 'first_byte': 9, 'second_byte': 10, 'bits1': 11, 'bits2': 12, },
        ])
        self.assertEqual(tmp.size_total(), 3 * 3)
        ser = tmp.serialize()
        self.assertEqual(ser, b'\x01\x024\x05\x06x\t\n\xbc')
        tmp2 = ArrayField(ArrayTest)
        tmp2.deserialize(ser)
        self.assertEqual(tmp.__repr__(), tmp2.__repr__())

if __name__ == '__main__':
    unittest.main()
