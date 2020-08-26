from frugy.types import MultirecordEntry, FixedField


class MultirecordArea:
    def __init__(self, initdict=None):
        self.records = {}
        if initdict is not None:
            self.update(initdict)
    
    def update(self, initdict):
        self.records = {}
        for k, v in initdict.items():
            constructor = globals()[k]
            self.records[k] = constructor(v)
    
    def __repr__(self):
        return self.to_dict().__repr__()

    def to_dict(self):
        return {k: v.to_dict() for k, v in self.records.items()}
    
    def serialize(self):
        result = b''
        rec = list(self.records.keys())
        for i, k in enumerate(rec):
            v = self.records[k]
            v.end_of_list = 1 if i == len(rec)-1 else 0
            result += v.serialize()
        return result
    
    def size_total(self):
        return sum([v.size_total() for v in self.records.values()])


class PicmgEntry(MultirecordEntry):
    def __init__(self, record_id, schema, initdict=None, format_version=2):
        self.record_id = record_id
        super().__init__(0xc0, schema, initdict=initdict, format_version=format_version)
    
    def _payload_prologue(self):
        return b'\x00\x31\x5a' + self.record_id.to_bytes(length=1, byteorder='little') + b'\x00'


class ModuleCurrentRequirements(PicmgEntry):
    def __init__(self, initdict=None):
        super().__init__(0x16, [
            ('current_draw', FixedField('u8', value=0))
        ], initdict)

    def _set_current_draw(self, value):
        self._set('current_draw', int(value * 10.0))

    def _get_current_draw(self):
        return float(self._get('current_draw') / 10.0)
