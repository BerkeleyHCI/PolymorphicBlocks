from typing import Type

import os
from contextlib import suppress
from edg_core import Block, ScalaCompiler, CompiledDesign
from electronics_model import footprint, NetlistTransform


def compile_board(design: Type[Block], target_dir: str, target_name: str) -> CompiledDesign:
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
  netlist = NetlistTransform(compiled).run()

  with open(design_filename, 'wb') as raw_file:
    raw_file.write(compiled.contents.SerializeToString())

  netlist_string = footprint.generate_netlist(netlist.blocks, netlist.nets)
  with open(netlist_filename, 'w', encoding='utf-8') as net_file:
    net_file.write(netlist_string)

  return compiled


def compile_board_inplace(design: Type[Block]) -> CompiledDesign:
  """Compiles a board and writes the results in a sub-directory
  where the module containing the top-level is located"""
  import inspect
  import os

  compiled = compile_board(
    design,
    os.path.join(os.path.dirname(inspect.getfile(design)), design.__module__.split(".")[-1]),
    design.__name__)

  return compiled
