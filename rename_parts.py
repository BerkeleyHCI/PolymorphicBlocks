import argparse
from typing import Dict, List
import sexpdata  # type: ignore

# this script must be placed and run in the project root directory, not within the examples folder
# otherwise, this import fails since the root path is incorrect
from electronics_model.KiCadSchematicParser import group_by_car, parse_symbol, test_cast


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
        fp_text[2] = 'ducks'

  modified_string = sexpdata.dumps(pcb_sexp)
  # sexpdata doesn't insert newlines, and KiCad chokes when there's one long line
  modified_string = modified_string.replace('))', '))\n')
  args.output_pcb.write(modified_string)
  print("Wrote PCB")
