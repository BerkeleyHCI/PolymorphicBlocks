import argparse
from typing import Dict, List

import sexpdata

from electronics_model.KiCadSchematicParser import group_by_car, parse_symbol, test_cast

if __name__ == '__main__':
  parser = argparse.ArgumentParser(description='Update timestamps on a kicad_pcb file from a new netlist.' +
                                   ' This is only used to upgrade a KiCad 5 PCB for use in KiCad 6,' +
                                   ' since KiCad 6 does not support non-numeric timestamps which netlists used to use.')
  parser.add_argument('input_pcb', type=argparse.FileType('r'))
  parser.add_argument('input_netlist', type=argparse.FileType('r'))
  parser.add_argument('output_pcb', type=argparse.FileType('w'))
  args = parser.parse_args()

  # build pathname -> new timestamp mapping
  path_timestamp_map: Dict[str, str] = {}

  net_sexp = sexpdata.loads(args.input_netlist.read())
  assert parse_symbol(net_sexp[0]) == 'export'
  net_dict = group_by_car(net_sexp)

  net_components = net_dict['components']
  assert len(net_components) == 1
  for elt in net_components[0][1:]:
    assert parse_symbol(elt[0]) == 'comp'
    elt_dict = group_by_car(elt)
    tstamp = elt_dict['tstamps'][0][1]
    props = {test_cast(prop[1][1], str): test_cast(prop[2][1], str)
             for prop in elt_dict.get('property', [])}
    path = props['edg_short_path']
    path_timestamp_map['/' + path.replace('.', '/')] = tstamp

  pcb_sexp = sexpdata.loads(args.input_pcb.read())
  assert parse_symbol(pcb_sexp[0]) == 'kicad_pcb'
  pcb_dict = group_by_car(pcb_sexp)  # shares internal references w/ pcb_sexp

  net_unseen_paths: List[str] = list(path_timestamp_map.keys())
  pcb_unmapped_paths: List[str] = []
  for elt in pcb_dict['module']:
    elt_dict = group_by_car(elt)
    tstamp = elt_dict['tstamp'][0][1]
    path = parse_symbol(elt_dict['path'][0][1])

    if path in path_timestamp_map:
      net_unseen_paths.remove(path)
      new_tstamp = path_timestamp_map[path]
      elt_dict['tstamp'][0][1] = new_tstamp
      print(f"Map: {tstamp}, {path} => {new_tstamp}")
    else:
      pcb_unmapped_paths.append(path)

  print(f"Netlist unseen paths: {net_unseen_paths}")
  print(f"PCB unmapped paths: {pcb_unmapped_paths}")

  args.output_pcb.write(sexpdata.dumps(pcb_sexp))
  print("Wrote PCB")
