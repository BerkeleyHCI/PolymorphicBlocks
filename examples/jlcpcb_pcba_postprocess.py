import argparse
import csv
import math
from typing import Dict, Tuple

parser = argparse.ArgumentParser(description='Post-process KiCad BoM and position files to be compatible with JLC.')
parser.add_argument('file_path_prefix', type=str,
                    help='Path prefix to the part data, without the .csv or -top-post.csv postfix, ' +
                         'for example LedMatrix/gerbers/LedMatrix')
args = parser.parse_args()


# Correct the rotations on a per-part-number-basis
PART_ROTATIONS = {
  'C425057': -90,  # resistor array 750ohm 4x0603
  'C20197': -90,  # resistor array 1k 4x0603
  'C8734': -90,  # STM32F103C8T6
  'C432211': 90,  # STM32G031GBU6
  'C91199': 180,  # VL53L0X
  'C27396': -90,  # TPA2005D1
  'C12084': -90,  # SN65HVD230DR
  'C264517': 180,  # 0606 RGB LED
  'C158099': 90,  # 0404 RGB LED
  'C86832': -90,  # PCF8574 IO expander
  'C500769': -90,  # AP3418 buck converter
  'C50506': -90,  # DRV8833 dual motor driver
  'C92482': -90,  # DRV8313 BLDC driver
  'C132291': -90,  # FUSB302B
  'C508453': 180,  # FET
  'C527684': -90,  # TPS54202H SOT-23-6
  'C155534': -90,  # AL8861 MSOP-8
  'C7722': -90,  # TPS61040 SOT-23-5
  'C216623': 0,  # XC6209 1.5 SOT-23-5
  'C216624': 0,  # XC6209 3.3 SOT-23-5
  'C222571': 0,  # XC6209 5.0 SOT-23-5
  'C86803': -90,  # PCA9554A TSSOP16
  'C106912': -90,  # NLAS4157
  'C3663690': 180,  # TMP1075N
  'C70285': 180,  # SN74LVC1G74DCUR
  'C2651906': 0,  # DG468
  'C840095': 0,  # LM2664 SOT-23-6

  'C2962219': -90,  # 2x5 1.27mm header shrouded
  'C126830': 90,  # "SOT-23" USB ESD protector
  'C6568': -90,  # CP2102 USB UART
  'C976032': -90,  # LGA-16 QMC5883L

  'C650309': -90,  # AD5941

  'C424093': -90,  # MCP73831T
  'C842287': -90,  # 74AHCT1G125
  'C113367': -90,  # PAM8302
  'C2890035': -90,  # SK6805-EC15
  'C125972': 90,  # BME680
  'C2682619': 180,  # MAX98357 BGA
  'C910544': -90,  # MAX98357 QFN

  'C262645': 180,  # AFC07 FPC 30
  'C262669': 180,  # AFC01 FPC 24

  'C424662': -90,  # FH35C 0.3mm FPC 31

  'C209762': -90,  # EC11J15

  'C585350': 180,  # Molex microSD 104031-0811
}

