# frugy - FRU Generator YAML

This is a tool which generates EEPROM images according to the [IPMI](https://www.intel.com/content/www/us/en/products/docs/servers/ipmi/ipmi-second-gen-interface-spec-v2-rev1-1.html) [FRU](https://www.intel.com/content/dam/www/public/us/en/documents/specification-updates/ipmi-platform-mgt-fru-info-storage-def-v1-0-rev-1-3-spec-update.pdf) standard from [YAML](https://yaml.org/spec/1.2/spec.html) configuration files. It can also parse a FRU EEPROM image and write its contents to a YAML file, or dump them to stdout.

## Installation

```
pip3 install git+https://msktechvcs.desy.de/techlab/tools/frugy.git
```

## Usage

```
$ frugy --help
usage: frugy [-h] [-v] [-o OUTPUT] [-w] [-r] [-e EEPROM_SIZE] [-d] srcfile

FRU Generator YAML

positional arguments:
  srcfile               Source file for reading

optional arguments:
  -h, --help            show this help message and exit
  -v, --version         show program's version number and exit
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
```

## Examples

```
frugy damc-fmc2zup.yml
```
Generate FRU image `damc-fmc2zup.bin` from `damc-fmc2zup.yml` configuration file.

```
frugy damc-fmc2zup.yml -o fmc2zup_fru_eeprom.bin -e 2048
```
Generate `fmc2zup_fru_eeprom.bin` from `damc-fmc2zup.yml` configuration, make it 2048 byte long (pad with 0xff).

```
frugy damc-fmc2zup.bin -r
```
Read and parse FRU image `damc-fmc2zup.bin`, generate `damc-fmc2zup.yml` from it.

```
frugy dmmc-stamp.yml -s BoardInfo.board_serial_number=Rev.A -s ProductInfo.product_version=0.01-alpha -t
```
Generate `dmmc-stamp.bin`, setting `board_serial_number` to *REV_A*, `product_version` to *0.01-alpha* and `mfg_date_time` to current UTC time.

## Supported FRU records

Supported FRU areas from IPMI standard:
* CommonHeader
* ChassisInfo
* BoardInfo
* ProductInfo
* Multirecord

Supported multirecords from IPMI standard:
* DCOutput
* DCLoad

Supported multirecords from PICMG AMC.0 standard:
* ModuleCurrentRequirements
* PointToPointConnectivity

Supported multirecords from ANSI/VITA 57.1 FMC standard:
* FmcMainDefinition

## Example configuration file

```
BoardInfo:
  board_manufacturer: DESY
  board_product_name: DMMC-STAMP Rev.A
  board_serial_number: '0000'
  board_part_number: '0000'
  fru_file_id: none
ProductInfo:
  manufacturer_name: DESY
  product_name: DMMC-STAMP Rev.A
  product_part_number: '0000'
  product_version: '0000'
  product_serial_number: '0000'
  asset_tag: none
  fru_file_id: none
MultirecordArea:
- type: ModuleCurrentRequirements
  current_draw: 6.5
```

More example configurations can be found in the `examples` folder.
