from frugy.types import FruAreaBase, FixedField
import bitstruct

_multirecord_types_lookup = {
    0xc0: 'PicmgEntry'
}

_multirecord_types_lookup_rev = {
    v: k for k, v in _multirecord_types_lookup.items()
}

class MultirecordEntry(FruAreaBase):
    _multirecord_header_fmt = 'u8u1u3u4u8u8'

    def __init__(self, type_id: int, schema, initdict=None, format_version=2):
        self.type_id = type_id
        self.end_of_list = 0
        self.format_version = format_version
        super().__init__(schema, initdict=initdict)

    def size_payload(self):
        # Add header size
        return super().size_payload() + 5 + len(self._payload_prologue())
    
    def _payload_prologue(self):
        # data prepended before actual payload by subclasses
        return b''

    def serialize(self):
        payload = self._payload_prologue() + super().serialize()
        payload_cksum = (-sum(payload)) & 0xff
        header = bitstruct.pack(self._multirecord_header_fmt,
                                self.type_id,
                                self.end_of_list,
                                0,
                                self.format_version,
                                len(payload),
                                payload_cksum)
        header_cksum = (-sum(header)) & 0xff
        header += header_cksum.to_bytes(length=1, byteorder='little')
        return header + payload

    @classmethod
    def deserialize(cls, input):
        header_fmt_complt = MultirecordEntry._multirecord_header_fmt + 'u8'
        header_len = bitstruct.calcsize(header_fmt_complt) // 8
        type_id, end_of_list, _, format_version, \
        payload_len, payload_cksum, _ = bitstruct.unpack(header_fmt_complt, input)

        header, remainder = input[:header_len], input[header_len:]
        payload, remainder = remainder[:payload_len], remainder[payload_len:]
        if sum(header) & 0xff != 0:
            raise RuntimeError("MultirecordEntry header checksum invalid")
        if (sum(payload) + payload_cksum) & 0xff != 0:
            raise RuntimeError("MultirecordEntry payload checksum invalid")

        cls_id = globals()[_multirecord_types_lookup[type_id]]
        new_entry = cls_id.from_payload(payload)
        new_entry.type_id = type_id
        new_entry.format_version = format_version
        new_entry.end_of_list = end_of_list
        
        return new_entry, remainder


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
    
    def deserialize(self, input):
        remainder = input
        while len(remainder):            
            new_entry, remainder = MultirecordEntry.deserialize(input)
            self.records[new_entry.__class__.__name__] = new_entry
            if new_entry.end_of_list:
                break

        return remainder

    def size_total(self):
        return sum([v.size_total() for v in self.records.values()])


_picmg_types_lookup = {
    0x16: 'ModuleCurrentRequirements'
}

_picmg_types_lookup_rev = {
    v: k for k, v in _picmg_types_lookup.items()
}

class PicmgEntry(MultirecordEntry):
    _picmg_identifier = b'\x5a\x31\x00'

    def __init__(self, record_id, schema, initdict=None, format_version=2):
        self.record_id = record_id
        super().__init__(_multirecord_types_lookup_rev['PicmgEntry'],
                         schema, initdict=initdict, format_version=format_version)
    
    def _payload_prologue(self):
        return self._picmg_identifier + self.record_id.to_bytes(length=1, byteorder='little') + b'\x00'
    
    @classmethod
    def from_payload(cls, payload):
        picmg_id, payload = payload[:len(cls._picmg_identifier)], payload[len(cls._picmg_identifier):]
        rec_id, payload = payload[:1], payload[1:]
        zero_byte, payload = payload[:1], payload[1:]
        if picmg_id != cls._picmg_identifier:
            raise RuntimeError("PICMG identifier not found")
        if zero_byte != b'\x00':
            raise RuntimeError("PICMG zero byte not found")
        rec_id = int.from_bytes(rec_id, byteorder='little')
        cls_inst = globals()[_picmg_types_lookup[rec_id]]()
        cls_inst._deserialize(payload)
        return cls_inst


class ModuleCurrentRequirements(PicmgEntry):
    def __init__(self, initdict=None):
        super().__init__(_picmg_types_lookup_rev[self.__class__.__name__], [
            ('current_draw', FixedField('u8', value=0))
        ], initdict)

    def _set_current_draw(self, value):
        self._set('current_draw', int(value * 10.0))

    def _get_current_draw(self):
        return float(self._get('current_draw') / 10.0)
