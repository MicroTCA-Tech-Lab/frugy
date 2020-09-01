import argparse
import os
import sys

from frugy.__init__ import __version__
from frugy.fru import Fru

def main():
    parser = argparse.ArgumentParser(
        description='FRU Generator YAML'
    )
    parser.add_argument('srcfile', type=str, help='Source file for reading')
    parser.add_argument('-v', '--version', action='version', version='%(prog)s ' + __version__)
    parser.add_argument('-o', '--output', type=str, help='Output file (derived from input file if not set)')
    parser.add_argument('-w', '--write', action='store_true', help='FRU write mode (convert YAML to FRU record), default')
    parser.add_argument('-r', '--read', action='store_true', help='FRU read mode (convert FRU record to YAML)')
    args = parser.parse_args()

    if args.write and args.read:
        parser.print_help(sys.stderr)
        sys.exit(1)
    read_mode = args.read

    basename, ext = os.path.splitext(os.path.basename(args.srcfile))
    if read_mode and ext != '.bin':
        print('Cowardly refusing to read a FRU file not ending with .bin', file=sys.stderr)
        sys.exit(1)
    if not read_mode and ext != '.yml' and ext != '.yaml':
        print('Cowardly refusing to read a YAML file not ending with .yaml or .yml', file=sys.stderr)
        sys.exit(1)

    outfile = args.output
    if not outfile:
        basename, _ = os.path.splitext(os.path.basename(args.srcfile))
        outfile = basename + ('.yml' if read_mode else '.bin')

    fru = Fru()
    
    if read_mode:
        fru.load_bin(args.srcfile)
        fru.save_yaml(outfile)
    else:
        fru.load_yaml(args.srcfile)
        fru.save_bin(outfile)


if __name__ == '__main__':
    main()