_FOOTPRINT_ROTATIONS = {
  'Connector_USB:USB_C_Receptacle_XKB_U262-16XN-4BVC11': 0,
  'RF_Module:ESP32-WROOM-32': -90,
  'Package_TO_SOT_SMD:SOT-23': 180,
  'Package_TO_SOT_SMD:SOT-23-5': 180,
  'Package_TO_SOT_SMD:SOT-23-6': 180,
  'Package_TO_SOT_SMD:SOT-89-3': 180,
  'Package_TO_SOT_SMD:SOT-323_SC-70': 180,
  'Package_TO_SOT_SMD:SOT-223-3_TabPin2': 180,
  'Package_TO_SOT_SMD:TO-252-2': 180,
  'Package_SO:SOIC-8_3.9x4.9mm_P1.27mm': -90,
  'Package_SO:SOIC-8_5.23x5.23mm_P1.27mm': -90,
  'Package_DFN_QFN:UDFN-4-1EP_1x1mm_P0.65mm_EP0.48x0.48mm': -90,

  'OptoDevice:Osram_BPW34S-SMD': 180,

  'Connector_Coaxial:BNC_Amphenol_B6252HB-NPP3G-50_Horizontal': 180,

  'Connector_JST:JST_PH_S2B-PH-K_1x02_P2.00mm_Horizontal': 180,

  'Capacitor_SMD:CP_Elec_3x5.3': 180,
  'Capacitor_SMD:CP_Elec_3x5.4': 180,
  'Capacitor_SMD:CP_Elec_4x3': 180,
  'Capacitor_SMD:CP_Elec_4x3.9': 180,
  'Capacitor_SMD:CP_Elec_4x4.5': 180,
  'Capacitor_SMD:CP_Elec_4x5.3': 180,
  'Capacitor_SMD:CP_Elec_4x5.4': 180,
  'Capacitor_SMD:CP_Elec_4x5.7': 180,
  'Capacitor_SMD:CP_Elec_4x5.8': 180,
  'Capacitor_SMD:CP_Elec_5x3': 180,
  'Capacitor_SMD:CP_Elec_5x3.9': 180,
  'Capacitor_SMD:CP_Elec_5x4.4': 180,
  'Capacitor_SMD:CP_Elec_5x4.5': 180,
  'Capacitor_SMD:CP_Elec_5x5.3': 180,
  'Capacitor_SMD:CP_Elec_5x5.4': 180,
  'Capacitor_SMD:CP_Elec_5x5.7': 180,
  'Capacitor_SMD:CP_Elec_5x5.8': 180,
  'Capacitor_SMD:CP_Elec_5x5.9': 180,
  'Capacitor_SMD:CP_Elec_6.3x3': 180,
  'Capacitor_SMD:CP_Elec_6.3x3.9': 180,
  'Capacitor_SMD:CP_Elec_6.3x4.5': 180,
  'Capacitor_SMD:CP_Elec_6.3x4.9': 180,
  'Capacitor_SMD:CP_Elec_6.3x5.2': 180,
  'Capacitor_SMD:CP_Elec_6.3x5.3': 180,
  'Capacitor_SMD:CP_Elec_6.3x5.4': 180,
  'Capacitor_SMD:CP_Elec_6.3x5.7': 180,
  'Capacitor_SMD:CP_Elec_6.3x5.8': 180,
  'Capacitor_SMD:CP_Elec_6.3x5.9': 180,
  'Capacitor_SMD:CP_Elec_6.3x7.7': 180,
  'Capacitor_SMD:CP_Elec_6.3x9.9': 180,
  'Capacitor_SMD:CP_Elec_8x5.4': 180,
  'Capacitor_SMD:CP_Elec_8x6.2': 180,
  'Capacitor_SMD:CP_Elec_8x6.5': 180,
  'Capacitor_SMD:CP_Elec_8x6.7': 180,
  'Capacitor_SMD:CP_Elec_8x6.9': 180,
  'Capacitor_SMD:CP_Elec_8x10': 180,
  'Capacitor_SMD:CP_Elec_8x10.5': 180,
  'Capacitor_SMD:CP_Elec_8x11.9': 180,
  'Capacitor_SMD:CP_Elec_10x7.7': 180,
  'Capacitor_SMD:CP_Elec_10x7.9': 180,
  'Capacitor_SMD:CP_Elec_10x10': 180,
  'Capacitor_SMD:CP_Elec_10x10.5': 180,
  'Capacitor_SMD:CP_Elec_10x12.5': 180,
  'Capacitor_SMD:CP_Elec_10x12.6': 180,
  'Capacitor_SMD:CP_Elec_10x14.3': 180,
  'Capacitor_SMD:CP_Elec_16x17.5': 180,
  'Capacitor_SMD:CP_Elec_16x22': 180,
  'Capacitor_SMD:CP_Elec_18x7.5': 180,
  'Capacitor_SMD:CP_Elec_18x22': 180,
}

