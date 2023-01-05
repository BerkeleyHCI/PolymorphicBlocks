import argparse
import sexpdata

from electronics_model.KiCadSchematicParser import group_by_car, parse_symbol

parser = argparse.ArgumentParser(description='Update timestamps on a kicad_pcb file from a new netlist.' +
                                 ' This is only used to upgrade a KiCad 5 PCB for use in KiCad 6,' +
                                 ' since KiCad 6 does not support non-numeric timestamps which netlists used to use.')
parser.add_argument('input_pcb', type=argparse.FileType('r'))
parser.add_argument('input_netlist', type=argparse.FileType('r'))
parser.add_argument('output_pcb', type=argparse.FileType('w'))
args = parser.parse_args()

# build pathname -> new timestamp mapping
net_sexp = sexpdata.loads(args.input_netlist.read())
assert parse_symbol(net_sexp[0]) == 'export'
net_dict = group_by_car(net_sexp)

net_components = net_dict['components']
assert len(net_components) == 1
for elt in net_components[0][1:]:
  assert parse_symbol(elt[0]) == 'comp'
  elt_dict = group_by_car(elt)
  print(elt_dict['tstamps'])

pcb_sexp = sexpdata.loads(args.input_pcb.read())
assert parse_symbol(pcb_sexp[0]) == 'kicad_pcb'
pcb_dict = group_by_car(pcb_sexp)

for elt in pcb_dict['module']:
  elt_dict = group_by_car(elt)
  print(elt_dict['tstamp'])
