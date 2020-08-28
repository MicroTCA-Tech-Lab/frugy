#!/usr/bin/env python3

import unittest
from datetime import datetime
from frugy.areas import CommonHeader, ChassisInfo, BoardInfo, ProductInfo
from frugy.types import FruAreaBase, FixedField


class foo(FruAreaBase):
    def __init__(self, initdict=None):
        super().__init__([
            ('first2', FixedField('u2', value=0)),
            ('second2', FixedField('u2', value=0)),
            ('then4', FixedField('u4', value=0)),
            ('lastone', FixedField('u8', value=0)),
        ], initdict)

class TestAreas(unittest.TestCase):
    def do_test_area(self, cls, src_dict, ser_vfy, sz):
        ch = cls()
        ch.update(src_dict)
        self.assertEqual(ch.size_total(), sz)
        ser = ch.serialize()
        self.assertEqual(ser, ser_vfy)
        ser += b'remainder'
        tmp = cls()
        self.assertEqual(tmp.deserialize(ser), b'remainder')
        self.assertEqual(tmp.__repr__(), ch.__repr__())

    def test_commonheader(self):
        a = {
            'internal_use_offs': 0,
            'chassis_info_offs': 8,
            'board_info_offs': 16,
            'product_info_offs': 80,
            'multirecord_offs': 160
        }
        b = b'\x01\x00\x01\x02\x0a\x14\x00\xde'
        self.do_test_area(CommonHeader, a, b, 8)

    def test_chassisinfo(self):
        a = {
            'chassis_type': 0x05,
            'chassis_part_number': 'Test1234',
            'chassis_serial_number': 'SN-4711'
        }
        b = b'\x01\x03\x05\xc8Test1234\xc7SN-4711\xc1\x00\x00\xa2'
        self.do_test_area(ChassisInfo, a, b, 24)

    def test_boardinfo(self):
        a = {
            'mfg_date_time': datetime(2020, 1, 1, 12, 30, 0),
            'board_manufacturer': 'FabLab',
            'board_product_name': 'FooGadget',
            'board_serial_number': '1234-rev42',
            'board_part_number': '54750893',
            'fru_file_id': 'N/A',
        }
        b = b'\x01\x07\x00\xae\x9f\xc0\xc6FabLab\xc9FooGadget\xca1234-rev42\xc854750893\xc3N/A\xc1\x00\x00\x00\x00\x00\x00\x00\xad'
        self.do_test_area(BoardInfo, a, b, 56)

    def test_productinfo(self):
        a = {
            'manufacturer_name': 'DESY',
            'product_name': 'Test Product',
            'product_part_number': 'P1234',
            'product_version': 'V9.0',
            'product_serial_number': 'SN98765',
            'asset_tag': 'Unknown',
            'fru_file_id': 'N/A',
        }
        b = b'\x01\x07\x00\xc4DESY\xccTest Product\xc5P1234\xc4V9.0\xc7SN98765\xc7Unknown\xc3N/A\xc1\x00\x00\x8e'
        self.do_test_area(ProductInfo, a, b, 56)

    def test_bitfield(self):
        f = foo({
            'first2': 2,
            'second2': 1,
            'then4': 5,
            'lastone': 7,
        })
        v = f.serialize()
        self.assertEqual(v, b'\x95\x07')
        v += b'remainder'
        e = foo()
        v = e.deserialize(v)
        self.assertEqual(v, b'remainder')
        self.assertEqual(e.to_dict(), {'first2': 2, 'second2': 1, 'then4': 5, 'lastone': 7})

if __name__ == '__main__':
    unittest.main()
