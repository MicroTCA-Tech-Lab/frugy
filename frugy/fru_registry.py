from enum import Enum, auto
from bidict import bidict
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

_lookup_by_id = defaultdict(bidict)


def rec_register(cls, rec_type: FruRecordType, rec_id=None):
    ''' Register FRU record type in central registry and lookup table '''
    _registry[rec_type].append(cls)
    if rec_id is not None:
        _lookup_by_id[rec_type][rec_id] = cls


def rec_enumerate(rec_type_filter = None):
    ''' Enumerate registered FRU records, filter if rec_type_filter given '''
    if rec_type_filter is None:
        rec_type_filter = list(FruRecordType)
    elif type(rec_type_filter) is not list:
        rec_type_filter = [rec_type_filter]
    
    result = [_registry[rec_type] for rec_type in rec_type_filter]

    return list(chain.from_iterable(result))


def rec_lookup_class(rec_type: FruRecordType, rec_id: int):
    ''' Lookup record class by ID '''
    return _lookup_by_id[rec_type][rec_id]


def rec_lookup_id(rec_type: FruRecordType, rec):
    ''' Lookup record ID by class '''
    return _lookup_by_id[rec_type].inverse[rec]
