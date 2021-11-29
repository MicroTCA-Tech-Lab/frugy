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

from enum import Enum, auto
from collections import defaultdict
from itertools import chain


class FruRecordType(Enum):
    ipmi_area = auto()
    ipmi_multirecord = auto()
    picmg_multirecord = auto()
    picmg_secondary = auto()
    fmc_multirecord = auto()
    fmc_secondary = auto()


_registry = defaultdict(list)

_lookup_by_id = defaultdict(dict)
_lookup_by_name = {}


def rec_register(cls, rec_type: FruRecordType, rec_id=None):
    ''' Register FRU record type in central registry and lookup table '''
    _registry[rec_type].append(cls)
    _lookup_by_name[cls.__name__] = cls
    if rec_id is not None:
        _lookup_by_id[rec_type][rec_id] = cls


def rec_enumerate(rec_type_filter=None):
    ''' Enumerate registered FRU records, filter if rec_type_filter given '''
    if rec_type_filter is None:
        rec_type_filter = list(FruRecordType)
    elif type(rec_type_filter) is not list:
        rec_type_filter = [rec_type_filter]

    result = [_registry[rec_type] for rec_type in rec_type_filter]

    return list(chain.from_iterable(result))


def rec_lookup_by_id(rec_type: FruRecordType, rec_id: int):
    ''' Lookup record class by record type and ID '''
    return _lookup_by_id[rec_type][rec_id]


def rec_lookup_by_name(rec_name: str):
    ''' Lookup record class by name '''
    return _lookup_by_name[rec_name]


def rec_info(rec):
    ''' return: record name, record information(docstring) '''
    return rec.__name__, str(rec.__doc__).strip()


def schema_entry_info(entry):
    ''' return schema entry name, type, options (e.g. constants) '''
    e_name = entry[0]
    e_inst = entry[1]._shortname
    if e_inst == 'array':
        e_args = f'({entry[2].__name__})'
    else:
        e_args = f'({entry[2]})' if len(
            entry) > 2 and entry[2] is not None else ''
    e_opt = None
    if len(entry) > 3:
        e_opt = entry[3]

    e_type = f'{e_inst} {e_args}'

    return e_name, e_type, e_opt
