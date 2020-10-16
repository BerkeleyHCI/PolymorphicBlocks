from tkinter import X, Y, BOTH, TOP, BOTTOM, HORIZONTAL, VERTICAL, RIGHT, Menu
from tkinter import ttk
import os
from edg_core import TransformUtil as tfu
from electronics_model import UnitUtils
from .Utils import *
from .Common import *
from .ExprDetailPanel import ExprDetailPanel
from edg_core import SimpleConstProp as scp


class BlockView:
  TOLERANCE_THRESHOLD = 0.25
  @classmethod
  def lit_to_str(cls, lit) -> str:
    if isinstance(lit, tuple) and len(lit) == 2 and isinstance(lit[0], (float, int)) and isinstance(lit[1], (float, int)):
      lit_center = (lit[0] + lit[1]) / 2
      if lit_center != 0:
        lit_tol = (lit_center - lit[0]) / lit_center
        if lit_tol == 0:
          return f"{UnitUtils.num_to_prefix(lit_center, 3)} ± {lit_tol*100:0.2g}%"
        elif lit_tol < cls.TOLERANCE_THRESHOLD:
          return f"{UnitUtils.num_to_prefix(lit_center, 3)} ± {lit_tol*100:0.2g}%  " \
            f"({UnitUtils.num_to_prefix(lit[0], 3)}, {UnitUtils.num_to_prefix(lit[1], 3)})"
      return f'({UnitUtils.num_to_prefix(lit[0], 3)}, {UnitUtils.num_to_prefix(lit[1], 3)})'
    elif isinstance(lit, float):
      return f'{UnitUtils.num_to_prefix(lit, 3)}'
    else:
      return str(lit)  # catchall fallback

  def __init__(self, parent: ttk.Frame) -> None:
    self.frame = ttk.Frame(parent)
    self.label = ttk.Label(self.frame)
    self.label.pack(side=TOP, fill=X)
    self.label.bind('<Configure>', self._set_label_wrap)

    self.property = ttk.Treeview(self.frame, columns=('value'))
    self.property.heading('value', text='Value')
    self.property.tag_configure('error', foreground=COLOR_ERROR)
    self.context_menu = Menu(self.property, tearoff=0)
    self.context_menu_len = 0
    self.property.bind('<Button-3>', self._on_rclick)
    self.property.bind('<Double-1>', self._on_dclick)

    self.hbar = ttk.Scrollbar(self.frame, orient=HORIZONTAL, command=self.property.xview)
    self.hbar.pack(side=BOTTOM, fill=X)
    self.vbar = ttk.Scrollbar(self.frame, orient=VERTICAL, command=self.property.yview)
    self.vbar.pack(side=RIGHT, fill=Y)

    self.property.pack(expand=True, fill=BOTH)
    self.property.configure(yscrollcommand=self.vbar.set, xscrollcommand=self.hbar.set)

    self.dclick_fns: List[Callable[[tfu.Path, Optional[edgir.LitTypes]], None]] = []

    self.item_path: MultiBiDict[Any, tfu.Path] = MultiBiDict()
    self.item_source: MultiBiDict[Any, Tuple[str, int]] = MultiBiDict()
    self.item_expr: MultiBiDict[Any, scp.ScpValueExpr] = MultiBiDict()
    self.vals: Optional[SimpleConstPropTransform] = None

    self.clear()

  def _set_label_wrap(self, event):
    event.widget.configure(wraplength=event.width)

  def get_root(self) -> ttk.Frame:  # TODO replace with generic superclass
    return self.frame

  def _on_rclick(self, event):
    item = self.property.identify_row(event.y)  # _on_click is called before the row is elected

    for i in range(self.context_menu_len):
      self.context_menu.delete(0)
    self.context_menu_len = 0

    if item in self.item_source:
      sloc_filepath, sloc_line = self.item_source[item]
      self.context_menu.add_command(label=f"Open instantiation at {os.path.split(sloc_filepath)[-1]}: {sloc_line}",
                                    command=open_source_locator_wrapper(sloc_filepath, sloc_line))
      self.context_menu_len += 1

    if item in self.item_path:
      assert self.vals is not None
      item_path = self.item_path[item]
      if item_path.params:
        if self.context_menu_len > 0:
          self.context_menu.add_separator()  # TODO separator should be added for exprs too
          self.context_menu_len += 1
        self.context_menu.add_command(label=f"Open constraint tracer at {item_path}",
                                      command=lambda: ExprDetailPanel.create_window(self.frame, item_path, self.vals))
        self.context_menu_len += 1

    if item in self.item_expr:
      assert self.vals is not None
      for expr in self.item_expr.get(item):
        self.context_menu.add_command(label=f"Open constraint tracer for {expr}",
                                      command=lambda: ExprDetailPanel.create_window(self.frame, expr, self.vals))
        self.context_menu_len += 1

    if self.context_menu_len > 0:
      self.context_menu.post(event.x_root, event.y_root)

  def _on_dclick(self, event):
    item = self.property.identify_row(event.y)
    if item in self.item_path:
      item_path = self.item_path[item]
      assert self.vals is not None
      value = self.vals.resolve_param(item_path)
      if value is not None:
        value_str: Optional[str] = scp.expr_result_to_str(value)
      else:
        value_str = None

      for fn in self.dclick_fns:
        fn(item_path, value_str)

  def on_dclick(self, fn: Callable[[tfu.Path, Optional[edgir.LitTypes]], None]) -> None:
    self.dclick_fns.append(fn)

  def clear(self) -> None:
    self.property.delete(*self.property.get_children())
    self.label.config(text="Block Detail")

    self.item_path.clear()
    self.item_source.clear()
    self.item_expr.clear()
    self.vals = None

  def load_block(self, design: edgir.Design, path: tfu.Path, vals: SimpleConstPropTransform) -> None:
    self.clear()

    self.vals = vals
    path = path.link_component(must_have_link=False)
    _, block = tfu.Path.empty().follow(path.to_local_path(), design.contents)  # TODO allow following to Path

    assert isinstance(block, (edgir.HierarchyBlock, edgir.Link))

    label_text = f"Block Detail: {superclasses_to_string(block.superclasses)} at {path}"

    edgdoc = edgir.edgdoc_of(block, 'self')
    if edgdoc is not None:
      label_text += '\n\n' + edgdoc

    if 'error' in block.meta.members.node:
      label_text += '\n\nContains Errors'
      if 'traceback' in block.meta.members.node:
        label_text += '\n\nTraceback:\n' + block.meta.members.node['traceback'].text_leaf
    else:
      assert 'traceback' not in block.meta.members.node

    self.label.config(text=label_text)

    def process_port(parent: str, path: tfu.Path, port: edgir.PortTypes, sloc: Optional[Tuple[str, int]]) -> None:
      item = self.property.insert(parent, 'end', parent + path.ports[-1],
                                  text=f'{path.ports[-1]}: Port[{superclasses_to_string(port.superclasses)}]',
                                  values=('',), open=True)
      self.item_path.add(item, path)
      if sloc is not None:
        self.item_source.add(item, sloc)

      if not path.links:  # can only get port link, if port is not part of a link
        link_port_path = vals.get_port_link(path)
      else:
        link_port_path = None

      if link_port_path is not None:
        link_path = link_port_path.link_component()
        _, link = tfu.Path.empty().follow(link_path.to_local_path(), design.contents)
        assert isinstance(link, edgir.Link)

        link_item = self.property.insert(item, 'end', item + 'link',
                                         text=f'Connected {superclasses_to_string(link.superclasses)}',
                                         values=(f'{link_port_path}',))
        self.item_path.add(link_item, link_path)
        for name, param in edgir.ordered_params(link):
          sloc = edgir.source_locator_of(link, name)
          process_param(link_item, link_path.append_param(name), param, sloc)
      elif not path.links:
        self.property.insert(item, 'end', item + 'link',
                             text=f'Unconnected', values=('',))

      if isinstance(port, (edgir.Port, edgir.Bundle)):
        for name, param in edgir.ordered_params(port):
          sloc = edgir.source_locator_of(port, name)
          process_param(item, path.append_param(name), param, sloc)
      if isinstance(port, edgir.Bundle):
        for name, subport in edgir.ordered_ports(port):
          sloc = edgir.source_locator_of(port, name)
          process_port(item, path.append_port(name), edgir.resolve_portlike(subport), sloc)
      if isinstance(port, edgir.PortArray):  # TODO ordered ports for Array?
        for name, subport in port.ports.items():
          process_port(item, path.append_port(name), edgir.resolve_portlike(subport), None)

    def process_param(parent: str, path: tfu.Path, param: edgir.ValInit, sloc: Optional[Tuple[str, int]]) -> None:
      if is_internal_name(path.params[-1]) and not DISPLAY_INTERNAL:
        return

      value = vals.resolve_param(path)
      tag = ''
      if value is None:
        value_str = 'unknown'
      elif isinstance(value, scp.BaseErrorResult):
        value_str = scp.expr_result_to_str(value)  # TODO unify logic?
        tag = 'error'
      elif isinstance(value, scp.Interval):
        value_str = self.lit_to_str((value.lower(), value.upper()))
      elif isinstance(value, scp.SubsetInterval):
        value_str = f'subset({self.lit_to_str((value.lower(), value.upper()))})'
      else:
        value_str = self.lit_to_str(value)

      item = self.property.insert(parent, 'end', parent + path.params[-1],
                                  text=f'{path.params[-1]}: {edgir.valinit_to_type_string(param)}', values=(value_str,),
                                  tag=tag)
      self.item_path.add(item, path)
      if sloc is not None:
        self.item_source.add(item, sloc)

    def process_metadata(parent: str, meta: edgir.Metadata) -> None:
      for key, meta in sorted(meta.members.node.items()):
        if meta.HasField('text_leaf'):
          # TODO Tkinter doesn't seem to escape text properly, this may crash if there are quotes in the text
          self.property.insert(parent, 'end', parent + key, text=key, values=(meta.text_leaf, ))
        elif meta.HasField('bin_leaf'):
          self.property.insert(parent, 'end', parent + key, text=key, values=(str(meta.bin_leaf), ))
        elif meta.HasField('members'):
          item = self.property.insert(parent, 'end', parent + key, text=key)
          process_metadata(item, meta)
        elif not meta.SerializeToString():
          self.property.insert(parent, 'end', parent + key, text=key, values=('empty', ))
        else:
          self.property.insert(parent, 'end', parent + key, text=key, values=(f'unknown: {str(meta.SerializeToString())}', ))

    params_item = self.property.insert('', 'end', 'params',
                                       text='Params', open=True)
    for name, param in edgir.ordered_params(block):
      sloc = edgir.source_locator_of(block, name)
      process_param(params_item, path.append_param(name), param, sloc)

    ports_item = self.property.insert('', 'end', 'ports',
                                      text='Ports', open=True)
    for name, port in edgir.ordered_ports(block):
      sloc = edgir.source_locator_of(block, name)
      process_port(ports_item, path.append_port(name), edgir.resolve_portlike(port), sloc)

    meta_item = self.property.insert('', 'end', 'meta',
                                      text='Metadata')
    process_metadata(meta_item, block.meta)

    constraints_item = self.property.insert('', 'end', 'constraints',
                                            text='Constraints')

    scp_constraints = vals.constraints.get(path, {})
    error_constraints = []  # TODO errors metadata should be in a cleaner format
    if 'error' in block.meta.members.node and 'constraints' in block.meta.members.node['error'].members.node:
      for constr_name, _ in block.meta.members.node['error'].members.node['constraints'].members.node.items():
        constr_name_split = constr_name.split(':')
        if len(constr_name_split) == 2:
          error_constraints.append(constr_name_split[1])

    for name, constr in block.constraints.items():
      tag = ''
      if name in error_constraints:
        tag = 'error'
        self.property.item(constraints_item, open=True)

      sloc = edgir.source_locator_of(block, name)
      item = self.property.insert(constraints_item, 'end', f'constraints{name}',
                                  text=name, values=(edgir.expr_to_string(constr), ), tag=tag)
      if f"{path}:{name}" in scp_constraints:
        for scp_expr in scp_constraints[f"{path}:{name}"]:
          self.item_expr.add(item, scp_expr)
      if sloc is not None:
        self.item_source.add(item, sloc)
