from frugy.types import MultirecordEntry, FixedField


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
