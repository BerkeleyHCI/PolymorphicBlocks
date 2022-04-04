from __future__ import annotations

from numbers import Number
from typing import *

import edgir
from .Array import ArrayExpr
from .Binding import InitParamBinding, AllocatedBinding, IsConnectedBinding, NameBinding
from .Blocks import BlockElaborationState
from .ConstraintExpr import ConstraintExpr, BoolExpr, FloatExpr, IntExpr, RangeExpr, StringExpr
from .Core import non_library
from .Exceptions import *
from .HierarchyBlock import Block
from .IdentityDict import IdentityDict
from .Ports import BasePort, Port
from .Range import Range


@non_library
class GeneratorBlock(Block):
  """Part which generates into a subcircuit, given fully resolved parameters.
  Generation happens after a solver run.
  Allows much more power and customization in the elaboration of a subcircuit.
  """
  def __init__(self):
    super().__init__()
    self._param_values: Optional[IdentityDict[ConstraintExpr, edgir.LitTypes]] = None
    self._generator: Optional[GeneratorBlock.GeneratorRecord] = None

  # Generator dependency data
  #
  class GeneratorRecord(NamedTuple):
    fn: Callable
    req_params: Tuple[ConstraintExpr, ...]  # all required params for generator to fire
    req_ports: Tuple[BasePort, ...]  # all required ports for generator to fire
    fn_args: Tuple[ConstraintExpr, ...]  # params to unpack for the generator function

  ConstrType1 = TypeVar('ConstrType1', bound=Any)
  ConstrCastable1 = TypeVar('ConstrCastable1', bound=Any)
  ConstrType2 = TypeVar('ConstrType2', bound=Any)
  ConstrCastable2 = TypeVar('ConstrCastable2', bound=Any)
  ConstrType3 = TypeVar('ConstrType3', bound=Any)
  ConstrCastable3 = TypeVar('ConstrCastable3', bound=Any)
  ConstrType4 = TypeVar('ConstrType4', bound=Any)
  ConstrCastable4 = TypeVar('ConstrCastable4', bound=Any)
  ConstrType5 = TypeVar('ConstrType5', bound=Any)
  ConstrCastable5 = TypeVar('ConstrCastable5', bound=Any)
  ConstrType6 = TypeVar('ConstrType6', bound=Any)
  ConstrCastable6 = TypeVar('ConstrCastable6', bound=Any)
  ConstrType7 = TypeVar('ConstrType7', bound=Any)
  ConstrCastable7 = TypeVar('ConstrCastable7', bound=Any)
  ConstrType8 = TypeVar('ConstrType8', bound=Any)
  ConstrCastable8 = TypeVar('ConstrCastable8', bound=Any)
  ConstrType9 = TypeVar('ConstrType9', bound=Any)
  ConstrCastable9 = TypeVar('ConstrCastable9', bound=Any)
  ConstrType10 = TypeVar('ConstrType10', bound=Any)
  ConstrCastable10 = TypeVar('ConstrCastable10', bound=Any)

  # These are super ugly, both in that it's manually enumerating all the possible argument numbers
  # (but there's precedent in how Scala's libraries are written!) and that the generator can't actually take
  # the *Like types (eg, BoolLike - it can only take a BoolExpr), but this is needed to allow the *Like types
  # in constructor argument lists, and avoid piping them through to an explicit parameter.
  # While @init_in_parent remaps the arguments from a *Like type in the input to a *Expr type into the constructor,
  # expressing that function signature remapping isn't quite possible with mypy.
  # So this is the least worst option, a bit more ugliness for the advanced generator functionality rather than
  # for the common case of block definition.
  @overload
  def generator(self, fn: Callable[[], None]) -> None: ...
  @overload
  def generator(self, fn: Callable[[ConstrType1], None],
                req1: Union[ConstrCastable1, ConstraintExpr[ConstrType1, ConstrCastable1]]) -> None: ...
  @overload
  def generator(self, fn: Callable[[ConstrType1, ConstrType2], None],
                req1: Union[ConstrCastable1, ConstraintExpr[ConstrType1, ConstrCastable1]],
                req2: Union[ConstrCastable2, ConstraintExpr[ConstrType2, ConstrCastable2]]) -> None: ...
  @overload
  def generator(self, fn: Callable[[ConstrType1, ConstrType2, ConstrType3], None],
                req1: Union[ConstrCastable1, ConstraintExpr[ConstrType1, ConstrCastable1]],
                req2: Union[ConstrCastable2, ConstraintExpr[ConstrType2, ConstrCastable2]],
                req3: Union[ConstrCastable3, ConstraintExpr[ConstrType3, ConstrCastable3]]) -> None: ...
  @overload
  def generator(self, fn: Callable[[ConstrType1, ConstrType2, ConstrType3, ConstrType4], None],
                req1: Union[ConstrCastable1, ConstraintExpr[ConstrType1, ConstrCastable1]],
                req2: Union[ConstrCastable2, ConstraintExpr[ConstrType2, ConstrCastable2]],
                req3: Union[ConstrCastable3, ConstraintExpr[ConstrType3, ConstrCastable3]],
                req4: Union[ConstrCastable4, ConstraintExpr[ConstrType4, ConstrCastable4]]) -> None: ...
  @overload
  def generator(self, fn: Callable[[ConstrType1, ConstrType2, ConstrType3, ConstrType4,
                                    ConstrType5], None],
                req1: Union[ConstrCastable1, ConstraintExpr[ConstrType1, ConstrCastable1]],
                req2: Union[ConstrCastable2, ConstraintExpr[ConstrType2, ConstrCastable2]],
                req3: Union[ConstrCastable3, ConstraintExpr[ConstrType3, ConstrCastable3]],
                req4: Union[ConstrCastable4, ConstraintExpr[ConstrType4, ConstrCastable4]],
                req5: Union[ConstrCastable5, ConstraintExpr[ConstrType5, ConstrCastable5]]) -> None: ...
  @overload
  def generator(self, fn: Callable[[ConstrType1, ConstrType2, ConstrType3, ConstrType4,
                                    ConstrType5, ConstrType6], None],
                req1: Union[ConstrCastable1, ConstraintExpr[ConstrType1, ConstrCastable1]],
                req2: Union[ConstrCastable2, ConstraintExpr[ConstrType2, ConstrCastable2]],
                req3: Union[ConstrCastable3, ConstraintExpr[ConstrType3, ConstrCastable3]],
                req4: Union[ConstrCastable4, ConstraintExpr[ConstrType4, ConstrCastable4]],
                req5: Union[ConstrCastable5, ConstraintExpr[ConstrType5, ConstrCastable5]],
                req6: Union[ConstrCastable6, ConstraintExpr[ConstrType6, ConstrCastable6]]) -> None: ...
  @overload
  def generator(self, fn: Callable[[ConstrType1, ConstrType2, ConstrType3, ConstrType4,
                                    ConstrType5, ConstrType6, ConstrType7], None],
                req1: Union[ConstrCastable1, ConstraintExpr[ConstrType1, ConstrCastable1]],
                req2: Union[ConstrCastable2, ConstraintExpr[ConstrType2, ConstrCastable2]],
                req3: Union[ConstrCastable3, ConstraintExpr[ConstrType3, ConstrCastable3]],
                req4: Union[ConstrCastable4, ConstraintExpr[ConstrType4, ConstrCastable4]],
                req5: Union[ConstrCastable5, ConstraintExpr[ConstrType5, ConstrCastable5]],
                req6: Union[ConstrCastable6, ConstraintExpr[ConstrType6, ConstrCastable6]],
                req7: Union[ConstrCastable7, ConstraintExpr[ConstrType7, ConstrCastable7]]) -> None: ...
  @overload
  def generator(self, fn: Callable[[ConstrType1, ConstrType2, ConstrType3, ConstrType4,
                                    ConstrType5, ConstrType6, ConstrType7, ConstrType8], None],
                req1: Union[ConstrCastable1, ConstraintExpr[ConstrType1, ConstrCastable1]],
                req2: Union[ConstrCastable2, ConstraintExpr[ConstrType2, ConstrCastable2]],
                req3: Union[ConstrCastable3, ConstraintExpr[ConstrType3, ConstrCastable3]],
                req4: Union[ConstrCastable4, ConstraintExpr[ConstrType4, ConstrCastable4]],
                req5: Union[ConstrCastable5, ConstraintExpr[ConstrType5, ConstrCastable5]],
                req6: Union[ConstrCastable6, ConstraintExpr[ConstrType6, ConstrCastable6]],
                req7: Union[ConstrCastable7, ConstraintExpr[ConstrType7, ConstrCastable7]],
                req8: Union[ConstrCastable8, ConstraintExpr[ConstrType8, ConstrCastable8]]) -> None: ...

  @overload
  def generator(self, fn: Callable[[ConstrType1, ConstrType2, ConstrType3, ConstrType4,
                                    ConstrType5, ConstrType6, ConstrType7, ConstrType8,
                                    ConstrType9], None],
                req1: Union[ConstrCastable1, ConstraintExpr[ConstrType1, ConstrCastable1]],
                req2: Union[ConstrCastable2, ConstraintExpr[ConstrType2, ConstrCastable2]],
                req3: Union[ConstrCastable3, ConstraintExpr[ConstrType3, ConstrCastable3]],
                req4: Union[ConstrCastable4, ConstraintExpr[ConstrType4, ConstrCastable4]],
                req5: Union[ConstrCastable5, ConstraintExpr[ConstrType5, ConstrCastable5]],
                req6: Union[ConstrCastable6, ConstraintExpr[ConstrType6, ConstrCastable6]],
                req7: Union[ConstrCastable7, ConstraintExpr[ConstrType7, ConstrCastable7]],
                req8: Union[ConstrCastable8, ConstraintExpr[ConstrType8, ConstrCastable8]],
                req9: Union[ConstrCastable9, ConstraintExpr[ConstrType9, ConstrCastable9]]) -> None: ...

  @overload
  def generator(self, fn: Callable[[ConstrType1, ConstrType2, ConstrType3, ConstrType4,
                                    ConstrType5, ConstrType6, ConstrType7, ConstrType8,
                                    ConstrType9, ConstrType10], None],
                req1: Union[ConstrCastable1, ConstraintExpr[ConstrType1, ConstrCastable1]],
                req2: Union[ConstrCastable2, ConstraintExpr[ConstrType2, ConstrCastable2]],
                req3: Union[ConstrCastable3, ConstraintExpr[ConstrType3, ConstrCastable3]],
                req4: Union[ConstrCastable4, ConstraintExpr[ConstrType4, ConstrCastable4]],
                req5: Union[ConstrCastable5, ConstraintExpr[ConstrType5, ConstrCastable5]],
                req6: Union[ConstrCastable6, ConstraintExpr[ConstrType6, ConstrCastable6]],
                req7: Union[ConstrCastable7, ConstraintExpr[ConstrType7, ConstrCastable7]],
                req8: Union[ConstrCastable8, ConstraintExpr[ConstrType8, ConstrCastable8]],
                req9: Union[ConstrCastable9, ConstraintExpr[ConstrType9, ConstrCastable9]],
                req10: Union[ConstrCastable10, ConstraintExpr[ConstrType10, ConstrCastable10]]) -> None: ...

  # TODO don't ignore the type and fix so the typer understands the above are subsumed by this
  def generator(self, fn: Callable[..., None], *reqs: ConstraintExpr) -> None:  # type: ignore
    """
    Registers a generator function
    :param fn: function (of self) to invoke, where the parameter list lines up with reqs
    :param reqs: required parameters, the value of which is made available to the generator
    :param req_ports: required ports, which can have their .is_connected() and .link().name() value obtained
    :param targets: list of ports and blocks the generator may connect to, to avoid generating initializers
    """
    assert callable(fn), f"fn {fn} must be a method (callable)"
    assert self._generator is None, f"redefinition of generator, multiple generators not allowed"

    for (i, req_param) in enumerate(reqs):
      assert isinstance(req_param.binding, InitParamBinding) or \
             (isinstance(req_param.binding, (AllocatedBinding, IsConnectedBinding, NameBinding))
              and req_param.binding.src._parent is self), \
        f"generator parameter {i} {req_param} not an __init__ parameter (or missing @init_in_parent)"

    self._generator = GeneratorBlock.GeneratorRecord(fn, reqs, (), reqs)

  # Generator solved-parameter-access interface
  #
  ConstrType = TypeVar('ConstrType')
  def get(self, param: ConstraintExpr[ConstrType, Any], default: Optional[ConstrType] = None) -> ConstrType:
    if self._elaboration_state != BlockElaborationState.generate:
      raise BlockDefinitionError(self, "can't call get(... outside generate",
                                 "call get(...) inside generate only, and remember to call super().generate()")
    if not isinstance(param, ConstraintExpr):
      raise TypeError(f"param to get(...) must be ConstraintExpr, got {param} of type {type(param)}")
    assert self._param_values is not None

    if param not in self._param_values:  # TODO disambiguate between inaccessible and failed const prop
      if default is not None:
        return default
      else:
        raise NotImplementedError(f"get({self._name_of_child(param)}) did not find a value, either the variable is inaccessible or an internal error")

    value = cast(Any, self._param_values[param])
    if isinstance(param, FloatExpr):
      assert isinstance(value, Number), f"get({self._name_of_child(param)}) expected float, got {value}"
    elif isinstance(param, IntExpr):
      assert isinstance(value, int), f"get({self._name_of_child(param)}) expected int, got {value}"
    elif isinstance(param, RangeExpr):
      assert isinstance(value, Range), f"get({self._name_of_child(param)}) expected range, got {value}"
    elif isinstance(param, BoolExpr):
      assert isinstance(value, bool), f"get({self._name_of_child(param)}) expected bool, got {value}"
    elif isinstance(param, StringExpr):
      assert isinstance(value, str), f"get({self._name_of_child(param)}) expected str, got {value}"
    elif isinstance(param, ArrayExpr):
      assert isinstance(value, list), f"get({self._name_of_child(param)}) expected list, got {value}"
    else:
      raise NotImplementedError(f"get({self._name_of_child(param)}) on unknown type, got {value}")
    return value  # type: ignore

  # Generator serialization and parsing
  #
  def _def_to_proto(self) -> edgir.HierarchyBlock:
    if self._elaboration_state != BlockElaborationState.post_generate:  # only write generator on the stub definition
      assert self._generator is not None, f"{self} did not define a generator"

      pb = edgir.HierarchyBlock()
      ref_map = self._get_ref_map(edgir.LocalPath())
      pb.generator.SetInParent()  # even if rest of the fields are empty, make sure to create a record
      for req_param in self._generator.req_params:
        pb.generator.required_params.add().CopyFrom(ref_map[req_param])
      for req_port in self._generator.req_ports:
        pb.generator.required_ports.add().CopyFrom(ref_map[req_port])
      pb = self._populate_def_proto_block_base(pb)
      return pb
    else:
      return super()._def_to_proto()

  def _parse_param_values(self, values: Iterable[Tuple[edgir.LocalPath, edgir.LitTypes]]) -> None:
    ref_map = self._get_ref_map(edgir.LocalPath())
    reverse_ref_map = { path.SerializeToString(): refable
                        for refable, path in ref_map.items() }
    self._param_values = IdentityDict()
    for (path, value) in values:
      path_expr = reverse_ref_map[path.SerializeToString()]
      assert isinstance(path_expr, ConstraintExpr)
      self._param_values[path_expr] = value

  def _generated_def_to_proto(self,
                              generate_values: Iterable[Tuple[edgir.LocalPath, edgir.LitTypes]]) -> edgir.HierarchyBlock:
    assert self._generator is not None, f"{self} did not define a generator"
    assert self._elaboration_state == BlockElaborationState.post_init  # TODO dedup w/ elaborated_def_to_proto
    self._elaboration_state = BlockElaborationState.contents

    self.contents()

    self._elaboration_state = BlockElaborationState.generate

    for (name, port) in self._ports.items():
      # TODO cleaner, oddly-stateful, detection of connected_link
      if isinstance(port, Port):
        port.link()  # lazy-initialize connected_link refs so it's ready for params
    self._parse_param_values(generate_values)

    fn_args = [self.get(arg_param) for arg_param in self._generator.fn_args]
    self._generator.fn(*fn_args)

    self._elaboration_state = BlockElaborationState.post_generate

    return self._def_to_proto()
