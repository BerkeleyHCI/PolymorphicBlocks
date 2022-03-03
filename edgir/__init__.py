from typing import Union, Tuple, Optional, Iterable, TYPE_CHECKING

from .common_pb2 import Empty, Metadata
from .init_pb2 import ValInit
from .name_pb2 import *
from .impl_pb2 import *
from .ref_pb2 import LibraryPath, LocalPath, LocalStep, CONNECTED_LINK, IS_CONNECTED, ALLOCATE, LENGTH, NAME
from .elem_pb2 import Port, PortArray, PortLike, Bundle, HierarchyBlock, BlockLike, Link, LinkLike
from .schema_pb2 import Library, Design
from .expr_pb2 import ConnectedExpr, ExportedExpr, ValueExpr, BinaryExpr, \
  BinarySetExpr, UnaryExpr, UnarySetExpr, MapExtractExpr
from .lit_pb2 import ValueLit

if TYPE_CHECKING:
  from .ref_pb2 import Reserved

  # Avoid a runtime circular import, these imports are done locally in scope
  # TODO this should be a separate util in edg_core
  from edg_core.Range import Range

PortTypes = Union[Port, PortArray, Bundle]
BlockTypes = HierarchyBlock
BlockLikeTypes = Union[BlockTypes, Link]
EltTypes = Union[PortTypes, BlockLikeTypes, ValInit]


def resolve_blocklike(block: BlockLike) -> BlockTypes:
  if block.HasField('hierarchy'):
    return block.hierarchy
  else:
    raise ValueError(f"bad blocklike {block}")


def resolve_linklike(link: LinkLike) -> Link:
  if link.HasField('link'):
    return link.link
  else:
    raise ValueError(f"bad linklike {link}")


def resolve_portlike(port: PortLike) -> PortTypes:
  if port.HasField('port'):
    return port.port
  elif port.HasField('array'):
    return port.array
  elif port.HasField('bundle'):
    return port.bundle
  else:
    raise ValueError(f"bad portlike {port}")


LitTypes = Union[bool, float, 'Range', str]  # TODO for Range: fix me, this prevents a circular import


def lit_assignment_from_expr(expr: ValueExpr) -> Optional[Tuple[LocalPath, LitTypes]]:
  if expr.HasField('binary') and expr.binary.op == BinaryExpr.EQ:
    rhs_lit = lit_from_expr(expr.binary.rhs)
    if expr.binary.lhs.HasField('ref') and rhs_lit is not None:
      # TODO: this only guarantees the expr structure, not that the lhs is reachable
      return (expr.binary.lhs.ref, rhs_lit)
    else:
      return None
  else:
    return None


def lit_from_expr(expr: ValueExpr) -> Optional[LitTypes]:
  if expr.HasField('literal'):
    return valuelit_to_lit(expr.literal)
  else:
    return None


def valuelit_to_lit(expr: ValueLit) -> Optional[LitTypes]:
  if expr.HasField('boolean'):
    return expr.boolean.val
  elif expr.HasField('floating'):
    return expr.floating.val
  elif expr.HasField('integer'):
    return expr.integer.val
  elif expr.HasField('range') and \
       expr.range.minimum.HasField('floating') and expr.range.maximum.HasField('floating'):
    from edg_core.Range import Range  # TODO fix me, this prevents a circular import
    return Range(expr.range.minimum.floating.val, expr.range.maximum.floating.val)
  elif expr.HasField('text'):
    return expr.text.val
  else:
    return None


def lit_to_valuelit(value: LitTypes) -> ValueLit:
  from edg_core.Range import Range  # TODO fix me, this prevents a circular import
  pb = ValueLit()
  if isinstance(value, bool):
    pb.boolean.val = value
  elif isinstance(value, int):
    pb.integer.val = value
  elif isinstance(value, float):
    pb.floating.val = value
  elif isinstance(value, Range):
    pb.range.minimum.floating.val = value.lower
    pb.range.maximum.floating.val = value.upper
  elif isinstance(value, str):
    pb.text.val = value
  else:
    raise ValueError(f"unknown lit {value}")
  return pb


