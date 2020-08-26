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

    def test_foo(self):
        initdict = {
            'BoardInfo': {
                'board_manufacturer': 'Foo',
                'board_product_name': 'Foo-Dings',
                'board_serial_number': '1234',
                'board_part_number': '5678',
                'fru_file_id': 'N/A',
            },
            'ProductInfo': {
                'manufacturer_name': 'FooBar',
                'product_name': 'Superfoo',
                'product_part_number': '4711',
                'product_version': 'V0.00-alpha',
                'product_serial_number': '0815',
                'asset_tag': 'N/A',
                'fru_file_id': 'N/A',
            },
            'MultirecordArea': {
                'ModuleCurrentRequirements': {
                    'current_draw': 7.5
                }
            }
        }
        fru = Fru(initdict)
        fru.save_bin("foo.bin")
        fru.save_yaml("foo.yml")
        # We don't support deserializing multirecords (yet)
        # tmp1 = Fru()
        # tmp1.load_bin("foo.bin")
        # self.assertEqual(fru.to_dict(), tmp1.to_dict())
        tmp2 = Fru()
        tmp2.load_yaml("foo.yml")
        self.assertEqual(fru.to_dict(), tmp2.to_dict())
