from typing import Union, Optional, Iterable, TYPE_CHECKING, List, cast, overload

from google.protobuf.internal.containers import RepeatedCompositeFieldContainer

from .common_pb2 import Empty, Metadata
from .init_pb2 import ValInit
from .name_pb2 import *
from .impl_pb2 import *
from .ref_pb2 import LibraryPath, LocalPath, LocalStep, CONNECTED_LINK, IS_CONNECTED, LENGTH, ALLOCATED, NAME
from .elem_pb2 import Port, PortArray, PortLike, Bundle, HierarchyBlock, BlockLike, Link, LinkArray, LinkLike, \
  NamedPortLike, NamedValInit, NamedValueExpr, NamedBlockLike, NamedLinkLike
from .schema_pb2 import Library, Design
from .expr_pb2 import ConnectedExpr, ExportedExpr, ValueExpr, BinaryExpr, \
  BinarySetExpr, UnaryExpr, UnarySetExpr, MapExtractExpr
from .lit_pb2 import ValueLit

if TYPE_CHECKING:
  from .ref_pb2 import Reserved

  # Avoid a runtime circular import, these imports are done locally in scope
  # TODO this should be a separate util in edg_core
  from ..core.Range import Range

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
  elif link.HasField('array'):
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


def valuelit_to_lit(expr: ValueLit) -> LitTypes:
  if expr.HasField('boolean'):
    return expr.boolean.val
  elif expr.HasField('floating'):
    return expr.floating.val
  elif expr.HasField('integer'):
    return expr.integer.val
  elif expr.HasField('range') and \
          expr.range.minimum.HasField('floating') and expr.range.maximum.HasField('floating'):
    from ..core.Range import Range  # TODO fix me, this prevents a circular import
    return Range(expr.range.minimum.floating.val, expr.range.maximum.floating.val)
  elif expr.HasField('text'):
    return expr.text.val
  elif expr.HasField('array'):
    elts = [valuelit_to_lit(elt) for elt in expr.array.elts]
    if None in elts:
      raise ValueError(f"bad valuelit array {expr}")
    else:
      return cast(List[LitLeafTypes], elts)
  else:
    raise ValueError(f"bad valuelit {expr}")


def lit_to_valuelit(value: LitTypes) -> ValueLit:
  from ..core.Range import Range  # TODO fix me, this prevents a circular import
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
    pb.array.SetInParent()
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


def local_path_to_str_list(path: LocalPath) -> List[str]:
  """Convert a LocalPath to a list of its components. Reserved params are presented as strings."""
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
  return [step_to_str(step) for step in path.steps]

def local_path_to_str(path: LocalPath) -> str:
  return '.'.join(local_path_to_str_list(path))

@overload
def add_pair(pb: RepeatedCompositeFieldContainer[NamedPortLike], name: str) -> PortLike: ...
@overload
def add_pair(pb: RepeatedCompositeFieldContainer[NamedBlockLike], name: str) -> BlockLike: ...
@overload
def add_pair(pb: RepeatedCompositeFieldContainer[NamedLinkLike], name: str) -> LinkLike: ...
@overload
def add_pair(pb: RepeatedCompositeFieldContainer[NamedValInit], name: str) -> ValInit: ...
@overload
def add_pair(pb: RepeatedCompositeFieldContainer[NamedValueExpr], name: str) -> ValueExpr: ...

def add_pair(pb: Union[
  RepeatedCompositeFieldContainer[NamedPortLike],
  RepeatedCompositeFieldContainer[NamedBlockLike],
  RepeatedCompositeFieldContainer[NamedLinkLike],
  RepeatedCompositeFieldContainer[NamedValInit],
  RepeatedCompositeFieldContainer[NamedValueExpr]
], name: str) -> Union[
  PortLike, BlockLike, LinkLike, ValInit, ValueExpr
]:
  elt = pb.add()
  elt.name = name
  return elt.value


@overload
def pair_get(pb: RepeatedCompositeFieldContainer[NamedPortLike], name: str) -> PortLike: ...
@overload
def pair_get(pb: RepeatedCompositeFieldContainer[NamedBlockLike], name: str) -> BlockLike: ...
@overload
def pair_get(pb: RepeatedCompositeFieldContainer[NamedLinkLike], name: str) -> LinkLike: ...
@overload
def pair_get(pb: RepeatedCompositeFieldContainer[NamedValInit], name: str) -> ValInit: ...
@overload
def pair_get(pb: RepeatedCompositeFieldContainer[NamedValueExpr], name: str) -> ValueExpr: ...

def pair_get(pb: Union[
  RepeatedCompositeFieldContainer[NamedPortLike],
  RepeatedCompositeFieldContainer[NamedBlockLike],
  RepeatedCompositeFieldContainer[NamedLinkLike],
  RepeatedCompositeFieldContainer[NamedValInit],
  RepeatedCompositeFieldContainer[NamedValueExpr]
], name: str) -> Union[
  PortLike, BlockLike, LinkLike, ValInit, ValueExpr
]:
  for elt in pb:
    if elt.name == name:
      return elt.value
  raise KeyError(name)


@overload
def pair_get_opt(pb: RepeatedCompositeFieldContainer[NamedPortLike], name: str) -> Optional[PortLike]: ...
@overload
def pair_get_opt(pb: RepeatedCompositeFieldContainer[NamedBlockLike], name: str) -> Optional[BlockLike]: ...
@overload
def pair_get_opt(pb: RepeatedCompositeFieldContainer[NamedLinkLike], name: str) -> Optional[LinkLike]: ...
@overload
def pair_get_opt(pb: RepeatedCompositeFieldContainer[NamedValInit], name: str) -> Optional[ValInit]: ...
@overload
def pair_get_opt(pb: RepeatedCompositeFieldContainer[NamedValueExpr], name: str) -> Optional[ValueExpr]: ...

def pair_get_opt(pb: Union[
  RepeatedCompositeFieldContainer[NamedPortLike],
  RepeatedCompositeFieldContainer[NamedBlockLike],
  RepeatedCompositeFieldContainer[NamedLinkLike],
  RepeatedCompositeFieldContainer[NamedValInit],
  RepeatedCompositeFieldContainer[NamedValueExpr]
], name: str) -> Union[
  Optional[PortLike], Optional[BlockLike], Optional[LinkLike], Optional[ValInit], Optional[ValueExpr]
]:
  for elt in pb:
    if elt.name == name:
      return elt.value
  return None
