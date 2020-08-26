from frugy.types import FruAreaBase, FruArea, FixedField, StringField
from datetime import datetime, timedelta

_language_code = 0  # Use English and UTF-8 as default encoding

class CommonHeader(FruAreaBase):
    _schema = [
        ('internal_use_offs', FixedField('u8', value=0)),
        ('chassis_info_offs', FixedField('u8', value=0)),
        ('board_info_offs', FixedField('u8', value=0)),
        ('product_info_offs', FixedField('u8', value=0)),
        ('multirecord_offs', FixedField('u8', value=0)),
    ]

    def __getitem__(self, key):
        return self._get(key) * 8

    def __setitem__(self, key, value):
            if value % 8 != 0:
                raise RuntimeError("Offset not aligned to 64 bit")
            self._set(key, value // 8)


class ChassisInfo(FruArea):
    _schema = [
        ('chassis_type', FixedField('u8')),
        ('chassis_part_number', StringField()),
        ('chassis_serial_number', StringField()),
        # TODO: do we need custom chassis info fields?
    ]


class BoardInfo(FruArea):
    _schema = [
        ('language_code', FixedField('u8', value=_language_code)),
        ('mfg_date_time', FixedField('u24', value=0)),
        ('board_manufacturer', StringField()),
        ('board_product_name', StringField()),
        ('board_serial_number', StringField()),
        ('board_part_number', StringField()),
        ('fru_file_id', StringField()),
        # TODO: do we need custom manufacturing info fields?
    ]

    _time_ref = datetime(1996, 1, 1)

    def _set_mfg_date_time(self, timestamp):
        td = timestamp - BoardInfo._time_ref
        minutes = td.seconds // 60 + td.days * (60*24)
        self._set('mfg_date_time', minutes)

    def _get_mfg_date_time(self):
        minutes = self._get('mfg_date_time')
        timestamp = BoardInfo._time_ref + timedelta(minutes=minutes)
        return timestamp


class ProductInfo(FruArea):
    _schema = [
        ('language_code', FixedField('u8', value=_language_code)),
        ('manufacturer_name', StringField()),
        ('product_name', StringField()),
        ('product_part_number', StringField()),
        ('product_version', StringField()),
        ('product_serial_number', StringField()),
        ('asset_tag', StringField()),
        ('fru_file_id', StringField()),
        # TODO: do we need custom manufacturing info fields?
    ]
