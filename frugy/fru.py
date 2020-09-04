"""
SPDX-License-Identifier: BSD-3-Clause
Copyright (c) 2020 Deutsches Elektronen-Synchrotron DESY.
See LICENSE.txt for license details.
"""

from frugy.areas import CommonHeader, ChassisInfo, BoardInfo, ProductInfo
from frugy.multirecords import MultirecordArea
import frugy.multirecords_ipmi
import frugy.multirecords_picmg
import frugy.multirecords_fmc
import yaml
from bidict import bidict

# YAML formatting helpers
class YamlFlowstyleList(list):
    pass

def yaml_flowstyle_list_rep(dumper, data):
    return dumper.represent_sequence(u'tag:yaml.org,2002:seq', data, flow_style=True)

yaml.add_representer(YamlFlowstyleList, yaml_flowstyle_list_rep)

class Fru:
    _area_table_lookup = bidict({
        'ChassisInfo': 'chassis_info_offs',
        'BoardInfo': 'board_info_offs',
        'ProductInfo': 'product_info_offs',
        'MultirecordArea': 'multirecord_offs',
    })

    def __init__(self, initdict=None):
        self.header = CommonHeader()
        self.areas = {}
        if initdict is not None:
            self.update(initdict)

    def factory(self, cls_name, cls_args=None):
        map = {
            'ChassisInfo': ChassisInfo,
            'BoardInfo': BoardInfo,
            'ProductInfo': ProductInfo,
            'MultirecordArea': MultirecordArea
        }
        if cls_name not in map:
            raise ValueError(f"unknown FRU area: {cls_name}")
        return map[cls_name](cls_args)

    def update(self, src):
        self.areas = {k: self.factory(k, src[k]) for k in src.keys()}

    def to_dict(self):
        return {k: v.to_dict() for k, v in self.areas.items()}

    def __repr__(self):
        return repr(self.to_dict())

    def serialize(self):
        self.header.reset()

        # Determine offsets for areas
        curr_offs = self.header.size_total()
        for area, offs in self._area_table_lookup.items():
            if area in self.areas:
                self.header[offs] = curr_offs
                curr_offs += self.areas[area].size_total()

        # Serialize everything
        result = self.header.serialize()
        for area in self._area_table_lookup.keys():
            if area in self.areas:
                result += self.areas[area].serialize()

        return result

    def deserialize(self, input):
        self.areas = {}
        self.header.deserialize(input)
        for k, v in self.header.to_dict().items():
            if v:
                obj_name = self._area_table_lookup.inverse[k]
                obj = self.factory(obj_name)
                obj.deserialize(input[v:])
                self.areas[obj_name] = obj

    def load_yaml(self, fname):
        with open(fname, 'r') as infile:
            fru_dict = yaml.safe_load(infile)
        self.update(fru_dict)

    def dump_yaml(self):
        def fmt_tree(part):
            ''' Set lists at edges of tree to YAML flow style '''
            if type(part) is list:
                if len(part) == 0:
                    return part, False
                part, edge_flags = zip(*[fmt_tree(elem) for elem in part])
                part = list(part)
                if all(edge_flags):
                    part = YamlFlowstyleList(part)
                return part, False
            elif type(part) is dict:
                part = { k: fmt_tree(part[k])[0] for k in part.keys() }
                return part, False
            elif type(part) is str:
                # don't collapse strings in YAML, for better readability
                return part, False
            else:
                # no dict list, or str ==> reached edge of tree
                return part, True

        yaml_dict = self.to_dict()
        yaml_dict, _ = fmt_tree(yaml_dict)
        return yaml.dump(yaml_dict, sort_keys=False)

    def save_yaml(self, fname):
        with open(fname, 'w') as outfile:
            outfile.write(self.dump_yaml())

    def load_bin(self, fname):
        with open(fname, 'rb') as infile:
            self.deserialize(infile.read())

    def save_bin(self, fname):
        with open(fname, 'wb') as outfile:
            outfile.write(self.serialize())
