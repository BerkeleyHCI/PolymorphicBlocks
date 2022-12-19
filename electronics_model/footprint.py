import zlib  # for deterministic hash
from typing import NamedTuple, List, Mapping


class Block(NamedTuple):
  footprint: str
  refdes: str
  part: str
  value: str  # gets written directly to footprint
  full_path: List[str]  # short path to this footprint
  path: List[str]  # short path to this footprint
  class_path: List[str]  # classes on short path to this footprint

class Pin(NamedTuple):
  block_name: str
  pin_name: str

###############################################################################################################################################################################################

"""1. Generating Header"""

def gen_header() -> str:
    return '(export (version D)'

###############################################################################################################################################################################################

"""2. Generating Blocks"""

def gen_block_comp(block_name: str) -> str:
    return f'(comp (ref "{block_name}")'

def gen_block_value(block_value: str) -> str:
    return f'(value "{block_value}")'

def gen_block_footprint(block_footprint: str) -> str:
    return f'(footprint "{block_footprint}")'

def gen_block_tstamp(block_path: List[str]) -> str:
    blockpath_hash = f"{zlib.adler32(str.encode(block_path[-1])):08x}"
    return f'(tstamps "{blockpath_hash}"))'

def gen_block_sheetpath(sheetpath: List[str]) -> str:
  sheetpath_hash = [f"{zlib.adler32(str.encode(sheetpath_elt)):08x}" for sheetpath_elt in sheetpath]
  sheetpath_str = '/' + '/'.join(sheetpath)
  sheetpath_hash_str = '/' + '/'.join(sheetpath_hash)
  if sheetpath:  # need to add trailing /
    sheetpath_str = sheetpath_str + '/'
    sheetpath_hash_str = sheetpath_hash_str + '/'
  return f'(sheetpath (names "{sheetpath_str}") (tstamps "{sheetpath_hash_str}"))'

def gen_block_prop_sheetname(block_path: List[str]) -> str:
  if len(block_path) >= 2:
    value = block_path[-2]
  else:
    value = ""
  return f'(property (name "Sheetname") (value "{value}"))'

def gen_block_prop_sheetfile(block_path: List[str]) -> str:
  if len(block_path) >= 2:
    value = block_path[-2]
  else:
    value = ""
  return f'(property (name "Sheetfile") (value "{value}"))'

def gen_block_prop_path(block_path: List[str]) -> str:
  return f'(property (name "edg_path") (value "{".".join(block_path)}"))'

def gen_block_prop_shortpath(block_path: List[str]) -> str:
  return f'(property (name "edg_short_path") (value "{".".join(block_path)}"))'

def gen_block_prop_refdes(refdes: str) -> str:
  return f'(property (name "edg_refdes") (value "{refdes}"))'

def gen_block_prop_part(part: str) -> str:
  return f'(property (name "edg_part") (value "{part}"))'

def block_exp(block_dict: Mapping[str, Block]) -> str:
        """Given a dictionary of block_names (strings) as keys and Blocks (namedtuples) as corresponding values

        Example:
        (components
        (comp (ref U1)
        (value LM555)
        (footprint Package_DIP:DIP-4_W7.62mm)
        (tstamp U1))
        (comp (ref R3)
        (value 1k)
        (footprint OptoDevice:R_LDR_4.9x4.2mm_P2.54mm_Vertical)
        (tstamp R3))

        """
        result = '(components' 
        for block_name, block in block_dict.items():
            result += '\n' + gen_block_comp(block_name) + '\n' +\
                      "  " + gen_block_value(block.value) + '\n' + \
                      "  " + gen_block_footprint(block.footprint) + '\n' + \
                      "  " + gen_block_prop_sheetname(block.path) + '\n' + \
                      "  " + gen_block_prop_sheetfile(block.class_path) + '\n' + \
                      "  " + gen_block_prop_path(block.full_path) + '\n' + \
                      "  " + gen_block_prop_shortpath(block.path) + '\n' + \
                      "  " + gen_block_prop_refdes(block.refdes) + '\n' + \
                      "  " + gen_block_prop_part(block.part) + '\n' + \
                      "  " + gen_block_sheetpath(block.path[:-1]) + '\n' + \
                      "  " + gen_block_tstamp(block.path)
        return result + ')'

###############################################################################################################################################################################################

"""3. Generating Nets"""

def gen_net_header(net_count: int, net_name: str) -> str:
    return '(net (code {}) (name "{}")'.format(net_count, net_name)

def gen_net_pin(block_name: str, pin_name: str) -> str:
    return "(node (ref {}) (pin {}))".format(block_name, pin_name)

def net_exp(nets: Mapping[str, List[Pin]]) -> str:
        """Given a dictionary of net names (strings) as keys and a list of connected Pins (namedtuples) as corresponding values

        Example:
        (nets
            (net (code 1) (name "Net-(R1-Pad2)")
              (node (ref R2) (pin 1))
              (node (ref R1) (pin 2)))
            (net (code 3) (name GND)
              (node (ref C2) (pin 2))
              (node (ref C1) (pin 2))
              (node (ref R4) (pin 2)))
              
        """
        result = '(nets'
        net_count = 1
        for (net_name, pin_list) in nets.items():
            result += '\n' + gen_net_header(net_count, net_name)
            net_count += 1
            for pin in pin_list:
                result += '\n  ' + gen_net_pin(pin.block_name, pin.pin_name)
            result += ')'
        return result + ')'

###############################################################################################################################################################################################

"""4. Generate Full Netlist"""


def generate_netlist(blocks_dict: Mapping[str, Block], nets_dict: Mapping[str, List[Pin]]) -> str:
    return gen_header() + '\n' + block_exp(blocks_dict) + '\n' + net_exp(nets_dict) + '\n' + ')'
