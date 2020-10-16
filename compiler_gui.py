from typing import *
import os
import pickle
import time
import argparse
import contextlib
import traceback
from electronics_model import footprint

from tkinter import *
from tkinter import ttk, simpledialog
from compiler_gui import *
from compiler_gui.ElkGraph import ElkGraph

from edg_core import *
from edg import *
from edg import TransformUtil as tfu
from edg_core.edgir import LibraryPath


parser = argparse.ArgumentParser()

parser.add_argument("design", help=".edg design file")
parser.add_argument("--library", help="library file, by default looks for lib.lib in the same folder as the design")
parser.add_argument("--refinement", help="refinements file, by default looks for refinement.edgr in the same folder as the design")
parser.add_argument("--no-generate", help="don't generate the design", action='store_true')

args = parser.parse_args()

raw_design = edgir.Design()
with open(args.design, "rb") as f:
  raw_design.ParseFromString(f.read())
  print(f'Loaded design from {args.design}')

design_folder, _ = os.path.split(args.design)

if args.library is None:
  library_file = os.path.join(design_folder, "lib.lib")
else:
  library_file = args.library

library = Library()
library_pb = edgir.Library()
with open(library_file, "rb") as f:
  library_pb.ParseFromString(f.read())
  print(f'Loaded library from {library_file}')
library._load_library(library_pb)  # TODO avoid internal method use?

refinement: DesignRefinement = DefaultRefinement
if args.refinement is None:
  refinement_file = os.path.join(design_folder, "refinement.edgr")
else:
  refinement_file = args.refinement

if os.path.exists(refinement_file):
  with open(refinement_file, "rb") as f:
    refinement = pickle.load(f)
  print(f'Loaded refinement from {refinement_file}')
else:
  print(f'Using default refinement')
assert isinstance(refinement, DesignRefinement)


ElkGraph.start_gateway()
def on_close():
  ElkGraph.close_gateway()
  root.destroy()


root = Tk()
root.geometry('2000x1000')
root.protocol("WM_DELETE_WINDOW", on_close)

main_pane = PanedWindow(root, orient=HORIZONTAL)
main_pane.pack(fill=BOTH, expand=1)
main_pane.config(showhandle=True, sashrelief='raised')


# Workaround for Tk bug in https://bugs.python.org/issue36468
def fixed_map(option):
  # Fix for setting text colour for Tkinter 8.6.9
  # From: https://core.tcl.tk/tk/info/509cafafae
  #
  # Returns the style map for 'option' with any styles starting with
  # ('!disabled', '!selected', ...) filtered out.

  # style.map() returns an empty list for missing options, so this
  # should be future-safe.
  return [elm for elm in style.map('Treeview', query_opt=option) if
          elm[:2] != ('!disabled', '!selected')]
style = ttk.Style()
style.map('Treeview', foreground=fixed_map('foreground'),
          background=fixed_map('background'))


block_diagram = BlockDiagramPanel(main_pane)
main_pane.add(block_diagram.get_root())

design_tree = DesignTreePanel(main_pane, library)
main_pane.add(design_tree.get_root())

library_pane = PanedWindow(root, orient=VERTICAL)
library_pane.config(showhandle=True, sashrelief='raised')
library_pane.pack(fill=BOTH, expand=1)

library_tree = LibraryTreePanel(library_pane, library)
library_pane.add(library_tree.get_root())
library_tree.populate_all()

refinement_pane = RefinementPanel(library_pane)
library_pane.add(refinement_pane.get_root())

main_pane.add(library_pane)

block_view = BlockView(main_pane)
main_pane.add(block_view.get_root())


selected_path: Optional[TransformUtil.Path] = None  # TODO can we avoid use of global state?


def update_design(refinement: DesignRefinement) -> Tuple[edgir.Design, SimpleConstPropTransform]:
  refinement_pane.load_refinement(refinement)

  solve_time = time.process_time()
  if not args.no_generate:
    netlist_filename = os.path.join(design_folder, 'netlist.net')

    with contextlib.suppress(FileNotFoundError):
      os.remove(netlist_filename)

    design, transformer = ElectronicsDriver([], library.all_defs())._generate_design(raw_design, refinement,
                                                                                     continue_on_error=True,
                                                                                     name=args.design)
    design = transformer.scp.transform_design(design)
    scp = transformer.scp
    design = CheckErrorsTransform(scp).transform_design(design)
    design_scp = WriteSolvedParamTransform(scp).transform_design(design)

    try:
      netlist = NetlistGenerator().generate(design_scp)
      netlist_string = footprint.generate_netlist(netlist.blocks, netlist.nets)

      with open(netlist_filename, 'w') as net_file:
        net_file.write(netlist_string)
        print(f"Wrote netlist to {netlist_filename}")
    except BaseException as e:
      traceback.print_exc()
      print(f"Failed to netlist")

  else:
    scp = SimpleConstPropTransform()
    scp.transform_design(raw_design)
    design = raw_design

  design_tree_load_time = time.process_time()
  design_tree.load(design, args.design)  # TODO better management of file state
  block_diagram_load_time = time.process_time()
  block_diagram.load(design)
  library_tree.populate_all()
  block_view.clear()

  finish_time = time.process_time()

  print(f"Loaded design, solve in {design_tree_load_time-solve_time:.3f}, "
        f"design tree in {block_diagram_load_time-design_tree_load_time:.3f}, "
        f"block diagram in {finish_time-block_diagram_load_time:.3f}")

  if selected_path is not None:
    unused_relpath, (target_path, target_elt) = tfu.Path.empty().follow_partial(selected_path.to_local_path(),
                                                                                design.contents)
    elt_select(target_path)

  return design, scp

