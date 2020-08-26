from frugy.areas import CommonHeader, ChassisInfo, BoardInfo, ProductInfo
import yaml

class Fru:
    def __init__(self, initdict=None):
        self.header = CommonHeader()
        self.areas = {}
        if initdict is not None:
            self.update(initdict)

    def factory(self, cls_name, cls_args):
        map = {
            'ChassisInfo': ChassisInfo,
            'BoardInfo': BoardInfo,
            'ProductInfo': ProductInfo
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
        self.header.update({k: 0 for k in [
            'internal_use_offs',
            'chassis_info_offs',
            'board_info_offs',
            'product_info_offs',
            'multirecord_offs'
        ]})
        area_table = (('ChassisInfo', 'chassis_info_offs'),
                      ('BoardInfo', 'board_info_offs'),
                      ('ProductInfo', 'product_info_offs'))

        # Determine offsets for areas
        curr_offs = self.header.size_total()
        for area, offs in area_table:
            if area in self.areas:
                self.header[offs] = curr_offs
                curr_offs += self.areas[area].size_total()

        # Serialize everything
        result = self.header.serialize()
        for area, _ in area_table:
            if area in self.areas:
                result += self.areas[area].serialize()

        return result


    def load_yaml(self, fname):
        with open(fname, 'r') as infile:
            fru_dict = yaml.load(infile)
        self.update(fru_dict)
    
    def save_yaml(self, fname):
        with open(fname, 'w') as outfile:
            yaml.dump(self.to_dict(), outfile, default_flow_style=False)

    def load_bin(self, fname):
        with open(fname, 'rb') as infile:
            print('not implemented yet :-(')

    def save_bin(self, fname):
        with open(fname, 'wb') as outfile:
            outfile.write(self.serialize())
