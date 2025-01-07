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

from frugy import __version__
from frugy.areas import CommonHeader, ChassisInfo, BoardInfo, ProductInfo
from frugy.multirecords import MultirecordArea
import frugy.multirecords_ipmi
import frugy.multirecords_picmg
import frugy.multirecords_fmc
import yaml
from bidict import bidict
import os
from copy import deepcopy


# YAML formatting helpers


class YamlFlowstyleList(list):
    pass


def yaml_flowstyle_list_rep(dumper, data):
    return dumper.represent_sequence(u'tag:yaml.org,2002:seq', data, flow_style=True)


yaml.add_representer(YamlFlowstyleList, yaml_flowstyle_list_rep)


def import_log(msg):
    if not hasattr(import_log, "str"):
        import_log.str = ''
    import_log.str += msg + '\n'


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
        self.comment = ''
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
        # Some constructors modify their arguments; make sure to leave the user-supplied initdict intact
        return map[cls_name](deepcopy(cls_args))

    def update(self, src):
        self.comment = ''
        self.areas = {k: self.factory(k, v) for k, v in src.items()}

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
        import_log.str = ''
        self.areas = {}
        self.header.deserialize(input)
        for k, v in self.header.to_dict().items():
            # Ignore "internal use area"
            # TODO: Support it as opaque byte array?
            if v and k != 'internal_use_offs':
                obj_name = self._area_table_lookup.inverse[k]
                obj = self.factory(obj_name)
                obj.deserialize(input[v:])
                self.areas[obj_name] = obj

    def load_yaml(self, fname):
        with open(fname, 'r') as infile:
            fru_dict = yaml.safe_load(infile)
        self.update(fru_dict)

    def dump_yaml_raw(self):
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
                part = {k: fmt_tree(part[k])[0] for k in part.keys()}
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

    def postprocess_yaml(self, data):
        result = ''
        if hasattr(import_log, 'str'):
            if len(import_log.str) != 0:
                import_log.str = '\n' + import_log.str
            for line in [self.comment, *import_log.str.splitlines()]:
                result += f'# {line}\n'
        line_prev = ''
        for line in data.splitlines():
            if line.endswith(':') and not line.startswith(' '):
                # add LF before entries on root level
                result += '\n'
            if line.startswith('- type:') and line_prev != 'MultirecordArea:':
                # add LF between multirecord entries
                result += '\n'
            result += line + '\n'
            line_prev = line
        return result

    def dump_yaml(self):
        yaml_raw = self.dump_yaml_raw()
        return self.postprocess_yaml(yaml_raw)

    def save_yaml(self, fname):
        with open(fname, 'w') as outfile:
            outfile.write(self.dump_yaml())

    def load_bin(self, fname):
        self.comment = f'created with frugy {__version__} from "{os.path.basename(fname)}"'
        with open(fname, 'rb') as infile:
            self.deserialize(infile.read())

    def save_bin(self, fname):
        with open(fname, 'wb') as outfile:
            outfile.write(self.serialize())