def lit_to_expr(value: LitTypes) -> ValueExpr:
  pb = ValueExpr()
  pb.literal.CopyFrom(lit_to_valuelit(value))
  return pb


def valinit_to_type_string(elt: ValInit) -> str:
  if elt.HasField('boolean'):
    return 'Bool'
  elif elt.HasField('integer'):
    return 'Int'
  elif elt.HasField('floating'):
    return 'Float'
  elif elt.HasField('range'):
    return 'Range'
  elif elt.HasField('text'):
    return 'Text'
  else:
    return 'unknown'


def string_to_lit(input: str, elt: ValInit) -> Optional[LitTypes]:
  if elt.HasField('boolean'):
    if input.lower() == 'true':
      return True
    elif input.lower() == 'false':
      return False
    else:
      return None
  elif elt.HasField('integer'):
    try:
      return int(input)
    except ValueError:
      return None
  elif elt.HasField('floating'):
    try:
      return float(input)
    except ValueError:
      return None
  elif elt.HasField('range'):  # TODO: support tolerance notation and single values?
    from edg_core.Range import Range  # TODO fix me, this prevents a circular import
    elts = input.split(',')
    if len(elts) != 2:
      return None
    try:
      return Range(float(elts[0]), float(elts[1]))
    except ValueError:
      return None
  elif elt.HasField('text'):
    return input
  else:
    raise ValueError(f"unknown elt {elt}")


def lit_to_string(lit: LitTypes) -> str:
  import numbers
  from edg_core.Range import Range  # TODO fix me, this prevents a circular import
  if isinstance(lit, bool):
    return str(lit)
  elif isinstance(lit, Range):
    return f"{lit.lower:3g}, {lit.upper:3g}"
  elif isinstance(lit, numbers.Number):
    return str(lit)
  elif isinstance(lit, str):
    return lit
  else:
    raise ValueError(f"lit_to_string: unknown type for {lit}")


