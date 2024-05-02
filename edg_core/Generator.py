from __future__ import annotations

from typing import *

from deprecated import deprecated

import edgir
from .Ports import BasePort, Port
from .PortTag import PortTag
from .IdentityDict import IdentityDict
from .Binding import InitParamBinding, AllocatedBinding, IsConnectedBinding
from .Blocks import BlockElaborationState, AbstractBlockProperty
from .ConstraintExpr import ConstraintExpr
from .Core import non_library
from .HdlUserExceptions import *
from .HierarchyBlock import Block


CastableType = TypeVar('CastableType', bound=Any)
@non_library
class GeneratorBlock(Block):
  """Block which allows arbitrary Python code to generate its internal subcircuit,
  and unlike regular Blocks can rely on Python values of solved parameters.
  """
  def __init__(self):
    super().__init__()
    self._generator: Optional[GeneratorBlock.GeneratorRecord] = None
    self._generator_params_list: list[ConstraintExpr] = []
    self._generator_param_values = IdentityDict[ConstraintExpr, Any]()

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

  WrappedType = TypeVar('WrappedType', bound=Any)
  def get(self, param: ConstraintExpr[WrappedType, Any]) -> WrappedType:
    return self._generator_param_values[param]

  # Generator dependency data
  #
  class GeneratorRecord(NamedTuple):
    fn: Callable
    req_params: Tuple[ConstraintExpr, ...]  # all required params for generator to fire
    fn_args: Tuple[ConstraintExpr, ...]  # params to unpack for the generator function

  @deprecated(reason="implement self.generate() instead (using self.get(...), self.generator_param(...))")
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

      if type(self).generate is not GeneratorBlock.generate:
        assert self._generator is None, "new-style generator may not define self.generator(...)"
        for param in self._generator_params_list:
          pb.generator.required_params.add().CopyFrom(ref_map[param])
      elif self._generator is not None:  # legacy generator style
        assert len(self._generator_params_list) == 0, "legacy self.generator(...) must not have generator_params()"
        for req_param in self._generator.req_params:
          pb.generator.required_params.add().CopyFrom(ref_map[req_param])
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
    if type(self).generate is not GeneratorBlock.generate:
      for param in self._generator_params_list:
        self._generator_param_values[param] = param._from_lit(generate_values_map[ref_map[param].SerializeToString()])
      self.generate()
    elif self._generator is not None:  # legacy generator style
      fn_args = [arg_param._from_lit(generate_values_map[ref_map[arg_param].SerializeToString()])
                 for arg_param in self._generator.fn_args]
      self._generator.fn(*fn_args)
    else:
      raise BlockDefinitionError(self, "Generator missing generate implementation", "define generate")

    self._elaboration_state = BlockElaborationState.post_generate

    return self._def_to_proto()


class DefaultExportBlock(GeneratorBlock):
  """EXPERIMENTAL UTILITY CLASS. There needs to be a cleaner way to address this eventually,
  perhaps as a core compiler construct.
  This encapsulates the common pattern of an optional export, which if not externally connected,
  connects the internal port to some other default port.
  TODO The default can be specified as a port, or a function that returns a port (e.g. to instantiate adapters)."""
  def __init__(self):
    super().__init__()
    self._default_exports: List[Tuple[BasePort, Port, Port]] = []  # internal, exported, default

  ExportType = TypeVar('ExportType', bound=BasePort)
  def Export(self, port: ExportType, *args, default: Optional[Port] = None, **kwargs) -> ExportType:
    """A generator-only variant of Export that supports an optional default (either internal or external)
    to connect the (internal) port being exported to, if the external exported port is not connected."""
    if default is  None:
      new_port = super().Export(port, *args, **kwargs)
    else:
      assert 'optional' not in kwargs, "optional must not be specified with default"
      new_port = super().Export(port, *args, optional=True, **kwargs)
      assert isinstance(new_port, Port), "defaults only supported with Port types"
      self.generator_param(new_port.is_connected())
      self._default_exports.append((port, new_port, default))
    return new_port

  def generate(self):
    super().generate()
    for (internal, exported, default) in self._default_exports:
      if self.get(exported.is_connected()):
        self.connect(internal, exported)
      else:
        self.connect(internal, default)