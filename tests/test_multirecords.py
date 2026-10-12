"""
SPDX-License-Identifier: BSD-3-Clause
Copyright (c) 2020 Deutsches Elektronen-Synchrotron DESY.
See LICENSE.txt for license details.
"""

import unittest
from frugy.multirecords import MultirecordArea, MultirecordEntry
from frugy.multirecords_fmc import FmcMainDefinition
from frugy.multirecords_picmg import ModuleCurrentRequirements
from frugy.multirecords_vita import ChassisAddressTable, ChassisManagerIpConnection

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


class TestVita(unittest.TestCase):
    def test_chassis_address_table(self):
        table = ChassisAddressTable({
            'chassis_identifier': 'VPX-1',
            'entries': [
                {'hardware_address': 0x10, 'site_number': 1,
                 'site_type': 'dedicated_chassis_manager'},
                {'hardware_address': 0x41, 'site_number': 0,
                 'site_type': 'front_loading_vpx_module'},
                {'hardware_address': 0x47, 'site_number': 1,
                 'site_type': 'fan_tray'},
            ]
        })
        serialized = table.serialize()
        payload = serialized[5:]
        # VITA manufacturer ID, record ID, format version, type/length
        self.assertEqual(payload[:6], b'\xac\x81\x00\x10\x00\xc5')
        # the identifier padded to 20 bytes, the count and the entries
        self.assertEqual(payload[6:26], b'VPX-1' + b'\x00' * 15)
        self.assertEqual(payload[26:], b'\x03\x10\x01\x03\x41\x00\x00'
                         b'\x47\x01\x04')
        self.assertEqual(serialized[2], len(payload))

        decoded, remainder, _ = MultirecordEntry.deserialize(serialized)
        self.assertEqual(remainder, b'')
        self.assertIsInstance(decoded, ChassisAddressTable)
        self.assertEqual(decoded.to_dict(), table.to_dict())
        self.assertEqual(decoded.to_dict()['entries'][2]['site_type'],
                         'fan_tray')

    def test_chassis_identifier_too_long(self):
        table = ChassisAddressTable({'chassis_identifier': 'X' * 21})
        with self.assertRaises(ValueError):
            table.serialize()

    def test_chassis_manager_ip_connection(self):
        record = ChassisManagerIpConnection({
            'ip_address': '192.168.0.10',
            'default_gateway': '192.168.0.1',
            'subnet_mask': '255.255.255.0',
        })
        serialized = record.serialize()
        payload = serialized[5:]
        # VITA manufacturer ID, record ID 13h, format version, then the
        # addresses MS byte first
        self.assertEqual(payload, b'\xac\x81\x00\x13\x00'
                         b'\xc0\xa8\x00\x0a\xc0\xa8\x00\x01\xff\xff\xff\x00')
        decoded, remainder, _ = MultirecordEntry.deserialize(serialized)
        self.assertEqual(remainder, b'')
        self.assertEqual(decoded.to_dict()['ip_address'], '192.168.0.10')
