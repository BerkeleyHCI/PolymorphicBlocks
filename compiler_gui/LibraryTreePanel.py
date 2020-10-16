from tkinter import X, Y, BOTH, TOP, BOTTOM, HORIZONTAL, VERTICAL, RIGHT, Menu
from tkinter import ttk
from edg_core import TransformUtil as tfu
import os
from .Utils import *
from .Common import *


class LibraryTreePanel:
  def __init__(self, parent: ttk.Frame, libraries: Library) -> None:
    self.frame = ttk.Frame(parent)
    self.label = ttk.Label(self.frame)
    self.label.pack(side=TOP, fill=X)

    self.tree = ttk.Treeview(self.frame)
    self.tree.tag_configure('selected', font=('TkDefaultFont', 9, 'bold'))  # TODO get default font size
    self.tree.tag_configure('missing', foreground=COLOR_ERROR)
    self.tree.tag_configure('abstract', foreground=COLOR_ABSTRACT)

    self.hbar = ttk.Scrollbar(self.frame, orient=HORIZONTAL, command=self.tree.xview)
    self.hbar.pack(side=BOTTOM, fill=X)
    self.vbar = ttk.Scrollbar(self.frame, orient=VERTICAL, command=self.tree.yview)
    self.vbar.pack(side=RIGHT, fill=Y)

    self.tree.pack(expand=True, fill=BOTH)
    self.tree.configure(yscrollcommand=self.vbar.set, xscrollcommand=self.hbar.set)

    self.context_menu = Menu(self.tree, tearoff=0)
    self.context_menu_len = 0
    self.tree.bind("<Button-3>", self._on_click)
    self.tree.bind("<Double-Button-1>", self._on_click)

    self.libraries = libraries

    self.item_path: MultiBiDict[Any, bytes] = MultiBiDict()  # serialized LibraryPath
    self.select_fns: List[Callable[[Union[edgir.LibraryPath, tfu.Path], edgir.LibraryPath], None]] = []
    self.block_path: Optional[tfu.Path] = None
    self.root_libs: List[edgir.LibraryPath] = []

  def get_root(self) -> ttk.Frame:  # TODO replace with generic superclass
    return self.frame

  def _on_click(self, event) -> None:
    item = self.tree.identify_row(event.y)  # _on_click is called before the row is elected
    if item not in self.item_path:
      return

    for i in range(self.context_menu_len):
      self.context_menu.delete(0)
    self.context_menu_len = 0

    selected_lib = edgir.LibraryPath.FromString(self.item_path[item])

    if self.block_path is not None and selected_lib not in self.root_libs:
      self.context_menu.add_command(label=f"Refine instance {self.block_path}",
                                    command=self._on_instance_refinement)
      self.context_menu_len += 1

      for block_lib in self.root_libs:
        self.context_menu.add_command(label=f"Refine all of class {path_to_string(block_lib)}",
                                      command=self._on_class_refinement_wrapper(block_lib))
        self.context_menu_len += 1

      self.tree.selection_set(item)

    if selected_lib.SerializeToString() in self.libraries.blocks:
      sloc = edgir.source_locator_of(self.libraries.blocks[selected_lib.SerializeToString()], 'self')
      if sloc is not None:
        sloc_filepath, sloc_line = sloc
        if self.context_menu_len > 0:
          self.context_menu.add_separator()
          self.context_menu_len += 1
        self.context_menu.add_command(label=f"Open definition at {os.path.split(sloc_filepath)[-1]}: {sloc_line}",
                                      command=open_source_locator_wrapper(sloc_filepath, sloc_line))
        self.context_menu_len += 1

    if self.context_menu_len > 0:
      self.context_menu.post(event.x_root, event.y_root)

  def _on_instance_refinement(self):
    selected = self.tree.focus()
    if self.block_path is not None and selected in self.item_path:
      for fn in self.select_fns:
        fn(self.block_path, edgir.LibraryPath.FromString(self.item_path[selected]))
    else:
      raise ValueError(f"unknown item {selected}")

  def _on_class_refinement_wrapper(self, lib_class: edgir.LibraryPath):
    def inner():
      selected = self.tree.focus()
      if selected in self.item_path:
        for fn in self.select_fns:
          fn(lib_class, edgir.LibraryPath.FromString(self.item_path[selected]))
        pass
      else:
        raise ValueError(f"unknown item {selected}")
    return inner

  def on_select(self, fn: Callable[[Union[edgir.LibraryPath, tfu.Path], edgir.LibraryPath], None]) -> None:
    self.select_fns.append(fn)

  def _populate_block(self, parent_ref: str, lib_path: edgir.LibraryPath, open: bool=False):
    ref = self.tree.insert(parent_ref, 'end', parent_ref + str(lib_path.SerializeToString()),
                           text=path_to_string(lib_path), open=open)

    if lib_path.SerializeToString() in self.libraries.blocks:
      block = self.libraries.blocks[lib_path.SerializeToString()]
      if 'abstract' in block.meta.members.node:
        self.tree.item(ref, tag='abstract')
    else:
      self.tree.item(ref, tag='missing')

    self.item_path.add(ref, lib_path.SerializeToString())
    for child_path, child_elt in self.libraries.get_child_blocks(lib_path):
      self._populate_block(ref, child_path, open)

  def populate_all(self) -> None:
    self.tree.delete(*self.tree.get_children())
    self.item_path.clear()
    self.block_path = None
    self.root_libs = []

    self.label.config(text=f"All Library Elements")

    self.tree.insert('', 'end', 'blocks', text='All Blocks', open=True)
    # insert blocks into the tree starting with those that do not have parents
    for path, elt in self.libraries.get_root_blocks():
      self._populate_block('blocks', path)

    for path in self.libraries.get_missing_blocks():
      self._populate_block('blocks', path)

    self.tree.insert('', 'end', 'ports', text='All Ports')
    for path, port in self.libraries.get_root_ports():
      self.tree.insert('ports', 'end', path.SerializeToString(),
                       text=path_to_string(path))

    self.tree.insert('', 'end', 'links', text='All Links')
    for path, link in self.libraries.get_root_links():
      self.tree.insert('links', 'end', path.SerializeToString(),
                       text=path_to_string(path))

  # TODO support base + refinement types
  def populate_block_subtypes(self, root_libs: List[edgir.LibraryPath], selected_libs: List[edgir.LibraryPath], block_path: tfu.Path) -> None:
    self.tree.delete(*self.tree.get_children())
    self.item_path.clear()
    self.block_path = block_path
    self.root_libs = root_libs

    self.label.config(text=f"Refinements for {str(block_path)}")

    # TODO: dedup block names where there is a parent child relation
    for lib in root_libs:
      self._populate_block('', lib, open=True)

    for selected_lib in selected_libs:
      for item in self.item_path.get_by_value(selected_lib.SerializeToString()):
        self.tree.item(item, tag='selected')

  def clear(self) -> None:
    raise NotImplementedError
