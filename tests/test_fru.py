import unittest
from datetime import datetime
from frugy.fru import Fru


class TestFru(unittest.TestCase):
    def fru_test_from_dict(self, initdict, test_name):
        fru = Fru(initdict)
        fru.save_bin(f"{test_name}.bin")
        fru.save_yaml(f"{test_name}.yml")
        tmp1 = Fru()
        tmp1.load_bin(f"{test_name}.bin")
        self.assertEqual(fru.to_dict(), tmp1.to_dict())
        tmp2 = Fru()
        tmp2.load_yaml(f"{test_name}.yml")
        self.assertEqual(fru.to_dict(), tmp2.to_dict())
    
    def test_damc_mmc_breakout(self):
        self.fru_test_from_dict({
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
        }, 'dmmc-breakout')

    def test_dmmc_stamp(self):
        self.fru_test_from_dict({
            'BoardInfo': {
                'board_manufacturer': 'DESY',
                'board_product_name': 'DMMC-STAMP Rev.A',
                'board_serial_number': '0000',
                'board_part_number': '0000',
                'fru_file_id': 'none',
            },
            'ProductInfo': {
                'manufacturer_name': 'DESY',
                'product_name': 'DMMC-STAMP Rev.A',
                'product_part_number': '0000',
                'product_version': '0000',
                'product_serial_number': '0000',
                'asset_tag': 'none',
                'fru_file_id': 'none',
            },
            'MultirecordArea': [
                {
                    'type': 'ModuleCurrentRequirements',
                    'current_draw': 6.5
                }
            ]
        }, 'dmmc-stamp')

    def test_cern_img(self):
        # uses test file generated from:
        # https://www.ohwr.org/project/fmc-dac-600m-12b-1cha-tst/blob/master/software/spec-sw/fmc-bus/tools/fru-generator
        tmp = Fru()
        tmp.load_bin("tests/cern.bin")
        tmp.save_yaml("cern.yml")

        tmp1 = Fru()
        tmp1.load_yaml("cern.yml")
        tmp1.save_bin("cern2.bin")