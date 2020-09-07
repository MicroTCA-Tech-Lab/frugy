"""
SPDX-License-Identifier: BSD-3-Clause
Copyright (c) 2020 Deutsches Elektronen-Synchrotron DESY.
See LICENSE.txt for license details.
"""

from frugy.types import FruAreaVersioned, FruAreaSized, FixedField, StringField, StringField, bin2hex_helper, CustomStringArray
from frugy.fru_registry import FruRecordType, rec_register
from datetime import datetime, timedelta
import logging


def ipmi_area(cls):
    rec_register(cls, FruRecordType.ipmi_area)
    return cls


_default_language_code = 0  # Use English and UTF-8 as default encoding


@ipmi_area
class CommonHeader(FruAreaVersioned):
    ''' Platform Management FRU Information Storage Definition, Table 8-1 '''

    _schema = [
        ('internal_use_offs', FixedField, 'u8', {'default': 0}),
        ('chassis_info_offs', FixedField, 'u8', {'default': 0}),
        ('board_info_offs', FixedField, 'u8', {'default': 0}),
        ('product_info_offs', FixedField, 'u8', {'default': 0}),
        ('multirecord_offs', FixedField, 'u8', {'default': 0}),
    ]

    def __getitem__(self, key):
        return self._get(key) * 8

    def __setitem__(self, key, value):
            if value % 8 != 0:
                raise RuntimeError("Offset not aligned to 64 bit")
            self._set(key, value // 8)
    
    def reset(self):
        for item in self._dict:
            self._set(item, 0)


@ipmi_area
class ChassisInfo(FruAreaSized):
    ''' Platform Management FRU Information Storage Definition, Table 10-1 '''

    _schema = [
        ('type', FixedField, 'u8'),
        ('part_number', StringField),
        ('serial_number', StringField),
        ('custom_info_fields', CustomStringArray),
    ]


@ipmi_area
class BoardInfo(FruAreaSized):
    ''' Platform Management FRU Information Storage Definition, Table 11-1 '''

    _schema = [
        ('language_code', FixedField, 'u8', {'default': _default_language_code}),
        ('mfg_date_time', FixedField, 'u24', {'default': 0}),
        ('manufacturer', StringField),
        ('product_name', StringField),
        ('serial_number', StringField),
        ('part_number', StringField),
        ('fru_file_id', StringField),
        ('custom_info_fields', CustomStringArray),
    ]

    _time_ref = datetime(1996, 1, 1)

    def _set_mfg_date_time(self, timestamp):
        if timestamp is not None:
            td = timestamp - BoardInfo._time_ref
            minutes = td.seconds // 60 + td.days * (60*24)
            self._set('mfg_date_time', minutes)
        else:
            self._set('mfg_date_time', 0)

    def _get_mfg_date_time(self):
        minutes = self._get('mfg_date_time')
        if minutes != 0:
            timestamp = BoardInfo._time_ref + timedelta(minutes=minutes)
            return timestamp
        else:
            return None


@ipmi_area
class ProductInfo(FruAreaSized):
    ''' Platform Management FRU Information Storage Definition, Table 12-1 '''

    _schema = [
        ('language_code', FixedField, 'u8', {'default': _default_language_code}),
        ('manufacturer', StringField),
        ('product_name', StringField),
        ('part_number', StringField),
        ('version', StringField),
        ('serial_number', StringField),
        ('asset_tag', StringField),
        ('fru_file_id', StringField),
        ('custom_info_fields', CustomStringArray),
    ]
