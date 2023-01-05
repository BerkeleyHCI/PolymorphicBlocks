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

pcb_sexp = sexpdata.loads(args.input_pcb.read())
assert parse_symbol(pcb_sexp[0]) == 'kicad_pcb'
pcb_dict = group_by_car(pcb_sexp)

netlist_sexp = sexpdata.loads(args.input_netlist.read())
assert parse_symbol(netlist_sexp[0]) == 'export'
netlist_dict = group_by_car(netlist_sexp)

print(pcb_dict)
