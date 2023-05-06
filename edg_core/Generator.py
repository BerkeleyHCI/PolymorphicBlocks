from __future__ import annotations

from typing import *

from deprecated import deprecated

import edgir
from . import IdentityDict
from .Binding import InitParamBinding, AllocatedBinding, IsConnectedBinding
from .Blocks import BlockElaborationState, AbstractBlockProperty
from .ConstraintExpr import ConstraintExpr
from .Core import non_library
from .HdlUserExceptions import *
from .HierarchyBlock import Block


ExprType = TypeVar('ExprType', bound=ConstraintExpr, covariant=True)
WrappedType = TypeVar('WrappedType', bound=Any)
class GeneratorParam(Generic[ExprType]):
  # TODO: currently this is compositional (has-a expr), but it may make sense for this to be-a expr with a .get()
  def __init__(self, expr: ExprType):
    self._expr = expr
    self._value: Optional[Any] = None  # set externally

  def get(self: GeneratorParam[ConstraintExpr[WrappedType, Any]]) -> WrappedType:
    assert self._value is not None, "parameter has no value"
    return self._value

  def expr(self) -> ExprType:
    return self._expr


CastableType = TypeVar('CastableType', bound=Any)
@non_library
class GeneratorBlock(Block):
  """Block which allows arbitrary Python code to generate its internal subcircuit,
  and unlike regular Blocks can rely on Python values of solved parameters.
  """
  def __init__(self):
    super().__init__()
    self._generator: Optional[GeneratorBlock.GeneratorRecord] = None
    self._generator_params = self.manager.new_dict(GeneratorParam)
    self._generator_params_list: list[ConstraintExpr] = []
    self._generator_param_values = IdentityDict[ConstraintExpr, Any]()

  from .ConstraintExpr import RangeLike, RangeExpr, IntExpr, BoolExpr, BoolLike, IntLike, FloatExpr, \
    FloatLike, StringExpr, StringLike
  from .ArrayExpr import ArrayRangeExpr, ArrayRangeLike, ArrayBoolExpr, ArrayBoolLike, ArrayFloatExpr, ArrayIntExpr, \
    ArrayIntLike, ArrayFloatLike, ArrayStringLike, ArrayStringExpr

  # all the case need to be defined since it can't infer the types when there's a *Like
  # type ignore is needed because IntLike overlaps BoolLike
  @overload
  def GeneratorParam(self, param: RangeLike) -> GeneratorParam[RangeExpr, Range]: ...  # type: ignore
  @overload
  def GeneratorParam(self, param: BoolLike) -> GeneratorParam[BoolExpr, bool]: ...  # type: ignore
  @overload
  def GeneratorParam(self, param: IntLike) -> GeneratorParam[IntExpr, int]: ...  # type: ignore
  @overload
  def GeneratorParam(self, param: FloatLike) -> GeneratorParam[FloatExpr, float]: ...  # type: ignore
  @overload
  def GeneratorParam(self, param: StringLike) -> GeneratorParam[StringExpr, str]: ...  # type: ignore
  @overload
  def GeneratorParam(self, param: ArrayRangeLike) -> GeneratorParam[ArrayRangeExpr, list[Range]]: ...  # type: ignore
  @overload
  def GeneratorParam(self, param: ArrayBoolLike) -> GeneratorParam[ArrayBoolExpr, list[bool]]: ...  # type: ignore
  @overload
  def GeneratorParam(self, param: ArrayIntLike) -> GeneratorParam[ArrayIntExpr, list[int]]: ...  # type: ignore
  @overload
  def GeneratorParam(self, param: ArrayFloatLike) -> GeneratorParam[ArrayFloatExpr, list[float]]: ...  # type: ignore
  @overload
  def GeneratorParam(self, param: ArrayStringLike) -> GeneratorParam[ArrayStringExpr, list[str]]: ...  # type: ignore

  def GeneratorParam(self, param: Union[ConstraintExpr, Any]) -> GeneratorParam:
    """Declares some parameter to be a generator, returning its GeneratorParam wrapper that
    can be .get()'d from within the generate() function."""
    if self._elaboration_state not in (BlockElaborationState.init, BlockElaborationState.contents):
      raise BlockDefinitionError(self, "can't call GeneratorParameter(...) outside __init__ or contents",
                                 "call GeneratorParameter(...) inside __init__ or contents only, and remember to call super().__init__()")
    if not isinstance(param, ConstraintExpr):
      raise TypeError(f"param to GeneratorParameter(...) must be ConstraintExpr, got {param} of type {type(param)}")
    if param.binding is None:
      raise BlockDefinitionError(self, "GeneratorParameter(...) param must be bound")
    if not isinstance(param.binding, (InitParamBinding, AllocatedBinding, IsConnectedBinding)):
      raise BlockDefinitionError(self, "GeneratorParameter(...) param must be an __init__ param, port requested, or port is_connected")

    elt = GeneratorParam(param)  # type: ignore
    self._generator_params.register(elt)  # type: ignore

    return elt

  def generator_param(self, *params: ConstraintExpr) -> None:
    """Declares some parameter to be a generator, so in generate() it can be used in self.get().
    Parameters that have not been called in generator_param will error out if used in self.get()."""
    if self._elaboration_state not in (BlockElaborationState.init, BlockElaborationState.contents):
      raise BlockDefinitionError(self, "can't call generator_param(...) outside __init__ or contents",
                                 "call generator_param(...) inside __init__ or contents only, and remember to call super().__init__()")
    for param in params:
      if not isinstance(param, ConstraintExpr):
        raise TypeError(f"param to generator_param(...) must be ConstraintExpr, got {param} of type {type(param)}")
      if param.binding is None:
        raise BlockDefinitionError(self, "generator_param(...) param must be bound")
      if not isinstance(param.binding, (InitParamBinding, AllocatedBinding, IsConnectedBinding)):
        raise BlockDefinitionError(self, "generator_param(...) param must be an __init__ param, port requested, or port is_connected")

      self._generator_params_list.append(param)

  def get(self, param: ConstraintExpr[WrappedType, Any]) -> WrappedType:
    ...

  # Generator dependency data
  #
  class GeneratorRecord(NamedTuple):
    fn: Callable
    req_params: Tuple[ConstraintExpr, ...]  # all required params for generator to fire
    fn_args: Tuple[ConstraintExpr, ...]  # params to unpack for the generator function

  @deprecated(reason="use self.GeneratorParam(...) instead")
  def generator(self, fn: Callable[..., None], *reqs: Any) -> None:  # type: ignore
    """
    Registers a generator function
    :param fn: function (of self) to invoke, where the parameter list lines up with reqs
    :param reqs: required parameters, the value of which are passed to the generator function

    Note, generator parameters must be __init__ parameters because the block is not traversed before generation,
    and any internal constraints (like parameter assignments from within) are not evaluated.
    """
    assert callable(fn), f"fn {fn} must be a method (callable)"
    assert self._generator is None, f"redefinition of generator, multiple generators not allowed"

    for (i, req_param) in enumerate(reqs):
      assert isinstance(req_param.binding, InitParamBinding) or \
             (isinstance(req_param.binding, (AllocatedBinding, IsConnectedBinding))
              and req_param.binding.src._parent is self), \
        f"generator parameter {i} {req_param} not an __init__ parameter (or missing @init_in_parent)"
    self._generator = GeneratorBlock.GeneratorRecord(fn, reqs, reqs)

  def generate(self):
    """Generate function which has access to the value of generator params. Implement me."""
    pass

  # Generator serialization and parsing
  #
  def _def_to_proto(self) -> edgir.HierarchyBlock:
    if self._elaboration_state != BlockElaborationState.post_generate:  # only write generator on the stub definition
      pb = edgir.HierarchyBlock()
      ref_map = self._get_ref_map(edgir.LocalPath())
      pb = self._populate_def_proto_block_base(pb)
      pb.generator.SetInParent()  # even if rest of the fields are empty, make sure to create a record

      if self._generator is not None:  # legacy generator style
        assert len(self._generator_params.items()) == 0, "self.generator() must not have GeneratorParams"
        for req_param in self._generator.req_params:
          pb.generator.required_params.add().CopyFrom(ref_map[req_param])
      elif type(self).generate is not GeneratorBlock.generate:
        for name, gen_param in self._generator_params.items():
          pb.generator.required_params.add().CopyFrom(ref_map[gen_param._expr])
        for param in self._generator_params_list:
          pb.generator.required_params.add().CopyFrom(ref_map[param])
      elif (self.__class__, AbstractBlockProperty) in self._elt_properties:
        pass  # abstract blocks allowed to not define a generator
      else:
        raise BlockDefinitionError(self, "Generator missing generate implementation", "define generate")
      return pb
    else:
      return super()._def_to_proto()

  def _generated_def_to_proto(self, generate_values: Iterable[Tuple[edgir.LocalPath, edgir.ValueLit]]) -> \
      edgir.HierarchyBlock:
    assert self._elaboration_state == BlockElaborationState.post_init  # TODO dedup w/ elaborated_def_to_proto
    self._elaboration_state = BlockElaborationState.contents

    self.contents()

    self._elaboration_state = BlockElaborationState.generate

    # Translate parameter values to function arguments
    ref_map = self._get_ref_map(edgir.LocalPath())
    generate_values_map = {path.SerializeToString(): value for (path, value) in generate_values}

    assert (self.__class__, AbstractBlockProperty) not in self._elt_properties  # abstract blocks can't generate
    if self._generator is not None:  # legacy generator style
      fn_args = [arg_param._from_lit(generate_values_map[ref_map[arg_param].SerializeToString()])
                 for arg_param in self._generator.fn_args]
      self._generator.fn(*fn_args)
    elif type(self).generate is not GeneratorBlock.generate:
      for name, gen_param in self._generator_params.items():
        gen_param._value = gen_param._expr._from_lit(generate_values_map[ref_map[gen_param._expr].SerializeToString()])
      self.generate()
    else:
      raise BlockDefinitionError(self, "Generator missing generate implementation", "define generate")

    self._elaboration_state = BlockElaborationState.post_generate

    return self._def_to_proto()
