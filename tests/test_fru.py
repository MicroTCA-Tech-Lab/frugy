"""
SPDX-License-Identifier: BSD-3-Clause
Copyright (c) 2020 Deutsches Elektronen-Synchrotron DESY.
See LICENSE.txt for license details.
"""

import unittest
from datetime import datetime
from frugy.fru import Fru
from frugy.multirecords import MultirecordEntry
import os

class TestFru(unittest.TestCase):
    '''
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

    def test_damc_zup(self):
        tmp = Fru()
        tmp.load_bin("tests/fru_damc-fmc2zup.bin")
#        print(tmp)
        tmp.save_yaml("damc-fmc2zup.yml")
    '''
    def bin_to_yaml(self, src_name, dest_name):
        print(f'converting {src_name} to {dest_name}')
        tmp = Fru()
        try:
            tmp.load_bin(src_name)
            tmp.save_yaml(dest_name)
        except RuntimeError:
            print(f'Error while converting {src_name}')

    def test_bin_files(self):
        for root, _, files in os.walk('tests/bin_files'):
            for name in files:
                name_base, name_ext = os.path.splitext(name)
                if name_ext == '.bin':
                    MultirecordEntry.opalkelly_workaround_enabled = name.startswith('opalkelly')
                    name_src = os.path.join(root, name)
                    name_dest = os.path.join('examples', name_base + '.yml')
                    self.bin_to_yaml(name_src, name_dest)

if __name__ == '__main__':
    unittest.main()