def expr_to_string(expr: ValueExpr) -> str:
  if expr.HasField('literal'):
    return str(lit_from_expr(expr))
  elif expr.HasField('unary'):
    un_op_prefix = {
      UnaryExpr.NEGATE: '-',
      UnaryExpr.NOT: '!',
    }
    un_op_fn_name = {
      UnaryExpr.MIN: 'min',
      UnaryExpr.MAX: 'max',
      UnaryExpr.CENTER: 'center',
      UnaryExpr.WIDTH: 'width',
    }

    if expr.unary.op in un_op_prefix:
      return f'({un_op_prefix[expr.unary.op]} {expr_to_string(expr.unary.val)})'
    elif expr.unary.op in un_op_fn_name:
      return f'{un_op_fn_name[expr.unary.op]}({expr_to_string(expr.unary.val)})'
    else:
      return f'{UnaryExpr.Op.Name(expr.unary.op)}({expr_to_string(expr.unary.val)})'
  elif expr.HasField('unary_set'):
    unset_op_fn_name = {
      UnarySetExpr.UNDEFINED: 'undef',
      UnarySetExpr.SUM: 'sum',
      UnarySetExpr.ALL_TRUE: 'all_true',
      UnarySetExpr.ANY_TRUE: 'any_true',
      UnarySetExpr.ALL_EQ: 'all_eq',
      UnarySetExpr.ALL_UNIQUE: 'all_unique',
      UnarySetExpr.MAXIMUM: 'max',
      UnarySetExpr.MINIMUM: 'min',
      UnarySetExpr.SET_EXTRACT: 'set_extract',
      UnarySetExpr.INTERSECTION: 'intersection',
      UnarySetExpr.HULL: 'null',
      UnarySetExpr.NEGATE: 'negate',
      UnarySetExpr.INVERT: 'invert',
      }

    if expr.unary_set.op in unset_op_fn_name:
      return f'{unset_op_fn_name[expr.unary_set.op]}({expr_to_string(expr.unary_set.vals)})'
    else:
      return f'{UnarySetExpr.Op.Name(expr.unary_set.op)}({expr_to_string(expr.unary_set.vals)})'
  elif expr.HasField('binary'):
    bin_op_infix = {
      BinaryExpr.ADD: '+',
        # BinaryExpr.SUB: '-',
      BinaryExpr.MULT: '*',
        # BinaryExpr.DIV: '/',
      BinaryExpr.AND: '&&',
      BinaryExpr.OR: '||',
      BinaryExpr.XOR: '^',
      BinaryExpr.IMPLIES: '->',
      BinaryExpr.EQ: '==',
      BinaryExpr.NEQ: '!=',
      BinaryExpr.GT: '>',
      BinaryExpr.GTE: '>=',
      BinaryExpr.LT: '<',
      BinaryExpr.LTE: '<=',
    }
    bin_op_fn_name = {
      BinaryExpr.UNDEFINED: 'undef',
      BinaryExpr.MAX: 'max',
      BinaryExpr.MIN: 'min',
      BinaryExpr.INTERSECTION: 'intersect',  # TODO maybe should be a symbol
      BinaryExpr.HULL: 'hull',
      BinaryExpr.WITHIN: 'within',
      BinaryExpr.RANGE: 'range',
    }
    if expr.binary.op in bin_op_infix:
      return f'({expr_to_string(expr.binary.lhs)} {bin_op_infix[expr.binary.op]} {expr_to_string(expr.binary.rhs)})'
    elif expr.binary.op in bin_op_fn_name:
      return f'{bin_op_fn_name[expr.binary.op]}({expr_to_string(expr.binary.lhs)}, {expr_to_string(expr.binary.rhs)})'
    else:
      return f'{BinaryExpr.Op.Name(expr.binary.op)}({expr_to_string(expr.binary.lhs)}, {expr_to_string(expr.binary.rhs)})'
  elif expr.HasField('binary_set'):
    binset_op_infix = {
      BinarySetExpr.ADD: '+',
      BinarySetExpr.MULT: '*',
    }
    binset_op_fn_name = {
      BinarySetExpr.UNDEFINED: 'undef',
    }
    if expr.binary_set.op in binset_op_infix:
      return f'({expr_to_string(expr.binary_set.lhset)} {binset_op_infix[expr.binary_set.op]} {expr_to_string(expr.binary_set.rhs)})'
    elif expr.binary_set.op in binset_op_fn_name:
      return f'{binset_op_fn_name[expr.binary_set.op]}({expr_to_string(expr.binary_set.lhset)}, {expr_to_string(expr.binary_set.rhs)})'
    else:
      return f'{BinarySetExpr.Op.Name(expr.binary_set.op)}({expr_to_string(expr.binary_set.lhset)}, {expr_to_string(expr.binary_set.rhs)})'
  elif expr.HasField('struct'):
    elt_strs = [f'{key}: {expr_to_string(val)}' for key, val in expr.struct.vals.items()]
    elt_str = ','.join(elt_strs)
    return f'{{{elt_str}}}'
  elif expr.HasField('range'):
    return f'range({expr_to_string(expr.range.minimum)}, {expr_to_string(expr.range.maximum)})'
  elif expr.HasField('ifThenElse'):
    return f'({expr_to_string(expr.ifThenElse.cond)} ? {expr_to_string(expr.ifThenElse.tru)} : {expr_to_string(expr.ifThenElse.fal)})'
  elif expr.HasField('extract'):
    return f'{expr_to_string(expr.extract.container)}[{expr_to_string(expr.extract.index)}]'
  elif expr.HasField('map_extract'):
    return f'[_.{local_path_to_str(expr.map_extract.path)} : {expr_to_string(expr.map_extract.container)}]'
  elif expr.HasField('connected'):
    return f'connected({expr_to_string(expr.connected.block_port)}, {expr_to_string(expr.connected.link_port)})'
  elif expr.HasField('exported'):
    return f'exported({expr_to_string(expr.exported.exterior_port)}, {expr_to_string(expr.exported.internal_block_port)})'
  elif expr.HasField('ref'):
    return local_path_to_str(expr.ref)
  else:
    raise ValueError(f"no format rule for {expr}")