design, scp = update_design(refinement)


def elt_select(path: Optional[TransformUtil.Path]) -> None:
  if path is not None:
    global selected_path
    selected_path = path
    block_diagram.select_path(selected_path)
    design_tree.select_path(selected_path)
    block_path = path.block_component()
    selected_block = tfu.Path.empty().follow(block_path.to_local_path(), design.contents)[1]

    root_libs = list(selected_block.superclasses)
    if 'refinement_original' in selected_block.meta.members.node:
      root_libs = [edgir.LibraryPath.FromString(selected_block.meta.members.node['refinement_original'].bin_leaf)]

    library_tree.populate_block_subtypes(root_libs, list(selected_block.superclasses),
                                         block_path)
    block_view.load_block(design, path, scp)
  else:
    library_tree.populate_all()
    block_view.clear()
    block_diagram.select_path(None)
    design_tree.select_path(None)

design_tree.on_select(elt_select)
block_diagram.on_select(elt_select)


def update_refinement(new_refinement: DesignRefinement) -> None:
  global design, scp, refinement
  refinement = new_refinement
  design, scp = update_design(new_refinement)
  print(f'Saving refinement to {refinement_file}')
  with open(refinement_file, "wb") as f:
    pickle.dump(new_refinement, f)


def library_tree_select(target: Union[edgir.LibraryPath, tfu.Path], lib_path: edgir.LibraryPath) -> None:
  global design, refinement

  if isinstance(target, edgir.LibraryPath):
    refinement.class_refinements.update({target.SerializeToString(): lib_path.SerializeToString()})
  elif isinstance(target, tfu.Path):
    target_elt = TransformUtil.Path.empty().follow(selected_path.to_local_path(), design.contents)[1]
    if target_elt.superclasses[-1] == lib_path:
      if target in refinement.instance_refinements:
        del refinement.instance_refinements[target]  # alternate way to clear refinement
    else:
      refinement.instance_refinements.update({target: lib_path.SerializeToString()})
  else:
    raise ValueError(f"unknown target {target}")

  update_refinement(refinement)  # TODO don't modify refinement in-place

library_tree.on_select(library_tree_select)


def block_param_update(path: tfu.Path, curr_value: Optional[edgir.LitTypes]) -> None:
  _, path_elt = tfu.Path.empty().follow(path.to_local_path(), design.contents)
  if isinstance(path_elt, edgir.ValInit):
    constrained_value = None
    if curr_value is not None:
      answer = edgir.lit_to_string(curr_value)
    else:
      answer = ''

    while constrained_value is None:
      answer = simpledialog.askstring("Add constraint", f"Set {path}: {edgir.valinit_to_type_string(path_elt)}",
                                      parent=root, initialvalue=answer)
      if answer is None:
        return
      constrained_value = edgir.string_to_lit(answer, path_elt)

    refinement.param_settings.update({path: constrained_value})
    update_refinement(refinement)  # TODO don't modify refinement in-place

block_view.on_dclick(block_param_update)


def refinement_del(key: Union[tfu.Path, edgir.LibraryPath], val: Union[edgir.LibraryPath, edgir.LitTypes]) -> None:
  global refinement
  if isinstance(key, tfu.Path) and isinstance(val, edgir.LibraryPath):  # instance refinement
    del refinement.instance_refinements[key]
  elif isinstance(key, tfu.Path):  # param value
    del refinement.param_settings[key]
  elif isinstance(key, edgir.LibraryPath) and isinstance(val, edgir.LibraryPath):  # class refinement
    del refinement.class_refinements[key.SerializeToString()]
  else:
    print(f"can't delete refinement {key}={val}")
    return
  update_refinement(refinement)  # TODO don't modify refinement in-place

refinement_pane.on_delete(refinement_del)


root.mainloop()
