import unittest
from frugy.multirecords import MultirecordArea
from frugy.multirecords import ModuleCurrentRequirements

class TestPicmg(unittest.TestCase):
    def test_module_current(self):
        mcr = ModuleCurrentRequirements({
            'current_draw': 7.5
        })
        self.assertEqual(mcr.serialize(), b'\xc0\x02\x01\x14\x29\x00\x31\x5a\x16\x00\x4b')


class TestMultirecord(unittest.TestCase):
    def test_multi(self):
        mr = MultirecordArea({
            'ModuleCurrentRequirements': {
                'current_draw': 7.5
            }
        })
        self.assertEqual(mr.serialize(), b'\xc0\x82\x01\x14\xa9\x00\x31\x5a\x16\x00\x4b')
