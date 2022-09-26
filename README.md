# frugy - FRU Generator YAML

This is a tool which generates EEPROM images according to the [IPMI](https://www.intel.com/content/www/us/en/products/docs/servers/ipmi/ipmi-second-gen-interface-spec-v2-rev1-1.html) [FRU](https://www.intel.com/content/dam/www/public/us/en/documents/specification-updates/ipmi-platform-mgt-fru-info-storage-def-v1-0-rev-1-3-spec-update.pdf) standard from [YAML](https://yaml.org/spec/1.2/spec.html) configuration files. It can also parse a FRU EEPROM image and write its contents to a YAML file, or dump them to stdout.

## Installation

From [PyPI](https://pypi.org/project/frugy):
```
pip3 install frugy
```

From [GitHub](https://github.com/MicroTCA-Tech-Lab/frugy):
```
pip3 install git+https://github.com/MicroTCA-Tech-Lab/frugy
```

## Usage

```
$ frugy --help
usage: frugy [-h] [--version] [-o OUTPUT] [-w] [-r] [-d]
             [-e EEPROM_SIZE] [-s SET] [-t] [-b] [-c] [-l [LIST]]
             [-v VERBOSITY]
             [srcfile]

FRU Generator YAML

positional arguments:
  srcfile               Source file for reading

optional arguments:
  -h, --help            show this help message and exit
  --version             show program's version number and exit
  -o OUTPUT, --output OUTPUT
                        output file (derived from input file if not set)
  -w, --write           FRU write mode (convert YAML to FRU image), default
  -r, --read            FRU read mode (convert FRU image to YAML)
  -d, --dump            dump FRU information to stdout (same as -r -o -)
  -e EEPROM_SIZE, --eeprom-size EEPROM_SIZE
                        pad FRU image to match EEPROM size in bytes (only
                        valid in write mode)
  -s SET, --set SET     set FRU record field to a value (only valid in write
                        mode)
  -t, --timestamp       set BoardInfo.mfg_date_time timestamp to current UTC
                        time (only valid in write mode)
  -b, --broken          enable workaround to parse Opal Kelly EEPROMs
  -c, --ignore-checksum-errors
                        ignore checksum errors when parsing a FRU image
  -l [LIST], --list [LIST]
                        list supported FRU records or schema of specified
                        record
  -v VERBOSITY, --verbosity VERBOSITY
                        set verbosity (0=quiet, 1=info, 2=debug)
```

## Examples

```
frugy damc-fmc2zup.yml
```
Read `damc-fmc2zup.yml` configuration, generate FRU image `damc-fmc2zup.bin`.

```
frugy damc-fmc2zup.yml -o fmc2zup_fru_eeprom.bin -e 2048
```
Read `damc-fmc2zup.yml` configuration, generate `fmc2zup_fru_eeprom.bin`, make it 2048 bytes (pad with 0xff).

```
frugy damc-fmc2zup.bin -r
```
Read and parse FRU image `damc-fmc2zup.bin`, generate YAML file `damc-fmc2zup.yml`.

```
frugy dmmc-stamp.yml -s BoardInfo.serial_number=1234 -s ProductInfo.version=1.0 -t
```
Read `dmmc-stamp.yml`, generate FRU with `BoardInfo.serial_number` set to *1234*, `ProductInfo.version` to *1.0* and `BoardInfo.mfg_date_time` to current UTC time.

```
frugy dmmc-stamp.yml -s serial_number=1234 -t
```
Read `dmmc-stamp.yml`, generate FRU with `BoardInfo.serial_number` *and* `ProductInfo.serial_number` set to *1234* and `BoardInfo.mfg_date_time` to current UTC time.

```
frugy -l
```
Show list of all supported FRU records.

```
frugy -l PointToPointConnectivity
```
Show layout of the FRU record called 'PointToPointConnectivity'.

## Supported FRU records

* [Overview of supported records](docs/records.md)

### YAML keywords for supported FRU records

* [Detailed list of supported IPMI records](docs/ipmi.md)
* [Detailed list of supported PICMG records](docs/picmg.md)
* [Detailed list of supported FMC records](docs/fmc.md)

## Example configuration file

```yaml
BoardInfo:
  manufacturer: DESY
  product_name: DMMC-STAMP Rev.A
  serial_number: '0000'
  part_number: '0000'
  fru_file_id: none
ProductInfo:
  manufacturer: DESY
  product_name: DMMC-STAMP Rev.A
  part_number: '0000'
  version: '0000'
  serial_number: '0000'
  asset_tag: none
  fru_file_id: none
MultirecordArea:
- type: ModuleCurrentRequirements
  current_draw: 6.5
```

More example configurations are stored in the [`examples`](examples)
 folder.
