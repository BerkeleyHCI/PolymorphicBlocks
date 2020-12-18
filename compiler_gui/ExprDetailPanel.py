from tkinter import X, Y, BOTH, TOP, BOTTOM, HORIZONTAL, VERTICAL, RIGHT, Toplevel, Menu
from tkinter import ttk

import os
from edg_core import TransformUtil as tfu
from .Utils import *
from edg_core import SimpleConstProp as scp


class ExprDetailPanel:
  @classmethod
  def create_window(cls, parent, expr: Union[tfu.Path, scp.ScpValueExpr], vals: SimpleConstPropTransform,
                    backedge: Optional[scp.ScpConstraint] = None, seen: FrozenSet[tfu.Path] = frozenset()):
    new_window = Toplevel(parent)
    expr_panel = ExprDetailPanel(new_window)
    if isinstance(expr, tfu.Path):
      expr_panel.load_param(expr, vals, backedge, seen)
    else:
      expr_panel.load_expr(expr, vals)
    expr_panel.frame.pack(fill=BOTH, expand=True)

  def __init__(self, parent) -> None:
    self.frame = ttk.Frame(parent)
    self.label = ttk.Label(self.frame)
    self.label.pack(side=TOP, fill=X)
    self.label.bind('<Configure>', self._set_label_wrap)

    self.tree = ttk.Treeview(self.frame, columns=('value'))  # TODO refactor keys so not storing both relpath and path
    self.tree.heading('value', text='Value')
    self.context_menu = Menu(self.tree, tearoff=False)
    self.context_menu_len = 0
    self.tree.bind('<Double-1>', self._on_dclick)
    self.tree.bind('<Button-3>', self._on_rclick)

    self.hbar = ttk.Scrollbar(self.frame, orient=HORIZONTAL, command=self.tree.xview)
    self.hbar.pack(side=BOTTOM, fill=X)
    self.vbar = ttk.Scrollbar(self.frame, orient=VERTICAL, command=self.tree.yview)
    self.vbar.pack(side=RIGHT, fill=Y)

    self.tree.pack(expand=True, fill=BOTH)
    self.tree.configure(yscrollcommand=self.vbar.set, xscrollcommand=self.hbar.set)

    self.item_path: MultiBiDict[Any, Tuple[tfu.Path, Optional[scp.ScpConstraint], FrozenSet[tfu.Path]]] = MultiBiDict()
    self.item_source: MultiBiDict[Any, Tuple[str, int]] = MultiBiDict()

    self.vals: Optional[SimpleConstPropTransform] = None

    self.clear()

  def _set_label_wrap(self, event):
    event.widget.configure(wraplength=event.width)

  def _on_dclick(self, event):
    selected = self.tree.focus()
    if selected in self.item_path:
      assert self.vals is not None
      selected_path, backedge, seen = self.item_path[selected]
      self.create_window(self.tree, selected_path, self.vals, backedge, seen)


  def _on_rclick(self, event):
    selected = self.tree.identify_row(event.y)  # _on_click is called before the row is selected

    for i in range(self.context_menu_len):
      self.context_menu.delete(0)
    self.context_menu_len = 0

    if selected in self.item_path:
      assert self.vals is not None
      selected_path, backedge, seen = self.item_path[selected]
      self.context_menu.add_command(label=f"Open constraint tracer at {selected_path}",
                                    command=lambda : self.create_window(self.tree, selected_path, self.vals, backedge, seen))
      self.context_menu_len += 1

    if selected in self.item_source:
      sloc_filepath, sloc_line = self.item_source[selected]
      if self.context_menu_len > 0:
        self.context_menu.add_separator()
        self.context_menu_len += 1
      self.context_menu.add_command(label=f"Open definition at {os.path.split(sloc_filepath)[-1]}: {sloc_line}",
                                    command=open_source_locator_wrapper(sloc_filepath, sloc_line))
      self.context_menu_len += 1

    if self.context_menu_len > 0:
      self.context_menu.post(event.x_root, event.y_root)

  def clear(self) -> None:
    self.tree.delete(*self.tree.get_children())
    self.label.config(text="Expr Detail")

    self.item_path.clear()
    self.vals = None

  def _insert_expr(self, parent: Any, eval_param_fn: scp.EvalFnType, expr: scp.ScpExpr,
                   backedge: Optional[scp.ScpConstraint], seen: FrozenSet[tfu.Path]):
    expr_value_str = scp.expr_result_to_str(expr.eval(eval_param_fn))
    expr_elts: List[Tuple[str, scp.ScpExpr]]
    expr_path: Optional[tfu.Path] = None
    if isinstance(expr, scp.ScpPath):
      expr_name = f'Path: {expr.path}'
      expr_elts = []
      expr_path = expr.path
    elif isinstance(expr, scp.ScpRawLiteral):
      expr_name = f'RawLiteral: {expr.val}'
      expr_elts = []
    elif isinstance(expr, scp.ScpLiteral):
      expr_name = f'Literal: {expr.val}'
      expr_elts = []
    elif isinstance(expr, scp.ScpBinaryOp):
      expr_name = f'Binary({edgir.BinaryExpr.Op.Name(expr.op)})'
      expr_elts = [('lhs', expr.lhs), ('rhs', expr.rhs)]
    elif isinstance(expr, scp.ScpIfThenElse):
      expr_name = f'IfThenElse'
      expr_elts = [('cond', expr.cond), ('true', expr.tru), ('false', expr.fal)]
    elif isinstance(expr, scp.ScpReduceOp):
      expr_name = f'Reduce({edgir.ReductionExpr.Op.Name(expr.op)})'
      expr_elts = [('vals', expr.vals)]
    elif isinstance(expr, scp.ScpMapExtract):
      expr_name = f'MapExtract({expr.extract_ref})'
      expr_elts = [(str(index), elt_expr) for index, elt_expr in enumerate(expr.elt_exprs)]
    elif isinstance(expr, scp.ScpIsConnected):
      expr_name = f'IsConnected: {expr.target}'
      expr_elts = []
    elif isinstance(expr, scp.ScpRef):
      expr_name = f'Ref: {expr.target}'
      expr_elts = []
      expr_path = expr.target
    else:
      expr_name = f'unknown {type(expr)}'
      expr_elts = []

    expr_item = self.tree.insert(parent, 'end', text=expr_name, values=(expr_value_str,), open=True)
    for name, expr_elt in expr_elts:
      self._insert_expr(expr_item, eval_param_fn, expr_elt, backedge, seen)
    if expr_path is not None:
      self.item_path.add(expr_item, (expr_path, backedge, seen))

  def _insert_constraint(self, parent: Any, eval_param_fn: scp.EvalFnType, constr: scp.ScpConstraint,
                         backedge: Optional[scp.ScpConstraint], seen: FrozenSet[tfu.Path]):
    if isinstance(constr, scp.ScpAssign):
      constr_type = 'assign'
    elif isinstance(constr, scp.ScpSubset):
      constr_type = 'subset'
    else:
      constr_type = f'unknown constraint {type(constr)}'

    constr_value_str = scp.expr_result_to_str(constr.eval(eval_param_fn))
    constr_item = self.tree.insert(parent, 'end', text=f'{constr.get_name()}: {constr_type}', values=(constr_value_str,), open=True)
    constr_sloc = constr.get_source_locator()
    if constr_sloc is not None:
      self.item_source.add(constr_item, constr_sloc)
    self._insert_expr(constr_item, eval_param_fn, constr.expr, backedge, seen)

  def load_param(self, path: tfu.Path, vals: SimpleConstPropTransform,
                 backedge: Optional[scp.ScpConstraint] = None, seen: FrozenSet[tfu.Path] = frozenset()) -> None:
    self.clear()

    path_val = vals.resolve_param(path, backedge, set(seen))
    self.label.config(text=f"Expr Detail: {path}\n={path_val}\nwith backedge {backedge}, seen {seen}")
    self.vals = vals

    seen = seen.union([path])

    # TODO maybe separate this from SCP internals?
    for constr in vals.param_exprs.get(path, set()):
      new_backedge = vals.backedge_of_constr(path, constr)
      eval_param_fn = lambda eval_path: vals.resolve_param(eval_path, new_backedge, set(seen))

      if constr == backedge:
        pruned_item = self.tree.insert('', 'end', text='pruned backedge')
        self._insert_constraint(pruned_item, eval_param_fn, constr, new_backedge, seen)
      else:
        self._insert_constraint('', eval_param_fn, constr, new_backedge, seen)

  def load_expr(self, expr: scp.ScpExpr, vals: SimpleConstPropTransform) -> None:
    self.clear()
    self.label.config(text=f"Expr Detail")
    self.vals = vals
    eval_param_fn = lambda eval_path: vals.resolve_param(eval_path)

    self._insert_expr('', eval_param_fn, expr, None, frozenset())
