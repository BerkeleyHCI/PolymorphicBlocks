import argparse
import os, sys
from typing import List, Dict

import sexpdata  # type: ignore

sys.path.append(os.getcwd())  # allow electronics_model to be seen if run in root even if script isn't in root
from edg.electronics_model.KiCadSchematicParser import group_by_car, parse_symbol

# a quick'n'dirty script to rename refdeses in a KiCad PCB according to the remap table below
# used since SVG-PCB (currently) doesn't seem to have a way to programmatically generate refdes
# so when components are programmatically defined, they all have the same name

# defined as original name to list of renamed names, assigned in order
# (first component matching the original name takes the first name in the rename list,
# second takes the second name, and so on)
remap_table: Dict[str, List[str]] = {}
remap_table['led'] = []
remap_table['sw'] = []
for led in range(24):
  remap_table['led'].append(f'rgb_ring.led[{led}]')
for sw in range(6):
  remap_table['sw'].append(f'sw[{sw}]')
for sw in range(12):
  remap_table['led'].append(f'rgb_sw.led[{sw}]')

if __name__ == '__main__':
  parser = argparse.ArgumentParser(description='Rename refdeses in a PCB.')
  parser.add_argument('input_pcb', type=argparse.FileType('r'))
  parser.add_argument('output_pcb', type=argparse.FileType('w'))
  args = parser.parse_args()

  pcb_data = args.input_pcb.read()
  pcb_sexp = sexpdata.loads(pcb_data)
  assert parse_symbol(pcb_sexp[0]) == 'kicad_pcb'
  pcb_dict = group_by_car(pcb_sexp)
  for footprint in pcb_dict['footprint']:
    footprint_dict = group_by_car(footprint)
    for fp_text in footprint_dict['fp_text']:
      if fp_text[1] == sexpdata.Symbol('reference'):
        old_refdes = fp_text[2]
        if old_refdes in remap_table:
          remap_list = remap_table[old_refdes]
          if remap_list:
            fp_text[2] = remap_list.pop(0)
            print(f"rename {old_refdes} => {fp_text[2]}")
          else:
            print(f"rename {old_refdes} failed, empty list")

  modified_string = sexpdata.dumps(pcb_sexp)
  # sexpdata doesn't insert newlines, and KiCad chokes when there's one long line
  modified_string = modified_string.replace('))', '))\n')
  args.output_pcb.write(modified_string)
  print("Wrote PCB")