def localpath_concat(*elts: Union[LocalPath, str, 'Reserved.V']) -> LocalPath:  # TODO workaround for broken enum typing
  result = LocalPath()
  for elt in elts:
    if isinstance(elt, LocalPath):
      for elt_elt in elt.steps:
        result.steps.add().CopyFrom(elt_elt)
    elif isinstance(elt, str):
      result.steps.add().name = elt
    elif elt in (CONNECTED_LINK, IS_CONNECTED, LENGTH, NAME, ALLOCATE):
      result.steps.add().reserved_param = elt
    else:
      raise ValueError(f"unknown localpath elt {elt}")
  return result


def localpath_slice(path: LocalPath, slice_from: int, slice_to: Optional[int] = None) -> LocalPath:
  if slice_to is None:
    slice_to = slice_from + 1
  rtn = LocalPath()
  for i in range(slice_from, slice_to):
    rtn.steps.add().CopyFrom(path.steps[i])
  return rtn


def libpath(name: str) -> LibraryPath:
  pb = LibraryPath()
  pb.target.name = name
  return pb


def LocalPathList(path: Iterable[Union[str, 'Reserved.V']]) -> LocalPath:
  pb = LocalPath()
  for step in path:
    if isinstance(step, str):
      pb.steps.add().name = step
    elif step in (CONNECTED_LINK, IS_CONNECTED, LENGTH, ALLOCATE):
      pb.steps.add().reserved_param = step
  return pb


def AssignLit(dst: Iterable[str], src: LitTypes) -> ValueExpr:
  pb = ValueExpr()
  pb.assign.dst.CopyFrom(LocalPathList(dst))
  pb.assign.src.CopyFrom(lit_to_expr(src))
  return pb


def AssignRef(dst: Iterable[str], src: Iterable[str]) -> ValueExpr:
  pb = ValueExpr()
  pb.assign.dst.CopyFrom(LocalPathList(dst))
  pb.assign.src.ref.CopyFrom(LocalPathList(src))
  return pb


def EqualsValueExpr(path: Iterable[str], value: Union[Iterable[str], float, Tuple[float, float], str]) -> ValueExpr:
  """Convenience shorthand constructor for a ValueExpr with a path on the lhs and a literal on the rhs"""
  import numbers

  pb = ValueExpr()
  pb.binary.op = BinaryExpr.EQ
  pb.binary.lhs.ref.CopyFrom(LocalPathList(path))

  if isinstance(value, bool):
    pb.binary.rhs.literal.boolean.val = value
  elif isinstance(value, numbers.Number):
    pb.binary.rhs.literal.floating.val = value
  elif isinstance(value, tuple) and isinstance(value[0], float) and isinstance(value[1], float):
    pb.binary.rhs.binary.op = BinaryExpr.RANGE
    pb.binary.rhs.binary.lhs.literal.floating.val = value[0]
    pb.binary.rhs.binary.rhs.literal.floating.val = value[1]
  elif isinstance(value, list) and isinstance(value[0], str):
    pb.binary.rhs.ref.CopyFrom(LocalPathList(value))
  elif isinstance(value, str):
    pb.binary.rhs.literal.text.val = value
  else:
    raise ValueError(f"unknown literal type {value}")

  return pb


