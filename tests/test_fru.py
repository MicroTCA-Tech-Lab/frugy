import unittest
from datetime import datetime
from frugy.fru import Fru


class TestFru(unittest.TestCase):
    def test_damc_mmc_breakout(self):
        initdict = {
            'BoardInfo': {
                'board_manufacturer': 'DESY',
                'board_product_name': 'DAMC-MMC-Breakout',
                'board_serial_number': '0000',
                'board_part_number': '0000',
                'fru_file_id': 'none',
            },
            'ProductInfo': {
                'manufacturer_name': 'DESY',
                'product_name': 'DAMC-MMC-Breakout',
                'product_part_number': '0000',
                'product_version': '0000',
                'product_serial_number': '0000',
                'asset_tag': 'none',
                'fru_file_id': 'none',
            }
        }
        fru = Fru(initdict)
        fru.save_bin("mmc_breakout.bin")
        fru.save_yaml("mmc_breakout.yml")
        tmp1 = Fru()
        tmp1.load_bin("mmc_breakout.bin")
        self.assertEqual(fru.to_dict(), tmp1.to_dict())
        tmp2 = Fru()
        tmp2.load_yaml("mmc_breakout.yml")
        self.assertEqual(fru.to_dict(), tmp2.to_dict())
