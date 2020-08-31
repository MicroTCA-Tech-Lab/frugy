import unittest
from frugy.multirecords import MultirecordArea, MultirecordEntry, ModuleCurrentRequirements, PointToPointConnectivity

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


class TestP2P(unittest.TestCase):
    def test_p2p(self):
        p2p = PointToPointConnectivity({
            'guids': [
                '7f72a8c4-0577-4825-b0d3-b574a65f6115',
                'dffdd6a5-20b9-4b47-9ba7-a6b3e00ae6c0',
                'feedbabe-d00f-affe-0000-5555aaaaffff'
            ],
            'amc_module_flag': 1,
            'conn_dev_id': 0,
            'channel_descriptors': [{
                'lane0_port': 1,
                'lane1_port': 2,
                'lane2_port': 3,
                'lane3_port': 4
            },{
                'lane0_port': 5,
                'lane1_port': 6
            }],
            'link_descriptors': [{
                'asymm_match': 1,
                'grouping_id': 2,
                'link_type_ext': 3,
                'link_type': 4,
                'link_designator': 5
            }]
        })
        ser = p2p.serialize()
        tmp = MultirecordEntry.deserialize(ser)
