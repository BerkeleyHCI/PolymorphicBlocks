from __future__ import annotations

from typing import *

from deprecated import deprecated

import edgir
from .Binding import InitParamBinding, AllocatedBinding, IsConnectedBinding
from .Blocks import BlockElaborationState
from .ConstraintExpr import ConstraintExpr
from .Core import non_library
from .HdlUserExceptions import *
from .HierarchyBlock import Block
from .Ports import Port


@non_library
class GeneratorBlock(Block):
  """Part which generates into a subcircuit, given fully resolved parameters.
  Generation happens after a solver run.
  Allows much more power and customization in the elaboration of a subcircuit.
  """
  def __init__(self):
    super().__init__()
    self._generator: Optional[GeneratorBlock.GeneratorRecord] = None

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
      pb = self._populate_def_proto_block_base(pb)
      return pb
    else:
      return super()._def_to_proto()

  def _generated_def_to_proto(self, generate_values: Iterable[Tuple[edgir.LocalPath, edgir.ValueLit]]) -> \
      edgir.HierarchyBlock:
    assert self._generator is not None, f"{self} did not define a generator"
    assert self._elaboration_state == BlockElaborationState.post_init  # TODO dedup w/ elaborated_def_to_proto
    self._elaboration_state = BlockElaborationState.contents

    self.contents()

    self._elaboration_state = BlockElaborationState.generate

    # Translate parameter values to function arguments
    for (name, port) in self._ports.items():
      # TODO cleaner, oddly-stateful, detection of connected_link
      if isinstance(port, Port):
        port.link()  # lazy-initialize connected_link refs so it's ready for params

    ref_map = self._get_ref_map(edgir.LocalPath())
    generate_values_map = {path.SerializeToString(): value for (path, value) in generate_values}
    fn_args = [arg_param._from_lit(generate_values_map[ref_map[arg_param].SerializeToString()])
               for arg_param in self._generator.fn_args]

    self._generator.fn(*fn_args)

    self._elaboration_state = BlockElaborationState.post_generate

    return self._def_to_proto()
