#!/usr/bin/env python3

import unittest

from frugy.areas import CommonHeader, ChassisInfo, BoardInfo, ProductInfo


class TestAreas(unittest.TestCase):
    def test_commonheader(self):
        a = {
            'internal_use_offs': 0,
            'chassis_info_offs': 8,
            'board_area_offs': 16,
            'product_info_offs': 80,
            'multirecord_offs': 160
        }

        ch = CommonHeader()
        ch.update(a)
        self.assertEqual(ch.size_payload(), 6)
        self.assertEqual(ch.size_total(), 8)
        ser = ch.serialize()
        self.assertEqual(ser, b'\x01\x00\x01\x02\x0a\x14\x00\xde')
        ser += b'remainder'
        tmp = CommonHeader()
        self.assertEqual(tmp.deserialize(ser), b'remainder')
        self.assertEqual(tmp.__repr__(), ch.__repr__())


if __name__ == '__main__':
    unittest.main()
