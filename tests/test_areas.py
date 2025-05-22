"""
SPDX-License-Identifier: BSD-3-Clause
Copyright (c) 2020 Deutsches Elektronen-Synchrotron DESY.
See LICENSE.txt for license details.
"""

import unittest
from datetime import date, datetime
from frugy.areas import CommonHeader, ChassisInfo, BoardInfo, ProductInfo
from frugy.types import FruAreaBase, FixedField


class foo(FruAreaBase):
    _schema = [
        ('first2', FixedField, 'u2', {'default': 0}),
        ('second2', FixedField, 'u2', {'default': 0}),
        ('then4', FixedField, 'u4', {'default': 0}),
        ('lastone', FixedField, 'u8', {'default': 0}),
    ]

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
            'type': 0x05,
            'part_number': 'Test1234',
            'serial_number': 'SN-4711'
        }
        b = b'\x01\x03\x05\xc8Test1234\xc7SN-4711\xc1\x00\x00\xa2'
        self.do_test_area(ChassisInfo, a, b, 24)

    def test_boardinfo(self):
        a = {
            'mfg_date_time': datetime(2020, 1, 1, 12, 30, 0),
            'manufacturer': 'FabLab',
            'product_name': 'FooGadget',
            'serial_number': '1234-rev42',
            'part_number': '54750893',
            'fru_file_id': 'N/A',
        }
        b = b'\x01\x07\x00\xae\x9f\xc0\xc6FabLab\xc9FooGadget\xca1234-rev42\xc854750893\xc3N/A\xc1\x00\x00\x00\x00\x00\x00\x00\xad'
        self.do_test_area(BoardInfo, a, b, 56)

    def test_productinfo(self):
        a = {
            'manufacturer': 'DESY',
            'product_name': 'Test Product',
            'part_number': 'P1234',
            'version': 'V9.0',
            'serial_number': 'SN98765',
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


    def test_y2k_rollover(self):
        bi = BoardInfo()
        dt_2000 = bi._timestamp_to_minutes(datetime(2000, 2, 3))
        dt_2031 = bi._timestamp_to_minutes(datetime(2031, 12, 27, 20, 16, 0))

        # Test truncation (yaml 2 bin)
        self.assertEqual(bi._handle_y2k27_rollover_yaml2bin(dt_2000), dt_2000)
        self.assertEqual(bi._handle_y2k27_rollover_yaml2bin(dt_2031), dt_2000)

        # Test extension (bin 2 yaml)
        now_2025 = datetime(2025, 1, 1)
        now_2031 = datetime(2031, 5, 1)
        now_2032 = datetime(2032, 1, 1)

        self.assertEqual(bi._handle_y2k27_rollover_bin2yaml(dt_2000, now_2025), dt_2000)
        self.assertEqual(bi._handle_y2k27_rollover_bin2yaml(dt_2000, now_2031), dt_2031)
        self.assertEqual(bi._handle_y2k27_rollover_bin2yaml(dt_2000, now_2032), dt_2031)

if __name__ == '__main__':
    unittest.main()
