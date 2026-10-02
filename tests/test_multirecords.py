"""
SPDX-License-Identifier: BSD-3-Clause
Copyright (c) 2020 Deutsches Elektronen-Synchrotron DESY.
See LICENSE.txt for license details.
"""

import unittest
from frugy.multirecords import MultirecordArea, MultirecordEntry
from frugy.multirecords_fmc import FmcMainDefinition
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


class TestFmc(unittest.TestCase):
    def test_vadatech_connector_bit_order(self):
        definition = FmcMainDefinition({
            'module_size': 'single_width',
            'p1_connector_size': 'lpc',
            'p2_connector_size': 'not_fitted',
            'clock_direction': 'm2c',
            'p1_a_num_signals': 68,
            'p1_b_num_signals': 0,
            'p2_a_num_signals': 0,
            'p2_b_num_signals': 0,
            'p1_gbt_num_trcv': 0,
            'p2_gbt_num_trcv': 0,
            'tck_max_clock': 0,
        })

        try:
            FmcMainDefinition.vadatech_workaround_enabled = False
            self.assertEqual(definition.serialize()[9], 0x0c)

            FmcMainDefinition.vadatech_workaround_enabled = True
            serialized = definition.serialize()
            self.assertEqual(serialized[9], 0x30)

            decoded, remainder, _ = MultirecordEntry.deserialize(serialized)
            self.assertEqual(remainder, b'')
            self.assertEqual(decoded.to_dict(), definition.to_dict())
        finally:
            FmcMainDefinition.vadatech_workaround_enabled = False


if __name__ == '__main__':
    unittest.main()
