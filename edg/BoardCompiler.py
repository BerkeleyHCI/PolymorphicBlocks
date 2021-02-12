from typing import Type

import os
from contextlib import suppress
from edg_core import Block, ScalaCompiler
from electronics_model import footprint, NetlistGenerator

from .SchematicStubGenerator import write_schematic_stubs


def compile_board(design: Type[Block], target_dir: str, target_name: str):
  if not os.path.exists(target_dir):
    os.makedirs(target_dir)
  assert os.path.isdir(target_dir), f"target_dir {target_dir} to compile_board must be directory"

  design_filename = os.path.join(target_dir, f'{target_name}.edg')
  netlist_filename = os.path.join(target_dir, f'{target_name}.net')

  with suppress(FileNotFoundError):
    os.remove(design_filename)
  with suppress(FileNotFoundError):
    os.remove(netlist_filename)

  compiled = ScalaCompiler.compile(design)
  netlist = NetlistGenerator().generate(compiled)

  with open(design_filename, 'wb') as raw_file:
    raw_file.write(compiled.contents.SerializeToString())

  netlist_string = footprint.generate_netlist(netlist.blocks, netlist.nets)
  with open(netlist_filename, 'w') as net_file:
    net_file.write(netlist_string)

  write_schematic_stubs(netlist, target_dir, target_name)
