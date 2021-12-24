from typing import Type, Optional, cast
from types import ModuleType

import os
from contextlib import suppress
from edg_core import Block, Link, Bundle, Port, ScalaCompiler, CompiledDesign
from electronics_model import footprint, NetlistGenerator
from edg_core.HdlInterfaceServer import LibraryElementResolver
from edg_core.Builder import builder
from .SchematicStubGenerator import write_schematic_stubs
import edgir


def compile_board(design: Type[Block], target_dir: str, target_name: str,
                  errors_fatal: bool = True) -> CompiledDesign:
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
  with open(netlist_filename, 'w', encoding='utf-8') as net_file:
    net_file.write(netlist_string)

  write_schematic_stubs(netlist, target_dir, target_name)

  return compiled


def compile_board_inplace(design: Type[Block], errors_fatal: bool = True) -> CompiledDesign:
  """Compiles a board and writes the results in a sub-directory
  where the module containing the top-level is located"""
  import inspect
  import os

  compiled = compile_board(
    design,
    os.path.join(os.path.dirname(inspect.getfile(design)), design.__module__.split(".")[-1]),
    design.__name__,
    errors_fatal=errors_fatal)

  if compiled.result.error:
    print(f"error during compilation: \n{compiled.result.error}")

  return compiled


def dump_library(module : ModuleType,
                 target_dir: Optional[str] = None,
                 target_name: str = 'library',
                 print_log : bool = False):

  def log(s:str):
    if print_log: print(s)

  library = LibraryElementResolver()
  library.load_module(module)
  pb = edgir.Library()
  target_dir = target_dir if target_dir else os.getcwd()
  output_file = os.path.join(target_dir, f'{target_name}.edg')

  count = 0
  for (name, cls) in library.lib_class_map.items():
    obj = cls()
    if isinstance(obj, Block):
      log(f"Dumping block {name}")
      block_proto = builder.elaborate_toplevel(obj, f"in elaborating library block {cls}")
      pb.root.members[name].hierarchy_block.CopyFrom(block_proto)
    elif isinstance(obj, Link):
      log(f"Dumping link {name}")
      link_proto = builder.elaborate_toplevel(obj, f"in elaborating library link {cls}")
      assert isinstance(link_proto, edgir.Link)  # TODO this needs to be cleaned up
      pb.root.members[name].link.CopyFrom(link_proto)
    elif isinstance(obj, Bundle):  # TODO: note Bundle extends Port, so this must come first
      log(f"Dumping bundle {name}")
      pb.root.members[name].bundle.CopyFrom(obj._def_to_proto())
    elif isinstance(obj, Port):
      log(f"Dumping port {name}")
      pb.root.members[name].port.CopyFrom(cast(Port, obj._def_to_proto()))
    else:
      log(f"Unknown category for class {cls}")

    count += 1

  with open(output_file, 'wb') as file:
    file.write(pb.SerializeToString())

  log(f"Wrote {count} classes to {output_file}")

def dump_design(design : Type[Block],
                target_dir : Optional[str] = None,
                target_name : str = 'design',
                print_log : bool = False):

  def log(s:str):
    if print_log: print(s)

  target_dir = target_dir if target_dir else os.getcwd()
  module_name = design.__module__.split(".")[-1]
  design_name = design.__name__

  if not os.path.exists(target_dir):
    os.makedirs(target_dir)
  assert os.path.isdir(target_dir), f"target_dir {target_dir} to compile_board must be directory"

  output_file = os.path.join(target_dir, f'{target_name}.edg')

  # assert isinstance(design, Block)

  log(f"Dumping design {design_name}")
  pb = builder.elaborate_toplevel(design, f"in elaborating design {design_name}")

  with open(output_file, 'wb') as file:
    file.write(pb.SerializeToString())

  log(f"Wrote {design_name} to {output_file}")