def WithinValueExpr(path: Iterable[str], value: Union[Iterable[str], Tuple[float, float]]) -> ValueExpr:
  """Convenience shorthand constructor for a ValueExpr with a path on the lhs and a literal on the rhs"""
  pb = ValueExpr()
  pb.binary.op = BinaryExpr.WITHIN
  pb.binary.lhs.ref.CopyFrom(LocalPathList(path))

  if isinstance(value, tuple) and isinstance(value[0], float) and isinstance(value[1], float):
    pb.binary.rhs.binary.op = BinaryExpr.RANGE
    pb.binary.rhs.binary.lhs.literal.floating.val = value[0]
    pb.binary.rhs.binary.rhs.literal.floating.val = value[1]
  elif isinstance(value, list) and isinstance(value[0], str):
    pb.binary.rhs.ref.CopyFrom(LocalPathList(value))
  else:
    raise ValueError(f"unknown literal type {value}")

  return pb


def local_path_to_str(path: LocalPath) -> str:
  def step_to_str(step: LocalStep) -> str:
    if step.HasField('name'):
      return step.name
    elif step.HasField('reserved_param'):
      return {
        CONNECTED_LINK: '(link)',
        IS_CONNECTED: '(is_connected)'
      }[step.reserved_param]
    else:
      raise ValueError(f"unknown step {step}")

  return '.'.join([step_to_str(step) for step in path.steps])


def _namespace(meta: Metadata) -> Iterable[str]:
  namespace_elts = [v.namespace_order
                    for k, v in meta.members.node.items() if v.HasField('namespace_order')]
  if len(namespace_elts) == 1:
    return namespace_elts[0].names
  elif not namespace_elts:
    return []
  else:
    raise ValueError(f"multiple namespace_order entries {namespace_elts}")


def ordered_blocks(block: HierarchyBlock) -> Iterable[Tuple[str, BlockLike]]:
  """Returns a list of all sub-blocks (as BlockLike) in lexical order recorded by metadata.
  """
  names_sorted = _namespace(block.meta)
  assert set(block.blocks.keys()).issubset(names_sorted), f"sorted names {names_sorted} did not contain all blocks {list(block.blocks.keys())}"
  return [(name, block.blocks[name]) for name in names_sorted if name in block.blocks]


def ordered_links(block: Union[HierarchyBlock, Link]) -> Iterable[Tuple[str, LinkLike]]:
  """Returns a list of all sub-links (as LinkLike) in lexical order recorded by metadata.
  """
  names_sorted = _namespace(block.meta)
  assert set(block.links.keys()).issubset(names_sorted), f"sorted names {names_sorted} did not contain all links {list(block.links.keys())}"
  return [(name, block.links[name]) for name in names_sorted if name in block.links]


def ordered_params(block: Union[HierarchyBlock, Link, Port, Bundle]) -> Iterable[Tuple[str, ValInit]]:
  """Returns a list of all sub-params (as ValInit) in lexical order recorded by metadata.
  """
  names_sorted = _namespace(block.meta)
  assert set(block.params.keys()).issubset(names_sorted), f"sorted names {names_sorted} did not contain all params {list(block.params.keys())}"
  return [(name, block.params[name]) for name in names_sorted if name in block.params]


def ordered_ports(block: Union[HierarchyBlock, Link, Bundle]) -> Iterable[Tuple[str, PortLike]]:
  """Returns a list of all sub-ports (as PortLike) in lexical order recorded by metadata.
  """
  names_sorted = _namespace(block.meta)
  assert set(block.ports.keys()).issubset(names_sorted), f"sorted names {names_sorted} did not contain all ports {list(block.ports.keys())}"
  return [(name, block.ports[name]) for name in names_sorted if name in block.ports]


def source_locator_of(elt: Union[HierarchyBlock, Port, Link, Bundle], subelt_name: str) -> Optional[Tuple[str, int]]:
  """Returns the source locator of subelt_name in elt, as a tuple of (filepath, lineno).
  """
  if '_sourcelocator' not in elt.meta.members.node:
    return None
  if subelt_name not in elt.meta.members.node['_sourcelocator'].members.node:
    return None
  sloc_str = elt.meta.members.node['_sourcelocator'].members.node[subelt_name].text_leaf
  sloc_split = sloc_str.rpartition(':')
  sloc_file = sloc_split[0].strip()
  sloc_line = int(sloc_split[2].strip())
  return sloc_file, sloc_line
