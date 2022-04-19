from typing import Union, Tuple, Optional, Iterable, TYPE_CHECKING, List, cast

from .common_pb2 import Empty, Metadata
from .init_pb2 import ValInit
from .name_pb2 import *
from .impl_pb2 import *
from .ref_pb2 import LibraryPath, LocalPath, LocalStep, CONNECTED_LINK, IS_CONNECTED, LENGTH, ALLOCATED, NAME
from .elem_pb2 import Port, PortArray, PortLike, Bundle, HierarchyBlock, BlockLike, Link, LinkArray, LinkLike
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
LinkTypes = Union[Link, LinkArray]  # LinkArray is not block-like b/c it doesn't have a class and params
EltTypes = Union[PortTypes, BlockLikeTypes, LinkArray, ValInit]


def resolve_blocklike(block: BlockLike) -> BlockTypes:
  if block.HasField('hierarchy'):
    return block.hierarchy
  else:
    raise ValueError(f"bad blocklike {block}")


def resolve_linklike(link: LinkLike) -> LinkTypes:
  if link.HasField('link'):
    return link.link
  if link.HasField('array'):
    return link.array
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


LitLeafTypes = Union[bool, float, 'Range', str]  # TODO for Range: fix me, this prevents a circular import
LitTypes = Union[LitLeafTypes, List[LitLeafTypes]]


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
  elif expr.HasField('array'):
    elts = [valuelit_to_lit(elt) for elt in expr.array.elts]
    if None in elts:
      return None
    else:
      return cast(List[LitLeafTypes], elts)
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
  elif isinstance(value, list):
    for elt in value:
      pb.array.elts.add().CopyFrom(lit_to_valuelit(elt))
  else:
    raise ValueError(f"unknown lit {value}")
  return pb


def lit_to_expr(value: LitTypes) -> ValueExpr:
  pb = ValueExpr()
  pb.literal.CopyFrom(lit_to_valuelit(value))
  return pb


class Allocate:
  """Wrapper around the Allocate LocalPath, for internal use"""
  def __init__(self, suggested_name: Optional[str] = None):
    if suggested_name is None:
      self.suggested_name = ""  # for now, no suggested name is represented as empty-string
    else:
      self.suggested_name = suggested_name


def localpath_concat(*elts: Union[LocalPath, str, Allocate, 'Reserved.V']) -> LocalPath:  # TODO workaround for broken enum typing
  result = LocalPath()
  for elt in elts:
    if isinstance(elt, LocalPath):
      for elt_elt in elt.steps:
        result.steps.add().CopyFrom(elt_elt)
    elif isinstance(elt, str):
      result.steps.add().name = elt
    elif isinstance(elt, Allocate):
      result.steps.add().allocate = elt.suggested_name
    elif elt in (CONNECTED_LINK, IS_CONNECTED, LENGTH, ALLOCATED, NAME):
      result.steps.add().reserved_param = elt
    else:
      raise ValueError(f"unknown localpath elt {elt}")
  return result


def libpath(name: str) -> LibraryPath:
  pb = LibraryPath()
  pb.target.name = name
  return pb


def LocalPathList(path: Iterable[Union[str, Allocate, 'Reserved.V']]) -> LocalPath:
  pb = LocalPath()
  for step in path:
    if isinstance(step, str):
      pb.steps.add().name = step
    elif isinstance(step, Allocate):
      pb.steps.add().allocate = step.suggested_name
    elif step in (CONNECTED_LINK, IS_CONNECTED, LENGTH):
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
