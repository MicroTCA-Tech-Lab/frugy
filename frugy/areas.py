from frugy.types import FruArea, FixedField


class FruCommonHeader(FruArea):
    _format_version = 1
    _schema = [
        ('format_version', FixedField('u4u4', value=(0, _format_version))),
        ('internal_use_offs', FixedField('u8', value=0)),
        ('chassis_info_offs', FixedField('u8', value=0)),
        ('board_area_offs', FixedField('u8', value=0)),
        ('product_info_offs', FixedField('u8', value=0)),
        ('multirecord_offs', FixedField('u8', value=0)),
    ]

    def __getitem__(self, key):
        return self._get(key) * 8 if key.endswith('offs') else self._get(key)

    def __setitem__(self, key, value):
        if key.endswith('offs'):
            if value % 8 != 0:
                raise RuntimeError("Offset not aligned to 64 bit")
            self._set(key, int(value / 8))
        else:
            self._set(key, value)