# footprint position export doesn't include the footprint library name
PACKAGE_ROTATIONS = {footprint.split(':')[-1]: rot for footprint, rot in _FOOTPRINT_ROTATIONS.items()}

# translational offsets using KiCad coordinate conventions, -y is up
# offsets estimated visually
PART_OFFSETS: Dict[str, Tuple[float, float]] = {
  'C262669': (0, -0.5),  # AFC01 FPC 24
  'C262671': (0, -0.5),  # AFC01 FPC 30
  'C262643': (0, -1),  # AFC07 FPC 24
  'C262645': (0, -1),  # AFC07 FPC 30
  'C110293': (0, 0.1),  # SKRTLAE010 R/A switch
  'C116648': (0, 2.1),  # EC05E1220401

  'C496552': (-0.3, 0),  # BWIPX-1-001E U.FL connector
}
_FOOTPRINT_OFFSETS: Dict[str, Tuple[float, float]] = {
  'Package_TO_SOT_SMD:SOT-89-3': (-0.6, 0),
  'Package_TO_SOT_SMD:TO-252-2': (-2, 0),

  'Connector_USB:USB_C_Receptacle_XKB_U262-16XN-4BVC11': (0, -1.25),
  'RF_Module:ESP32-WROOM-32': (0, 0.8),

  'Connector_Coaxial:BNC_Amphenol_B6252HB-NPP3G-50_Horizontal': (0, -2.5),

  'Connector_JST:JST_PH_S2B-PH-K_1x02_P2.00mm_Horizontal': (1, 0),
  'Connector_JST:JST_PH_S6B-PH-K_1x06_P2.00mm_Horizontal': (5, 0),
}
PACKAGE_OFFSETS = {footprint.split(':')[-1]: offset for footprint, offset in _FOOTPRINT_OFFSETS.items()}

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
      package_index = rows[0].index('Package')
      rot_index = rows[0].index('Rotation')
      x_index = rows[0].index('Mid X')
      y_index = rows[0].index('Mid Y')

      csv_out.writerow(rows[0])

      for i, row in enumerate(rows[1:]):
        refdes = row[refdes_index]
        package = row[package_index]
        lcsc_opt = refdes_lcsc_map.get(refdes, None)

        # correct offsets before applying rotation
        if lcsc_opt is not None and lcsc_opt in PART_OFFSETS:
          (xoff, yoff) = PART_OFFSETS[lcsc_opt]
          rot = math.radians(float(row[rot_index]))
          row[x_index] = str((float(row[x_index]) + xoff * math.cos(rot) + yoff * math.sin(rot)))
          row[y_index] = str((float(row[y_index]) + xoff * math.sin(rot) - yoff * math.cos(rot)))
          print(f"correct offset for row {i+1} ref {refdes}, {lcsc_opt}")
        elif package in PACKAGE_OFFSETS:
          (xoff, yoff) = PACKAGE_OFFSETS[package]
          rot = math.radians(float(row[rot_index]))
          row[x_index] = str((float(row[x_index]) + xoff * math.cos(rot) + yoff * math.sin(rot)))
          row[y_index] = str((float(row[y_index]) + xoff * math.sin(rot) - yoff * math.cos(rot)))
          print(f"correct offset for row {i+1} ref {refdes}, {package}")

        if lcsc_opt is not None and lcsc_opt in PART_ROTATIONS:
          row[rot_index] = str((float(row[rot_index]) + PART_ROTATIONS[lcsc_opt]) % 360)
          print(f"correct rotation for row {i+1} ref {refdes}, {lcsc_opt}")
        elif package in PACKAGE_ROTATIONS:
          row[rot_index] = str((float(row[rot_index]) + PACKAGE_ROTATIONS[package]) % 360)
          print(f"correct rotation for row {i+1} ref {refdes}, {package}")

        csv_out.writerow(row)

    print(f"wrote {args.file_path_prefix}-{pos_postfix}-pos_jlc.csv")
