from tkinter import X, Y, BOTH, HORIZONTAL, VERTICAL, RIGHT, TOP, BOTTOM, Menu
from tkinter import ttk
import os

from edg_core import TransformUtil as tfu
from .Utils import *
from .Common import *


class DesignTreePanel:
  def __init__(self, parent: ttk.Frame, libraries: Library) -> None:
    self.frame = ttk.Frame(parent)
    self.label = ttk.Label(self.frame, text='Design Tree')
    self.label.pack(side=TOP, fill=X)

    self.tree = ttk.Treeview(self.frame, columns=('type'))
    self.tree.heading('type', text='Type')
    self.tree.tag_configure('noopts', foreground='black')
    self.tree.tag_configure('error', foreground=COLOR_ERROR)
    self.tree.tag_configure('abstract', foreground=COLOR_ABSTRACT)
    self.tree.tag_configure('refined', foreground=COLOR_REFINED)
    self.tree.bind('<<TreeviewSelect>>', self._on_select)

    self.hbar = ttk.Scrollbar(self.frame, orient=HORIZONTAL, command=self.tree.xview)
    self.hbar.pack(side=BOTTOM, fill=X)
    self.vbar = ttk.Scrollbar(self.frame, orient=VERTICAL, command=self.tree.yview)
    self.vbar.pack(side=RIGHT, fill=Y)

    self.tree.pack(expand=True, fill=BOTH)
    self.tree.configure(yscrollcommand=self.vbar.set, xscrollcommand=self.hbar.set)

    self.context_menu = Menu(self.tree, tearoff=0)
    self.context_menu_len = 0
    self.tree.bind("<Button-3>", self._on_rclick)

    self.libraries = libraries
    self.select_fns: List[Callable[[Optional[tfu.Path]], None]] = []

    self.item_path: MultiBiDict[Any, tfu.Path] = MultiBiDict()
    self.path_block: Dict[tfu.Path, edgir.BlockLikeTypes] = {}

  def _on_rclick(self, event) -> None:
    for i in range(self.context_menu_len):
      self.context_menu.delete(0)
    self.context_menu_len = 0

    item = self.tree.identify_row(event.y)  # _on_click is called before the row is elected
    if item not in self.item_path:
      return
    path = self.item_path[item]
    if path in self.path_block:
      sloc = edgir.source_locator_of(self.path_block[path], 'self')
      if sloc is not None:
        sloc_filepath, sloc_line = sloc
        self.context_menu.add_command(label=f"Open definition at {os.path.split(sloc_filepath)[-1]}: {sloc_line}",
                                      command=open_source_locator_wrapper(sloc_filepath, sloc_line))
        self.context_menu_len += 1

    parent_path = tfu.Path(path.blocks[:-1], (), (), ())
    if parent_path in self.path_block:
      sloc = edgir.source_locator_of(self.path_block[parent_path], path.blocks[-1])
      if sloc is not None:
        sloc_filepath, sloc_line = sloc
        self.context_menu.add_command(label=f"Open instantiation at {os.path.split(sloc_filepath)[-1]}: {sloc_line}",
                                      command=open_source_locator_wrapper(sloc_filepath, sloc_line))
        self.context_menu_len += 1

    if self.context_menu_len > 0:
      self.context_menu.post(event.x_root, event.y_root)

  def get_root(self) -> ttk.Frame:  # TODO replace with generic superclass
    return self.frame

  def _on_select(self, event) -> None:
    selected_path: Optional[tfu.Path] = None
    if self.tree.focus() in self.item_path:
      selected_path = self.item_path[self.tree.focus()]
    else:
      print(f"DesignTreePanel: unknown item selected")
    for fn in self.select_fns:
      fn(selected_path)

  def on_select(self, fn: Callable[[Optional[tfu.Path]], None]) -> None:
    self.select_fns.append(fn)

  def select_path(self, path: Optional[tfu.Path]) -> None:
    if path is not None:
      path = path.link_component(must_have_link=False)
    if path is not None and self.item_path.contains_value(path):
      self.tree.unbind('<<TreeviewSelect>>')
      self.tree.selection_set(self.item_path.get_only_by_value(path))
      self.tree.update()
      self.tree.bind('<<TreeviewSelect>>', self._on_select)

      path = tfu.Path(path.blocks[:-1], (), (), ())
      while self.item_path.contains_value(path) and path.blocks:
        self.tree.item(self.item_path.get_only_by_value(path), open=True)
        path = tfu.Path(path.blocks[:-1], (), (), ())
    else:
      self.tree.unbind('<<TreeviewSelect>>')
      self.tree.selection_set()  # type: ignore
      self.tree.update()
      self.tree.bind('<<TreeviewSelect>>', self._on_select)

  def load(self, design: edgir.Design, name: str) -> None:
    self.label.config(text=f"Design Tree: {name}")
    self.tree.delete(*self.tree.get_children())
    self.item_path.clear()
    self.path_block.clear()

    item = self.tree.insert('', 'end', text='(root)',
                            values=(superclasses_to_string(design.contents.superclasses), ), tag='noopts')
    self.item_path.add(item, tfu.Path.empty())
    self.path_block[tfu.Path.empty()] = design.contents  # TODO enable this with design contents in path_block

    for subname, subblock in edgir.ordered_blocks(design.contents):
      self._load_blocklike('', tfu.Path.empty().append_block(subname), subblock)
    for subname, sublink in edgir.ordered_links(design.contents):  # TODO unify w/ load_blocklike without root elt?
      self._load_blocklike('', tfu.Path.empty().append_link(subname), sublink)

  def _load_blocklike(self, parent_ref: str, path: tfu.Path,
                      blocklike: Union[edgir.BlockLike, edgir.LinkLike]) -> bool:  # returns needs parent to open
    if (isinstance(blocklike, edgir.BlockLike) and blocklike.HasField('hierarchy')) or \
        (isinstance(blocklike, edgir.LinkLike) and blocklike.HasField('link')):
      if isinstance(blocklike, edgir.BlockLike):
        block: edgir.BlockLikeTypes = blocklike.hierarchy
      elif isinstance(blocklike, edgir.LinkLike):
        block = blocklike.link
      if (path.blocks and is_internal_name(path.blocks[-1]) or isinstance(block, edgir.Link))\
          and 'error' not in block.meta.members.node and not DISPLAY_INTERNAL:
        return False

      parent_needs_open = False
      if 'error' in block.meta.members.node:
        tag = 'error'
        parent_needs_open = True
      elif 'refinement_original' in block.meta.members.node:
        tag = 'refined'
      elif 'abstract' in block.meta.members.node:
        tag = 'abstract'
        parent_needs_open = True
      else:
        tag = 'noopts'


      if isinstance(block, edgir.Link):
        text = 'Link: ' + path.links[-1]
      else:
        text = path.blocks[-1]

      item = self.tree.insert(parent_ref, 'end', text=text,
                              values=(superclasses_to_string(block.superclasses), ), tag=tag)
      self.item_path.add(item, path)
      self.path_block[path] = block

      item_open = False
      if isinstance(block, edgir.HierarchyBlock):
        for subname, subblock in edgir.ordered_blocks(block):
          block_needs_open = self._load_blocklike(item, path.append_block(subname), subblock)
          item_open = item_open or block_needs_open
      for subname, sublink in edgir.ordered_links(block):
        link_needs_open = self._load_blocklike(item, path.append_link(subname), sublink)
        item_open = item_open or link_needs_open
      if item_open:
        self.tree.item(item, open=True)
      return item_open or parent_needs_open
    elif isinstance(blocklike, edgir.BlockLike) and blocklike.HasField('lib_elem'):
      if is_internal_name(path.blocks[-1]) and not DISPLAY_INTERNAL:
        return False

      item = self.tree.insert(parent_ref, 'end', text=path.blocks[-1],
                              values=(f"unelaborated {blocklike.lib_elem.target.name}", ))
      self.item_path.add(item, path)
      return True
    else:
      raise ValueError(f"unknown BlockLike type {blocklike}")
