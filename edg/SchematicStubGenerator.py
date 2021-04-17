from typing import List, Tuple, Dict, Set
from edg_core import TransformUtil
from electronics_model import Netlist
import zlib  # for a deterministic hash
import os


def _schematic_instantiation(name: str, type_name: str) -> str:
  return f"""
$Sheet
S 0 0 0 0 
U {name}
F0 "{name}" 0
F1 "{type_name}.sch" 0
$EndSheet
"""


def _schematic_contents(children: List[Tuple[str, str]]) -> str:  # name -> type
  child_strs = '\n\n'.join([_schematic_instantiation(name, type_name) for name, type_name in children])

  return f"""
EESchema Schematic File Version 2
EELAYER 25 0
EELAYER END

{child_strs}

$EndSCHEMATC
"""

def write_schematic_stubs(netlist: Netlist, target_dir: str, top_target_name: str):
  block_contents: Dict[TransformUtil.Path, List[TransformUtil.Path]] = {}  # block name -> list of internal blocks
  for path, block_type in netlist.types.items():
    if path.blocks:
      parent_blocks = path.blocks[:-1]
      parent_path = TransformUtil.Path(parent_blocks, (), (), ())
      block_contents.setdefault(parent_path, []).append(path)
  block_contents = {path: sorted(contents) for path, contents in block_contents.items()}

  block_types: Dict[TransformUtil.Path, Tuple[str, int]] = {}  # block name -> block type, hash of children
  def get_block_type(path: TransformUtil.Path) -> Tuple[str, int]:
    if path in block_types:
      return block_types[path]
    if path not in block_contents:
      return "", 0  # leaf block
    content_types = [(subblock.blocks[-1], get_block_type(subblock)) for subblock in block_contents[path]
                     if not subblock.blocks[-1].startswith('(bridge)') and
                     not subblock.blocks[-1].startswith('(adapter)')]
    content_str = str.encode(str(content_types))
    block_types[path] = netlist.types[path], zlib.adler32(content_str)  # TODO maybe use pickle
    return block_types[path]

  seen_types: Set[Tuple[str, int]] = set()
  def to_type_str(type_name: str, hash: int) -> str:
    return (type_name + ('_%08X' % hash)).replace('.', '_')

  for path, contents in block_contents.items():
    block_type_tup = get_block_type(path)
    if block_type_tup in seen_types:
      continue
    seen_types.add(block_type_tup)

    if not path.blocks:
      sch_name = top_target_name
    else:
      sch_name = to_type_str(*block_type_tup)

    children = [(subblock_path.blocks[-1], to_type_str(*get_block_type(subblock_path))) for subblock_path in contents
                if subblock_path in block_types]

    with open(os.path.join(target_dir, f'{sch_name}.sch'), 'w') as sch_file:
      sch_file.write(_schematic_contents(children))
