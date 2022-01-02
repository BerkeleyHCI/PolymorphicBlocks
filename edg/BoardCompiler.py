from typing import Type, Optional, cast, Dict, Any, Mapping
from types import ModuleType

import os
from contextlib import suppress
from edg_core import Block, Link, Bundle, Port, ScalaCompiler, CompiledDesign
from electronics_model import footprint, NetlistGenerator
from edg_core.HdlInterfaceServer import LibraryElementResolver
from edg_core.Builder import builder
from edg_core.Core import LibraryElement
from .SchematicStubGenerator import write_schematic_stubs
import edgir
import pathlib
import inspect
import importlib

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
                 base_library: Mapping[str,Type[LibraryElement]] = {},
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
    if name in base_library:
      log(f"Skipping {name}")
      assert base_library[name] == cls, f"Inconsistent definitions for {name} in base and loaded library"
    elif isinstance(obj, Block):
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
      pb.root.members[name].port.CopyFrom(cast(edgir.Port, obj._def_to_proto()))
    else:
      log(f"Unknown category for class {cls}")

    count += 1

  log(f"Writing library to {output_file}")

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

  assert issubclass(design, Block), f"Designs must be blocks."

  design_obj = design()

  log(f"Dumping design {design_name}")
  pb = builder.elaborate_toplevel(design_obj, f"in elaborating design {design_name}")

  with open(output_file, 'wb') as file:
    file.write(pb.SerializeToString())

  log(f"Wrote {design_name} to {output_file}")

def dump_examples(*env_vars : Any,
                  target_dir : Optional[str] = None,
                  target_library_name : str = 'library_dump',
                  target_design_suffix : str = '_dump',
                  base_library : Optional[ModuleType] = None,
                  print_log : bool = False):
  """
  Used as follows within an example:

  > if __name__ == "__main__":
  >   dump_examples(<examples go here>, print_log=True)
  """

  def log(s:str):
    if print_log: print(s)
  examples : Dict[str,Type[Block]] = dict()
  example_module : ModuleType = cast(ModuleType, None)

  # if called w/ `globals()` as first parameter just unpack that.
  if len(env_vars) == 1 and isinstance(env_vars[0], dict):
    env_vars = tuple(env_vars[0].values())

  # Grab valid blocks from env_vars
  for item in env_vars:
    if inspect.isclass(item) and issubclass(item, Block):
      log(f"Found example {item.__name__}")

      # Make sure all examples are from the same module.
      if example_module:
        assert example_module == item.__module__, \
          f"Cannot dump examples from multiple modules: {example_module} and {item.__module__}"
      else:
        example_module = item.__module__

      examples[item.__name__] = item

  example_module = importlib.import_module(example_module)
  assert len(examples) > 0, f"No valid examples found"

  # get target directory
  if not target_dir:
    module_file = example_module.__file__
    target_dir = pathlib.Path(module_file).with_suffix('')
  log(f"Dumping examples to {target_dir}")

  # Dump library for base (if any)
  base_lib : Mapping[str, Type[LibraryElement]] = dict()
  if base_library:
     base_lib_resolver = LibraryElementResolver()
     base_lib_resolver.load_module(base_library)
     base_lib = base_lib_resolver.lib_class_map

  # Dump the example specific library
  dump_library(example_module,
               target_dir = target_dir,
               target_name = target_library_name,
               base_library = base_lib,
               print_log = print_log)

  for (name, example) in examples.items():
    dump_design(example,
                target_dir = target_dir,
                target_name = f"{name}{target_design_suffix}",
                print_log = print_log)
