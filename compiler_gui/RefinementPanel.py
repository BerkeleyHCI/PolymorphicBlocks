from tkinter import X, Y, BOTH, TOP, BOTTOM, HORIZONTAL, VERTICAL, RIGHT, Menu
from tkinter import ttk
from edg_core import TransformUtil as tfu
from .Utils import *


class RefinementPanel():
  def __init__(self, parent: ttk.Frame) -> None:
    self.frame = ttk.Frame(parent)
    self.label = ttk.Label(self.frame, text='Refinements')
    self.label.pack(side=TOP, fill=X)

    self.tree = ttk.Treeview(self.frame)

    self.hbar = ttk.Scrollbar(self.frame, orient=HORIZONTAL, command=self.tree.xview)
    self.hbar.pack(side=BOTTOM, fill=X)
    self.vbar = ttk.Scrollbar(self.frame, orient=VERTICAL, command=self.tree.yview)
    self.vbar.pack(side=RIGHT, fill=Y)

    self.tree.pack(expand=True, fill=BOTH)
    self.tree.configure(yscrollcommand=self.vbar.set, xscrollcommand=self.hbar.set)

    self.context_menu = Menu(self.tree, tearoff=0)
    self.context_menu.add_command(label="Delete", command=self._on_delete)
    self.tree.bind("<Button-1>", self._on_click)

    self.item_class_refinement: MultiBiDict[Any, Tuple[bytes, bytes]] = MultiBiDict()  # serialized LibraryPath
    self.item_instance_refinement: MultiBiDict[Any, Tuple[tfu.Path, bytes]] = MultiBiDict()
    self.item_param: MultiBiDict[Any, Tuple[tfu.Path, edgir.LitTypes]] = MultiBiDict()

    self.delete_fns: List[Callable[[Union[tfu.Path, edgir.LibraryPath], Union[edgir.LibraryPath, edgir.LitTypes]], None]] = []

  def on_delete(self, fn: Callable[[Union[tfu.Path, edgir.LibraryPath], Union[edgir.LibraryPath, edgir.LitTypes]], None]):
    self.delete_fns.append(fn)

  def _on_click(self, event) -> None:
    item = self.tree.identify_row(event.y)  # _on_click is called before the row is elected
    if item in self.item_class_refinement or item in self.item_instance_refinement or item in self.item_param:
      self.tree.selection_set(item)
      self.context_menu.post(event.x_root, event.y_root)

  def _on_delete(self) -> None:
    item = self.tree.focus()
    if item in self.item_class_refinement:
      cls_bin, lib_bin = self.item_class_refinement[item]
      for fn in self.delete_fns:
        fn(edgir.LibraryPath.FromString(cls_bin), edgir.LibraryPath.FromString(lib_bin))
    elif item in self.item_instance_refinement:
      path, lib_bin = self.item_instance_refinement[item]
      for fn in self.delete_fns:
        fn(path, edgir.LibraryPath.FromString(lib_bin))
    elif item in self.item_param:
      path, value = self.item_param[item]
      for fn in self.delete_fns:
        fn(path, value)

  def get_root(self) -> ttk.Frame:  # TODO replace with generic superclass
    return self.frame

  def load_refinement(self, refinement: DesignRefinement) -> None:
    self.tree.delete(*self.tree.get_children())
    self.item_instance_refinement.clear()
    self.item_param.clear()

    class_refinements_item = self.tree.insert('', 'end', 'class_refinements', text='Class Refinements', open=True)
    for cls_bin, lib_bin in refinement.class_refinements.items():
      item = self.tree.insert(class_refinements_item, 'end', cls_bin,
                              text=f'{path_to_string(edgir.LibraryPath.FromString(cls_bin))} = {path_to_string(edgir.LibraryPath.FromString(lib_bin))}')
      self.item_class_refinement.add(item, (cls_bin, lib_bin))

    instance_refinements_item = self.tree.insert('', 'end', 'instance_refinements', text='Instance Refinements', open=True)
    for path, lib_bin in refinement.instance_refinements.items():
      item = self.tree.insert(instance_refinements_item, 'end', str(path),
                              text=f'{str(path)} = {path_to_string(edgir.LibraryPath.FromString(lib_bin))}')
      self.item_instance_refinement.add(item, (path, lib_bin))

    param_settings_item = self.tree.insert('', 'end', 'param_settings', text='Param Settings', open=True)
    for path, value in refinement.param_settings.items():
      item = self.tree.insert(param_settings_item, 'end', str(path),
                              text=f'{str(path)} = {value}')
      self.item_param.add(item, (path, value))
