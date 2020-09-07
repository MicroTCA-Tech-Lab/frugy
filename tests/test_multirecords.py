"""
SPDX-License-Identifier: BSD-3-Clause
Copyright (c) 2020 Deutsches Elektronen-Synchrotron DESY.
See LICENSE.txt for license details.
"""

import unittest
from frugy.multirecords import MultirecordArea
from frugy.multirecords_picmg import ModuleCurrentRequirements

class TestPicmg(unittest.TestCase):
    def test_module_current(self):
        mcr = ModuleCurrentRequirements({
            'current_draw': 7.5
        })
        self.assertEqual(mcr.serialize(), b'\xc0\x02\x06\x14$Z1\x00\x16\x00K')


class TestMultirecord(unittest.TestCase):
    def test_multi(self):
        mr = MultirecordArea([{
                'type': 'ModuleCurrentRequirements',
                'current_draw': 7.5
            }
        ])
        self.assertEqual(mr.serialize(), b'\xc0\x82\x06\x14\xa4Z1\x00\x16\x00K')

if __name__ == '__main__':
    unittest.main()
