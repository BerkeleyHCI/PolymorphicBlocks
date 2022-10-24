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
}


if __name__ == '__main__':
  def remap_by_dict(elt: str, remap_dict: Dict[str, str]) -> str:
    if elt in remap_dict:
      return remap_dict[elt]
    else:
      return elt

  # Process the BoM
  BOM_HEADER_MAP = {
    'Designation': 'JLCPCB Part #',
  }
  with open(f'{args.file_path_prefix}.csv', 'r', newline='') as bom_in, \
      open(f'{args.file_path_prefix}_jlc.csv', 'w', newline='') as bom_out:
    csv_in = csv.reader(bom_in, delimiter=';')
    csv_out = csv.writer(bom_out)

    rows = list(csv_in)
    rows[0] = [remap_by_dict(elt, BOM_HEADER_MAP) for elt in rows[0]]

    for row in rows:
      csv_out.writerow(row)

  print(f"wrote {args.file_path_prefix}_jlc.csv")

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

      lcsc_index = rows[0].index('Val')
      rot_index = rows[0].index('Rotation')

      for i, row in enumerate(rows):
        if row[lcsc_index] in PART_ROTATIONS:
          row[rot_index] = str((float(row[rot_index]) + PART_ROTATIONS[row[lcsc_index]]) % 360)
          print(f"correct rotation for row {i}, {row[lcsc_index]}")
        csv_out.writerow(row)

    print(f"wrote {args.file_path_prefix}-{pos_postfix}-pos_jlc.csv")
