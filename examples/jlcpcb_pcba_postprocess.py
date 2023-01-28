import argparse
import csv
from typing import Dict

parser = argparse.ArgumentParser(description='Post-process KiCad BoM and position files to be compatible with JLC.')
parser.add_argument('file_path_prefix', type=str,
                    help='Path prefix to the part data, without the .csv or -top-post.csv postfix, ' +
                         'for example test_ledmatrix/gerbers/LedMatrixTest')
args = parser.parse_args()


# Correct the rotations on a per-part-number-basis
PART_ROTATIONS = {
  'C87911': 180,  # USB ESD diode
  'C165948': 0,  # USB C connector
  'C86781': 180,  # LD1117
  'C134077': 180,  # LD1117
  'C425057': -90,  # resistor array 750ohm 4x0603
  'C20197': -90,  # resistor array 1k 4x0603
  'C8734': -90,  # STM32F103C8T6
  'C91199': 180,  # VL53L0X
  'C27396': -90,  # TPA2005D1
  'C12084': -90,  # SN65HVD230DR
  'C264517': 90,  # 0606 RGB LED
  'C86832': -90,  # PCF8574 IO expander
  'C500769': -90,  # AP3418 buck converter
  'C50506': -90,  # DRV8833 dual motor driver
  'C701342': -90,  # ESP32
  'C7972': 180,  # LMV opamp
  'C92482': -90,  # DRV8313 BLDC driver
  'C132291': -90,  # FUSB302B
  'C508453': 180,  # FET

  'C508461': -90,  # SOIC-8 FET
  'C112032': 180,  # LDO
  'C413500': -90,  # SOIC-8 gate driver
  'C476470': -90,  # SOIC-8 digital isolator
  'C460356': 180,  # SOT-23-5 boost converter
  'C97521': -90,  # SOIC-8 SPI Flash
  'C2962219': -90,  # 2x5 1.27mm header shrouded
  'C126830': 90,  # "SOT-23" USB ESD protector
  'C6568': -90,  # CP2102 USB UART
  'C155612': 180,  # SOT-223 1.2v reg
  'C190271': 180,  # SOT-23-6 93LC56 EEPROM
  'C976032': -90,  # QMC3883L
}

if __name__ == '__main__':
  def remap_by_dict(elt: str, remap_dict: Dict[str, str]) -> str:
    if elt in remap_dict:
      return remap_dict[elt]
    else:
      return elt

  refdes_lcsc_map: Dict[str, str] = {}  # refdes -> LCSC part number

  # while we don't need to modify this file, we do need the JLC P/N to refdes map
  # to apply the rotations, since that data isn't in the placement file
  with open(f'{args.file_path_prefix}.csv', 'r', newline='') as bom_in:
    csv_in = csv.reader(bom_in)

    rows = list(csv_in)
    refdes_list_index = rows[0].index('Designator')
    lcsc_index = rows[0].index('JLCPCB Part #')

    for i, row in enumerate(rows[1:]):
      if not row[lcsc_index]:  # ignore rows without part number
        continue
      refdes_list = row[refdes_list_index].split(',')
      for refdes in refdes_list:
        assert refdes not in refdes_lcsc_map, f"duplicate refdes {refdes} in row {i+1}"
        refdes_lcsc_map[refdes] = row[lcsc_index]

  print(f"read {args.file_path_prefix}.csv")

  # Process position CSV
  POS_HEADER_MAP = {
    'Ref': 'Designator',
    'PosX': 'Mid X',
    'PosY': 'Mid Y',
    'Rot': 'Rotation',
    'Side': 'Layer',
  }
  for pos_postfix in ['top', 'bottom']:
    with open(f'{args.file_path_prefix}-{pos_postfix}-pos.csv', 'r', newline='') as pos_in, \
        open(f'{args.file_path_prefix}-{pos_postfix}-pos_jlc.csv', 'w', newline='') as pos_out:
      csv_in = csv.reader(pos_in)
      csv_out = csv.writer(pos_out)

      rows = list(csv_in)
      rows[0] = [remap_by_dict(elt, POS_HEADER_MAP) for elt in rows[0]]

      refdes_index = rows[0].index('Designator')
      rot_index = rows[0].index('Rotation')

      csv_out.writerow(rows[0])

      for i, row in enumerate(rows[1:]):
        refdes = row[refdes_index]
        lcsc_opt = refdes_lcsc_map.get(refdes, None)
        if lcsc_opt is not None and lcsc_opt in PART_ROTATIONS:
          row[rot_index] = str((float(row[rot_index]) + PART_ROTATIONS[lcsc_opt]) % 360)
          print(f"correct rotation for row {i+1} ref {refdes}, {lcsc_opt}")
        csv_out.writerow(row)

    print(f"wrote {args.file_path_prefix}-{pos_postfix}-pos_jlc.csv")
