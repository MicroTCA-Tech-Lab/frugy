import unittest
from datetime import datetime
from frugy.fru import Fru


class TestFru(unittest.TestCase):
    """
    def test_fru(self):
        initdict = {
            'ChassisInfo': {
                'chassis_type': 0x05,
                'chassis_part_number': 'Test1234',
                'chassis_serial_number': 'SN-4711'
            },
            'BoardInfo': {
                'mfg_date_time': datetime(2020, 1, 1, 12, 30, 0),
                'board_manufacturer': 'FabLab',
                'board_product_name': 'FooGadget',
                'board_serial_number': '1234-rev42',
                'board_part_number': '54750893',
                'fru_file_id': 'N/A',
            },
            'ProductInfo': {
                'manufacturer_name': 'DESY',
                'product_name': 'Test Product',
                'product_part_number': 'P1234',
                'product_version': 'V9.0',
                'product_serial_number': 'SN98765',
                'asset_tag': 'Unknown',
                'fru_file_id': 'N/A',
            }
        }
        fru = Fru(initdict)
        fru.save_yaml("fru.yml")
        fru.save_bin("fru.bin")

        tmp = Fru()
        tmp.load_yaml("fru.yml")
        # print(tmp)
    """
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
        fru.save_yaml("mmc_breakout.yml")
        fru.save_bin("mmc_breakout.bin")
