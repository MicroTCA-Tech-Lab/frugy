#!/usr/bin/env python3

import unittest

from frugy.types import FixedField, StringField, StringFmt


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


class TestString(unittest.TestCase):
    def test_null(self):
        nul = StringField()
        ser = nul.serialize()
        self.assertEqual(ser, b'\xc0')
        ser += b'remainder'
        tmp = StringField()
        self.assertEqual(tmp.deserialize(ser), b'remainder')
        self.assertEqual(tmp.value, '')

    def test_plain(self):
        testStr = 'Hello world'
        tmp = StringField(testStr, format=StringFmt.ASCII_8BIT)
        self.assertEqual(tmp.size(), 12)
        ser = tmp.serialize()
        self.assertEqual(ser, b'\xcbHello world')
        ser += b'remainder'
        tmp2 = StringField()
        self.assertEqual(tmp2.deserialize(ser), b'remainder')
        self.assertEqual(tmp2.format, StringFmt.ASCII_8BIT)
        self.assertEqual(tmp2.value, testStr)

    def test_bcd_plus(self):
        testStr = '123.45-67 890'
        tmp = StringField(testStr, format=StringFmt.BCD_PLUS)
        self.assertEqual(tmp.size(), 8)
        ser = tmp.serialize()
        self.assertEqual(ser, b'\x47\x12\x3c\x45\xb6\x7a\x89\x0a')
        ser += b'remainder'
        tmp2 = StringField()
        self.assertEqual(tmp2.deserialize(ser), b'remainder')
        self.assertEqual(tmp2.format, StringFmt.BCD_PLUS)
        self.assertEqual(tmp2.value, testStr + ' ')  # append padding space

    def test_ascii_6bit(self):
        testStr = 'IPMI Hello world'
        tmp = StringField(testStr, format=StringFmt.ASCII_6BIT)
        self.assertEqual(tmp.size(), 13)
        ser = tmp.serialize()
        self.assertEqual(ser,
                         b'\x8c\x29\xdc\xa6\x00Z\xb2\xec\x0b\xdc\xaf\xcc\x92')
        ser += b'remainder'
        tmp2 = StringField()
        self.assertEqual(tmp2.deserialize(ser), b'remainder')
        self.assertEqual(tmp2.format, StringFmt.ASCII_6BIT)
        self.assertEqual(tmp2.value, 'IPMI HELLO WORLD')


if __name__ == '__main__':
    unittest.main()
