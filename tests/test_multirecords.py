import unittest
from frugy.multirecords import MultirecordArea
from frugy.multirecords import ModuleCurrentRequirements

class TestPicmg(unittest.TestCase):
    def test_module_current(self):
        mcr = ModuleCurrentRequirements({
            'current_draw': 7.5
        })
        with open("test.bin", "wb") as f:
            f.write(mcr.serialize())


class TestMultirecord(unittest.TestCase):
    def test_multi(self):
        mr = MultirecordArea({
            'ModuleCurrentRequirements': {
                'current_draw': 7.5
            }
        })
        with open("test1.bin", "wb") as f:
            f.write(mr.serialize())
