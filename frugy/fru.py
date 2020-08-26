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

    def load_yaml(self, fname):
        with open(fname, 'r') as infile:
            fru_dict = yaml.load(infile)
        self.update(fru_dict)
    
    def save_yaml(self, fname):
        with open(fname, 'w') as outfile:
            yaml.dump(self.to_dict(), outfile)

    def to_dict(self):
        return {k: v.to_dict() for k, v in self.areas.items()}

    def __repr__(self):
        return repr(self.to_dict())
