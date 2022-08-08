from collections import namedtuple
from typing import *
import zlib  # for deterministic hash

class Block(NamedTuple):
  footprint: str
  value: str
  path: List[str]

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
    blockpath_hash = f"{zlib.adler32(str.encode('.'.join(block_path))):08x}"
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
  return f'(property (name "Sheetname") (value "{".".join(block_path[:-1])}"))'

def gen_block_prop_sheetfile(block_path: List[str]) -> str:

  if len(block_path) >= 2:
    value = block_path[-2]
  else:
    value = ""
  return f'(property (name "Sheetfile") (value "{value}"))'

def block_exp(dict: Dict[str, Block]) -> str:
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
        for (block_name, block) in dict.items():
            result += '\n' + gen_block_comp(block_name) + '\n' +\
                      "  " + gen_block_value(block.value) + '\n' + \
                      "  " + gen_block_footprint(block.footprint) + '\n' + \
                      "  " + gen_block_prop_sheetname(block.path) + '\n' + \
                      "  " + gen_block_prop_sheetfile(block.path) + '\n' + \
                      "  " + gen_block_sheetpath(block.path[:-1]) + '\n' + \
                      "  " + gen_block_tstamp(block.path)
        return result + ')'

###############################################################################################################################################################################################

"""3. Generating Nets"""

def gen_net_header(net_count: int, net_name: str) -> str:
    return '(net (code {}) (name "{}")'.format(net_count, net_name)

def gen_net_pin(block_name: str, pin_name: str) -> str:
    return "(node (ref {}) (pin {}))".format(block_name, pin_name)

def net_exp(dict: Dict[str, Iterable[Pin]]) -> str:
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
        for (net_name, pin_list) in dict.items():
            result += '\n' + gen_net_header(net_count, net_name)
            net_count += 1
            for pin in pin_list:
                result += '\n' + gen_net_pin(pin.block_name, pin.pin_name)
            result += ')'
        return result + ')'

###############################################################################################################################################################################################

"""4. Generate Full Netlist"""

def generate_netlist(blocks_dict, nets_dict):
    return gen_header() + '\n' + block_exp(blocks_dict) + '\n' + net_exp(nets_dict) + '\n' + ')'

###############################################################################################################################################################################################

"""5. Test Data"""

blocks_dict = {'U1': Block('Package_DIP:DIP-4_W7.62mm', 'LM555', []),
            'R3': Block('OptoDevice:R_LDR_4.9x4.2mm_P2.54mm_Vertical', '1k', []),
            'R1': Block('OptoDevice:R_LDR_4.9x4.2mm_P2.54mm_Vertical', '4k7', []),
            'R2': Block('OptoDevice:R_LDR_4.9x4.2mm_P2.54mm_Vertical', '10k', []),
            'C1': Block('Capacitor_SMD:CP_Elec_3x5.3', '100\u03BCF', []),
            'C2': Block('Capacitor_SMD:C_0201_0603Metric', '10n', []),
            'D1': Block('LED_SMD:LED_0603_1608Metric_Pad1.05x0.95mm_HandSolder', 'LED', [])
              }

block_test1 = blocks_dict
block_test2: Dict[str, Block] = {}
block_test3 = {'A': Block('Capacitor', '10k', []), 'B': Pin('LED', 'LED')}
block_test4 = {1: Block('Capacitor', '10k', []), 2: Block('LED', 'LED', [])}
# Extra test case: block_test5 = {'A': Block('Capacitor', '10k'), 'B': Block('LED', 'LED')}


nets_dict = {'Net-(R3-Pad1)': [Pin('U1', '3'), Pin('R3', '1')],
            'Net-(C1-Pad1)': [Pin('U1', '2'), Pin('U1', '5'), Pin('U1', '6'), Pin('R2', '2'), Pin('C1', '1'), Pin('C2', '1')],
            'Net-(R1-Pad2)': [Pin('R2', '1'), Pin('R1', '2'), Pin('U1', '7')],
            '+9V': [Pin('R1', '1'), Pin('U1', '4'), Pin('U1', '8')],
            'GND': [Pin('D1', '1'), Pin('C2', '2'), Pin('C1', '2'), Pin('U1', '1')],
            'Net-(D1-Pad2)': [Pin('D1', '2'), Pin('R3', '2')]
            }

net_test1 = nets_dict
net_test2: Dict[str, List[Pin]] = {}
net_test3 = {'Net1': [Pin('U1', '3'), Pin('U2', '1')], 'Net2': [Block('R2', '4', []), Pin('R3', '1')]}
net_test4 = {1: [Pin('U1', '3'), Pin('U2', '1')], 2: [Block('R2', '4', []), Pin('R3', '1')]}
# Extra test case: net_test5 = {'Net3': [], 'Net4': [Pin('R2', '4'), Pin('R3', '1')]}
