###########################################################################
#      ____  _____________  __    __  __ _           _____ ___   _        #
#     / __ \/ ____/ ___/\ \/ /   |  \/  (_)__ _ _ __|_   _/ __| /_\  (R)  #
#    / / / / __/  \__ \  \  /    | |\/| | / _| '_/ _ \| || (__ / _ \      #
#   / /_/ / /___ ___/ /  / /     |_|  |_|_\__|_| \___/|_| \___/_/ \_\     #
#  /_____/_____//____/  /_/      T  E  C  H  N  O  L  O  G  Y   L A B     #
#                                                                         #
#          Copyright 2021 Deutsches Elektronen-Synchrotron DESY.          #
#                  SPDX-License-Identifier: BSD-3-Clause                  #
#                                                                         #
###########################################################################

from frugy.types import FruAreaVersioned, FruAreaSized, FixedField, StringField, StringField, bin2hex_helper, CustomStringArray
from frugy.fru_registry import FruRecordType, rec_register
from datetime import datetime, timedelta
import logging
import frugy

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
        ('language_code', FixedField, 'u8', {
         'default': _default_language_code}),
        ('mfg_date_time', FixedField, 'u24', {'default': 0}),
        ('manufacturer', StringField),
        ('product_name', StringField),
        ('serial_number', StringField),
        ('part_number', StringField),
        ('fru_file_id', StringField),
        ('custom_info_fields', CustomStringArray),
    ]

    # With a Y2K27 rollover baked into the specification, we have to deal with
    # - 24bit overflow when converting yaml to bin
    # - uncertainty of original 25th bit when converting bin to yaml
    # see also: https://github.com/MicroTCA-Tech-Lab/frugy/issues/11
    _time_ref = datetime(1996, 1, 1)
    _time_rollover_limit = 2**24

    def _timestamp_to_minutes(self, timestamp):
        td = timestamp - self._time_ref
        return td.seconds // 60 + td.days * (60*24)

    def _timestamp_from_minutes(self, minutes):
        return BoardInfo._time_ref + timedelta(minutes=minutes)

    def _handle_y2k27_rollover_yaml2bin(self, minutes):
        # Truncate the timestamp to 24 bits
        # If the remainder is nonzero, log a warning.
        minutes_truncated = minutes % BoardInfo._time_rollover_limit
        if minutes != minutes_truncated:
            min_str = self._timestamp_from_minutes(minutes).isoformat()
            min_trunc_str = self._timestamp_from_minutes(minutes_truncated).isoformat()
            logging.warning(f'Timestamp {min_str} truncated; may be interpreted by FRU parsers as {min_trunc_str}')
        return minutes_truncated

    def _handle_y2k27_rollover_bin2yaml(self, minutes, now):
        # Apply heuristic to possibly truncated timestamp:
        # If it is "too old" relative to the system time, add rollover timedelta and log a warning.
        # We draw the line at 31 years into the past (not the full 2**24 minutes).
        # This will allow a margin of a couple months in case the system time is incorrect
        # or the board is dated a bit into the future.
        if now - self._timestamp_from_minutes(minutes) > timedelta(days=31*365):
            minutes_ext = minutes + self._time_rollover_limit
            min_str = self._timestamp_from_minutes(minutes).isoformat()
            min_ext_str = self._timestamp_from_minutes(minutes_ext).isoformat()
            warn_str = f'BoardInfo.mfg_date_time: possible Y2K27 rollover detected; timestamp bumped to {min_ext_str} - original timestamp was {min_str}'
            logging.warning(warn_str)
            frugy.fru.import_log(warn_str)
            return minutes_ext
        return minutes

    def _set_mfg_date_time(self, timestamp):
        if timestamp is not None:
            if type(timestamp) == str:
                timestamp = datetime.fromisoformat(timestamp)
            minutes = self._timestamp_to_minutes(timestamp)
            minutes = self._handle_y2k27_rollover_yaml2bin(minutes)
            self._set('mfg_date_time', minutes)
        else:
            self._set('mfg_date_time', 0)

    def _get_mfg_date_time(self):
        minutes = self._get('mfg_date_time')
        if minutes != 0:
            minutes = self._handle_y2k27_rollover_bin2yaml(minutes, datetime.now())
            return self._timestamp_from_minutes(minutes)
        else:
            return None


@ipmi_area
class ProductInfo(FruAreaSized):
    ''' Platform Management FRU Information Storage Definition, Table 12-1 '''

    _schema = [
        ('language_code', FixedField, 'u8', {
         'default': _default_language_code}),
        ('manufacturer', StringField),
        ('product_name', StringField),
        ('part_number', StringField),
        ('version', StringField),
        ('serial_number', StringField),
        ('asset_tag', StringField),
        ('fru_file_id', StringField),
        ('custom_info_fields', CustomStringArray),
    ]
