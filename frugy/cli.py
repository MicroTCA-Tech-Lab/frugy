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

import argparse
import os
import sys
import yaml
from datetime import datetime
import logging

from frugy.__init__ import __version__
from frugy.fru import Fru
from frugy.fru_registry import FruRecordType, rec_enumerate, rec_lookup_by_name, rec_info, schema_entry_info
from frugy.types import FruAreaChecksummed
from frugy.multirecords import MultirecordEntry


def list_supported_records():
    width = 108
    separator = '+' + '-' * (width-2) + '+'
    lf = f"|".ljust(width-1) + '|'
    print(separator)
    for rec_type in list(FruRecordType):
        rec_list = rec_enumerate(rec_type)
        if len(rec_list) != 0:
            print(lf)
            print(f'| type: {rec_type.name}'.ljust(width-1) + '|')
            print(lf)
            for r in rec_list:
                name, doc = rec_info(r)
                print(f'| {name.ljust(33)} {doc}'.ljust(width-1) + '|')
            print(lf)
            print(separator)


def list_record_schema(rec_name):
    schema = rec_lookup_by_name(rec_name)._schema
    print(f'{"Name".ljust(20)} {"Type".ljust(30)} {"Opt"}')

    for entry in schema:
        e_name, e_type, e_opt = schema_entry_info(entry)
        if e_name.startswith('_'):
            continue
        if e_opt is not None and 'constants' in e_opt:
            e_opt = ', '.join(k for k in e_opt['constants'].keys())
        else:
            e_opt = ''
        print(f'{e_name.ljust(20)} {e_type.ljust(30)} {e_opt}')


def writer(fname, content, bin_mode=False):
    if fname != '-':
        with open(fname, 'wb' if bin_mode else 'w') as f:
            f.write(content)
    else:
        if bin_mode:
            os.write(sys.stdout.fileno(), content)
        else:
            sys.stdout.write(content)


def dict_set(d, keys, item):
    if len(keys) > 1:
        key, rest = keys[0], keys[1:]
        if key not in d:
            d[key] = {}
        dict_set(d[key], rest, item)
    else:
        d[keys[0]] = item


def main():
    parser = argparse.ArgumentParser(
        description='FRU Generator YAML'
    )
    parser.add_argument('srcfile',
                        type=str,
                        nargs='?',
                        help='Source file for reading'
                        )
    parser.add_argument('--version',
                        action='version',
                        version='%(prog)s ' + __version__
                        )
    parser.add_argument('-o', '--output',
                        type=str,
                        help='output file (derived from input file if not set)'
                        )
    parser.add_argument('-w', '--write',
                        action='store_true',
                        help='FRU write mode (convert YAML to FRU image), default'
                        )
    parser.add_argument('-r', '--read',
                        action='store_true',
                        help='FRU read mode (convert FRU image to YAML)'
                        )
    parser.add_argument('-d', '--dump',
                        action='store_true',
                        help='dump FRU information to stdout (same as -r -o -)'
                        )
    parser.add_argument('-e', '--eeprom-size',
                        type=int,
                        help='pad FRU image to match EEPROM size in bytes (only valid in write mode)'
                        )
    parser.add_argument('-s', '--set',
                        type=str,
                        action='append',
                        help='set FRU record field to a value (only valid in write mode)'
                        )
    parser.add_argument('-t', '--timestamp',
                        action='store_true',
                        help='set BoardInfo.mfg_date_time timestamp to current UTC time (only valid in write mode)'
                        )
    parser.add_argument('-b', '--broken',
                        action='store_true',
                        help='enable workaround to parse Opal Kelly EEPROMs'
                        )
    parser.add_argument('-c', '--ignore-checksum-errors',
                        action='store_true',
                        help='ignore checksum errors when parsing a FRU image'
                        )
    parser.add_argument('-l', '--list',
                        type=str,
                        default=None,
                        const='',
                        nargs='?',
                        help='list supported FRU records or schema of specified record'
                        )
    parser.add_argument('-v', '--verbosity',
                        type=int,
                        help='set verbosity (0=quiet, 1=info, 2=debug)'
                        )
    args = parser.parse_args()

    verbosity = args.verbosity if args.verbosity is not None else 0
    logging.basicConfig(
        format='%(levelname)7s: %(message)s',
        level=[logging.WARNING, logging.INFO, logging.DEBUG][verbosity]
    )

    if args.list is not None:
        if args.list == '':
            list_supported_records()
        else:
            list_record_schema(args.list)
        sys.exit(0)

    if args.srcfile is None:
        parser.print_help(sys.stderr)
        sys.exit(1)

    read_mode = args.read or args.dump
    if args.write and args.read:
        parser.print_help(sys.stderr)
        sys.exit(1)

    if read_mode and (args.eeprom_size is not None or args.set or args.timestamp):
        parser.print_help(sys.stderr)
        sys.exit(1)

    if read_mode and args.broken:
        MultirecordEntry.opalkelly_workaround_enabled = True

    if read_mode and args.ignore_checksum_errors:
        FruAreaChecksummed.ignore_checksum_errors = True

    outfile = args.output
    if args.dump:
        if outfile:
            parser.print_help(sys.stderr)
            sys.exit(1)
        outfile = '-'

    basename, ext = os.path.splitext(os.path.basename(args.srcfile))

    if read_mode and ext != '.bin':
        print('Cowardly refusing to read a FRU file not ending with .bin',
              file=sys.stderr)
        sys.exit(1)
    if not read_mode and ext != '.yml' and ext != '.yaml':
        print('Cowardly refusing to read a YAML file not ending with .yaml or .yml', file=sys.stderr)
        sys.exit(1)

    if not outfile:
        basename, _ = os.path.splitext(os.path.basename(args.srcfile))
        outfile = basename + ('.yml' if read_mode else '.bin')

    fru = Fru()

    if read_mode:
        try:
            fru.load_bin(args.srcfile)
            writer(outfile, fru.dump_yaml())
        except RuntimeError as e:
            print(f'Error while parsing or writing: {e}')
            return False
    else:
        with open(args.srcfile, 'r') as infile:
            fru_dict = yaml.safe_load(infile)

        if args.set is not None:
            for s in args.set:
                k, v = s.split('=')
                key_path = k.split('.')
                if len(key_path) > 1:
                    # Traverse hierarchy of selected key_path e.g. ['BoardInfo', 'serial_number']
                    dict_set(fru_dict, key_path, v)
                else:
                    # Set property e.g 'serial_number' of all first level records (e.g. 'BoardInfo', 'ProductInfo')
                    key = key_path[0]
                    for k in fru_dict.keys():
                        if key in fru_dict[k]:
                            fru_dict[k][key] = v

        if args.timestamp:
            if 'BoardInfo' in fru_dict:
                fru_dict['BoardInfo']['mfg_date_time'] = datetime.utcnow()
            else:
                print(
                    'Error: FRU needs BoardInfo area to carry the timestamp', file=sys.stderr)
                sys.exit(1)

        fru.update(fru_dict)
        img = fru.serialize()
        if args.eeprom_size is not None:
            if len(img) <= args.eeprom_size:
                img += b'\xff' * (args.eeprom_size - len(img))
            else:
                print(
                    f'Error: Image size ({len(img)}) exceeds EEPROM size ({args.eeprom_size})', file=sys.stderr)
                sys.exit(1)
        writer(outfile, img, bin_mode=True)


if __name__ == '__main__':
    main()
