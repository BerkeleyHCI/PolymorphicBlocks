KEEP_CATEGORIES = [
  'Chip Resistor - Surface Mount',
  'Current Sense Resistors/Shunt Resistors',
  'Low Resistors & Current Sense Resistors - Surface Mount',
  'Resistor Networks & Arrays',
  'Through Hole Resistors',


  'Aluminum Electrolytic Capacitors - Leaded',
  'Aluminum Electrolytic Capacitors - SMD',
  'Multilayer Ceramic Capacitors MLCC - Leaded',
  'Multilayer Ceramic Capacitors MLCC - SMD/SMT',
  'Tantalum Capacitors',

  'Fuse Holders',
  'Fuses',
  'Resettable Fuses',

  'Crystals',
  'Pre-programmed Oscillators',
  'Oscillators',

  'Diodes - Fast Recovery Rectifiers',
  'Diodes - General Purpose',
  'Schottky Barrier Diodes (SBD)',
  'Switching Diode',

  'Zener Diodes',

  'Inductors (SMD)',
  'Power Inductors',
  'Through Hole Inductors',
  'Ferrite Beads',

  'Infrared (IR) LEDs',
  'Light Emitting Diodes (LED)',
  'Ultra Violet LEDs',

  'Bipolar Transistors - BJT',
  'MOSFETs',
]

MIN_STOCK = 100  # arbitrary cutoff to prune rare parts

FILE = 'JLCPCB SMT Parts Library(20220419).csv'

if __name__ == '__main__':
  # Not using a standard CSV parser to preserve the original formatting as much as possible
  with open(f'{FILE}', 'rb') as full_file, open(f'Pruned_{FILE}', 'wb') as out_file:
    header = full_file.readline()
    out_file.writelines([header])
    rows = str(header.decode('gb2312').strip()).split(',')
    CATEGORY_INDEX = rows.index('Second Category')
    STOCK_INDEX = -2  # hard-coded because str.split doesn't account for quoted elements

    wrote_lines = 0
    for i, line in enumerate(full_file.readlines()):
      values = str(line.decode('gb2312').strip()).split(',')
      if values[CATEGORY_INDEX] in KEEP_CATEGORIES and \
          values[STOCK_INDEX] and int(values[STOCK_INDEX]) >= MIN_STOCK:
        out_file.writelines([line])
        wrote_lines += 1

  print(f"read {i} lines, wrote {wrote_lines} lines")
