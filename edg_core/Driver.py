from __future__ import annotations

from types import ModuleType
from typing import *
from itertools import chain, takewhile
import sys
import inspect
import importlib
import copy
import traceback


from . import edgir
from .Core import LibraryElement, builder
from .ConstraintExpr import BoolExpr
from .HierarchyBlock import GeneratorBlock
from . import Block, Port, Bundle
from . import TransformUtil
from .SimpleConstProp import SimpleConstPropTransform, BaseErrorResult


# Returns true if this may be a constraint understandable by generator parse_from_proto
def maybe_generator_constraint(constraint: edgir.ValueExpr) -> bool:
  return constraint.HasField('binary') and constraint.binary.op == edgir.BinaryExpr.EQ and \
      constraint.binary.lhs.HasField('ref') and \
      (constraint.binary.rhs.HasField('literal') or
        (constraint.binary.rhs.HasField('binary') and constraint.binary.rhs.binary.op == edgir.BinaryExpr.RANGE))


class DesignRefinement(NamedTuple):  # TODO this should probably go into a more base package?
  class_refinements: Dict[bytes, bytes] = {}  # we use LibraryPath.SerializeToString because proobuf objs are not hashable
  instance_refinements: Dict[TransformUtil.Path, bytes] = {}
  param_settings: Dict[TransformUtil.Path, edgir.LitTypes] = {}

EmptyRefinement = DesignRefinement({}, {})


class InstantiationTransform(TransformUtil.Transform):
  """Defines transforms to instantiate library elements"""
  def __init__(self, lib: Dict[str, edgir.EltTypes], refinement: DesignRefinement = EmptyRefinement):
    self.lib = lib
    # Refinements are defined here to avoid instantiating the original, then replacing it, and so that there is only
    # one instantiation phase for other transforms (eg, simple const prop) to deal with.
    self.refinement = refinement

    # Number of connections to each block / link edge array port. The key must be a direct port of a block / link, not a
    # sub-port. This should be guaranteed by the block connect restrictions.
    self.array_connect_count: Dict[TransformUtil.Path, int] = {}

  def visit_portlike(self, context: TransformUtil.TransformContext, port: edgir.PortLike) -> None:
    if port.HasField('lib_elem'):
      assert context.path not in self.array_connect_count

      lib_elem = port.lib_elem
      lib_pb = self.lib[lib_elem.target.name]
      port_elt: edgir.PortTypes
      if isinstance(lib_pb, edgir.Port):
        port.port.CopyFrom(lib_pb)
        port_elt = port.port
      elif isinstance(lib_pb, edgir.Bundle):
        port.bundle.CopyFrom(lib_pb)
        port_elt = port.bundle
      else:  # Arrays should not be in the library, but rather directly in the enclosing object
        raise ValueError(f"unknown PortLike library elem type {lib_pb.__class__} at {context}")

      del port_elt.superclasses[:]  # TODO stack instead of replace superclasses?
      port_elt.superclasses.add().CopyFrom(lib_elem)
    elif port.HasField('array'):
      array_elts = self.array_connect_count.get(context.path, 0)
      for i in range(array_elts):
        assert len(port.array.superclasses) == 1
        port.array.ports[str(i)].lib_elem.CopyFrom(port.array.superclasses[0])

  def resolve_into_lib(self, path: TransformUtil.Path, curr: edgir.EltTypes,
                       steps: List[edgir.LocalStep]) -> Tuple[TransformUtil.Path, edgir.EltTypes]:
    """Like TransformUtil.follow, but this expects to recurse into a library from the first step onwards, except for
    PortArray types"""
    if not steps:
      return path, curr

    assert steps[0].HasField('name')
    name = steps[0].name

    if isinstance(curr, edgir.PortArray):  # special case for fake heuristic Map-Extract
      assert len(curr.superclasses) == 1
      resolved_elt = self.lib[curr.superclasses[0].target.name]
      if isinstance(resolved_elt, edgir.Bundle) and name in resolved_elt.ports:
        return self.resolve_into_lib(path, resolved_elt, steps)

    # TODO unify w/ TransformUtil.Path? But this can recurse into libraries?
    if (isinstance(curr, edgir.Bundle) or isinstance(curr, edgir.PortArray) or isinstance(curr, edgir.Link) or
        isinstance(curr, edgir.HierarchyBlock)) and name in curr.ports:
      portlike = curr.ports[name]
      if portlike.HasField('lib_elem'):
        resolved_elt = self.lib[portlike.lib_elem.target.name]
        return self.resolve_into_lib(path.append_port(name), resolved_elt, steps[1:])
      elif portlike.HasField('array'):
        return self.resolve_into_lib(path.append_port(name), portlike.array, steps[1:])
      else:
        raise NotImplementedError(f"can't resolve into portlike {portlike}")
    elif (isinstance(curr, edgir.HierarchyBlock) or isinstance(curr, edgir.Link)) and name in curr.links:
      linklike = curr.links[name]
      if linklike.HasField('lib_elem'):
        resolved_elt = self.lib[linklike.lib_elem.target.name]
        return self.resolve_into_lib(path.append_link(name), resolved_elt, steps[1:])
      else:
        raise NotImplementedError(f"can't resolve into linklike {linklike}")
    else:
      raise NotImplementedError(f"can't resolve {steps} into unknown type {type(curr)} {curr}")

  def transform_connection(self, context: TransformUtil.TransformContext,
                           constr: edgir.ValueExpr, block: edgir.BlockLikeTypes) -> Optional[List[edgir.ValueExpr]]:
    def transform_link_port_path(path: edgir.LocalPath) -> None:
      assert len(path.steps) == 2, f"invalid path structure {path}"
      # TODO this currently assumes no array-array connects, which is fine since arrays aren't allowed on Blocks (yet)
      path_target, path_target_elt = self.resolve_into_lib(context.path, block, list(path.steps))
      if isinstance(path_target_elt, edgir.PortArray):
        this_index = self.array_connect_count.get(path_target, 0)
        self.array_connect_count[path_target] = this_index + 1
        path.steps.add().name = str(this_index)

    if constr.HasField('connected'):
      assert isinstance(block, edgir.HierarchyBlock)
      assert constr.connected.link_port.HasField('ref')
      assert constr.connected.block_port.HasField('ref')
      new_constr = copy.deepcopy(constr)
      transform_link_port_path(new_constr.connected.link_port.ref)
      return [new_constr]
    elif constr.HasField('exported') and isinstance(block, edgir.Link):
      ext_refs: Union[edgir.LocalPath, List[edgir.LocalPath]]
      if constr.exported.exterior_port.HasField('ref'):
        ext_path, ext_elt = self.resolve_into_lib(context.path, block, list(constr.exported.exterior_port.ref.steps))
        if isinstance(ext_elt, edgir.PortArray):
          ext_refs = []
          for array_idx in range(self.array_connect_count.get(ext_path, 0)):  # need default zero for unconnected ports
            array_subref = copy.deepcopy(constr.exported.exterior_port.ref)
            array_subref.steps.add().name = str(array_idx)
            ext_refs.append(array_subref)
        else:
          ext_refs = constr.exported.exterior_port.ref
      elif constr.exported.exterior_port.HasField('map_extract'):
        ext_path, ext_elt = self.resolve_into_lib(context.path, block, list(constr.exported.exterior_port.map_extract.container.ref.steps))
        assert isinstance(ext_elt, edgir.PortArray)
        ext_refs = []
        for array_idx in range(self.array_connect_count.get(ext_path, 0)):  # need default zero for unconnected ports
          array_subref = copy.deepcopy(constr.exported.exterior_port.map_extract.container.ref)
          array_subref.steps.add().name = str(array_idx)
          array_subref.steps.extend(constr.exported.exterior_port.map_extract.path.steps)
          ext_refs.append(array_subref)
      else:
        raise ValueError(f"invalid exported.exterior_port {constr.exported.exterior_port}")

      assert constr.exported.internal_block_port.HasField('ref')
      int_path, int_elt = self.resolve_into_lib(context.path, block, list(constr.exported.internal_block_port.ref.steps))
      if isinstance(int_elt, edgir.PortArray):  # array target
        if isinstance(ext_refs, edgir.LocalPath):  # convert external side to array-like
          ext_refs = [ext_refs]
        expanded: List[edgir.ValueExpr] = []
        for ext_ref in ext_refs:
          int_idx = self.array_connect_count.get(int_path, 0)
          new_constr = copy.deepcopy(constr)
          new_constr.exported.exterior_port.ref.CopyFrom(ext_ref)
          new_constr.exported.internal_block_port.ref.steps.add().name = str(int_idx)
          expanded.append(new_constr)
          self.array_connect_count[int_path] = int_idx + 1
        return expanded
      else:  # single port target
        assert isinstance(ext_refs, edgir.LocalPath), "can't connect array to port"
        return None
    else:  # not a connected / exported constraint, or an exported constraint that doesn't need expansion
      return None

  def visit_blocklike(self, context: TransformUtil.TransformContext, block: edgir.BlockLike) -> None:
    if block.HasField('lib_elem'):
      lib_elem = block.lib_elem

      # do refinement if necessary
      original_lib_elem: Optional[edgir.LibraryPath] = None
      if context.path in self.refinement.instance_refinements:
        original_lib_elem = lib_elem
        lib_elem = edgir.LibraryPath.FromString(self.refinement.instance_refinements[context.path])
      elif lib_elem.SerializeToString() in self.refinement.class_refinements:
        original_lib_elem = lib_elem
        lib_elem = edgir.LibraryPath.FromString(self.refinement.class_refinements[lib_elem.SerializeToString()])

      # instantiate block
      lib_pb = self.lib[lib_elem.target.name]
      block_elt: edgir.BlockTypes
      if isinstance(lib_pb, edgir.HierarchyBlock):
        block.hierarchy.CopyFrom(lib_pb)
        block_elt = block.hierarchy
      else:
        raise ValueError(f"unknown BlockLike library elem type {lib_pb.__class__} at {context}")

      del block_elt.superclasses[:]  # TODO stack instead of replace superclasses?
      block_elt.superclasses.add().CopyFrom(lib_elem)
      if original_lib_elem is not None:
        block_elt.meta.members.node['refinement_original'].bin_leaf = original_lib_elem.SerializeToString()

  def transform_constraints(self, context: TransformUtil.TransformContext, block: edgir.BlockLikeTypes) -> None:
    # transform connected constraints, traversing keys to allow in-place mutation
    for name in list(block.constraints.keys()):
      constr = block.constraints[name]
      new_constrs = self.transform_connection(context, constr, block)
      if new_constrs is None:
        pass  # TODO a speed optimization to not touch unchanged constraints but kind of odd
      elif len(new_constrs) == 1:
        block.constraints[name].CopyFrom(new_constrs[0])
      else:
        del block.constraints[name]
        for i, new_constr in enumerate(new_constrs):
          block.constraints[f'{name}_{i}'].CopyFrom(new_constr)

  def visit_block(self, context: TransformUtil.TransformContext, block: edgir.BlockLikeTypes) -> None:
    if isinstance(block, edgir.HierarchyBlock):  # post-instantiation, get data for array expansion
      self.transform_constraints(context, block)


  def visit_linklike(self, context: TransformUtil.TransformContext, link: edgir.LinkLike) -> None:
    if link.HasField('lib_elem'):
      lib_elem = link.lib_elem
      lib_pb = self.lib[lib_elem.target.name]
      if isinstance(lib_pb, edgir.Link):
        link.link.CopyFrom(lib_pb)
        link_elt = link.link
      else:
        raise ValueError(f"unknown LinkLike library elem type {lib_pb.__class__} at {context}")

      del link_elt.superclasses[:]  # TODO stack instead of replace superclasses?
      link_elt.superclasses.add().CopyFrom(lib_elem)

  def visit_link(self, context: TransformUtil.TransformContext, link: edgir.Link) -> None:
    self.transform_constraints(context, link)

class GeneratorTransform(TransformUtil.Transform):
  """Defines transforms to instantiate generators, on top of library element instantiation"""
  def __init__(self, lib: Dict[str, edgir.EltTypes], refinement: DesignRefinement,
               continue_on_error=False) -> None:
    super().__init__()

    self.instantiator = InstantiationTransform(lib, refinement)
    self.scp = SimpleConstPropTransform()
    self.continue_on_error = continue_on_error

    for path, value in refinement.param_settings.items():
      self.scp.set_value(path, value, "refinement")

  def transform_design(self, design: edgir.Design) -> edgir.Design:
    # Pre-instantiate and const-prop the design so the generator is in a good state
    design = self.instantiator.transform_design(design)
    design = self.scp.transform_design(design)

    return super().transform_design(design)

  def visit_block(self, context: TransformUtil.TransformContext, block: edgir.HierarchyBlock) -> None:
    # If a generator, invoke it
    if 'generator' in block.meta.members.node and 'done' not in block.meta.members.node['generator'].members.node:
      class_module = block.meta.members.node['generator'].members.node['module'].text_leaf
      class_name = block.meta.members.node['generator'].members.node['class'].text_leaf
      cls = getattr(importlib.import_module(class_module), class_name)
      generator_obj = cast(GeneratorBlock, cls())

      additional_constraints: Dict[str, edgir.ValueExpr] = {}
      for param_relpath, param_value in self.scp.get_block_solved_params(context.design, context.path):
        # TODO dedup w/ WriteSolvedParamTransform?
        if isinstance(param_value, BaseErrorResult):
          continue

        constr_name = '(scp)' + edgir.local_path_to_str(param_relpath)
        assert constr_name not in block.constraints
        additional_constraints[constr_name] = edgir.ValueExpr()
        additional_constraints[constr_name].binary.op = edgir.BinaryExpr.EQ
        additional_constraints[constr_name].binary.lhs.ref.CopyFrom(param_relpath)
        additional_constraints[constr_name].binary.rhs.CopyFrom(edgir.lit_to_expr(param_value))

      generator_obj._parse_from_proto(block, additional_constraints)
      if self.continue_on_error:  # if continue on error, wrap in a try/except call
        try:
          generated = builder.elaborate_toplevel(generator_obj, f"in generate at {context.path} for {generator_obj}",
                                                 generate=True)
        except BaseException as e:
          generated = copy.deepcopy(block)
          generated.meta.members.node['error'].members.node['generator'].text_leaf = repr(e)
          generated.meta.members.node['traceback'].text_leaf = traceback.format_exc()
          del generated.meta.members.node['generator'].members.node['class']
          del generated.meta.members.node['generator'].members.node['module']
          generated.meta.members.node['generator'].members.node['done'].text_leaf = 'done'
      else:
        generated = builder.elaborate_toplevel(generator_obj, f"in generate at {context.path} for {generator_obj}",
                                               generate=True)

      assert 'done' in generated.meta.members.node['generator'].members.node

      # TODO maybe dedup w/ instantiation transform?
      del generated.superclasses[:]  # TODO stack instead of replace superclasses?
      for block_superclass in block.superclasses:
        generated.superclasses.add().CopyFrom(block_superclass)

      # copy over any additional constraints from the source
      for name, constraint in block.constraints.items():
        if name in generated.constraints:
          assert generated.constraints[name] == constraint
        else:
          generated.constraints[name].CopyFrom(constraint)

      # Consistency check
      assert generated.ports.keys() == block.ports.keys()  # TODO we can't consistency check values pre-instantiation
      assert generated.params == block.params

      if 'refinement_original' in block.meta.members.node:
        generated.meta.members.node['refinement_original'].CopyFrom(block.meta.members.node['refinement_original'])

      def check_metadata_is_superset(generated_metadata: edgir.Metadata, block_metadata: edgir.Metadata, path: str):
        if path in ['.generator', '._sourcelocator']:  # expected mismatch
          # TODO fix sourcelocator to not error out on top_init if the generator is the top-level
          return

        if generated_metadata.HasField('members') and block_metadata.HasField('members'):
          for key, val in block_metadata.members.node.items():
            assert key in generated_metadata.members.node, f"mismatch in metadata at {path}, generated missing key {key}"
            check_metadata_is_superset(generated_metadata.members.node[key], val, f"{path}.{key}")
        elif generated_metadata.HasField('bin_leaf') and block_metadata.HasField('bin_leaf'):
          assert generated_metadata.bin_leaf == block_metadata.bin_leaf, \
            f"mismatch in metadata at {path}, generated={generated_metadata.bin_leaf!r}, block={block_metadata.bin_leaf!r}"
        elif generated_metadata.HasField('text_leaf') and block_metadata.HasField('text_leaf'):
          assert generated_metadata.text_leaf == block_metadata.text_leaf,\
            f"mismatch in metadata at {path}, generated={generated_metadata.text_leaf}, block={block_metadata.text_leaf}"

      check_metadata_is_superset(generated.meta, block.meta, '')

      block.CopyFrom(generated)

      self.instantiator._traverse_block(context, block)
      self.scp._traverse_block(context, block)

    super().visit_block(context, block)


class OverwritingConsole():
  def __init__(self):
    self.last_length = 0

  def print(self, line: str) -> None:
    line_len = len(line)
    print_line = '\b' * self.last_length + line
    erase_len = self.last_length - line_len
    if erase_len > 0:
      print_line += ' ' * erase_len + '\b' * erase_len
    print(print_line, end='', flush=True)

    self.last_length = line_len


console = OverwritingConsole()


class Driver():
  cache: Dict[ModuleType, Dict[str, edgir.EltTypes]] = {}

  def __init__(self, libs: List[ModuleType], raw_defs: Dict[str, edgir.EltTypes] = {}):
    self._lib_modules = libs
    self._raw_defs = raw_defs
    self._libs_opt: Optional[Dict[str, edgir.EltTypes]] = None

  def libs(self) -> Dict[str, edgir.EltTypes]:  # lazy-initialize libraries
    if self._libs_opt is None:
      self._libs_opt = self._raw_defs.copy()
      # Walk through the libraries in reverse order, leaf-level first, since that's the most likely one the user is
      # working on and hence and fail.
      for lib in reversed(self._lib_modules):
        if lib not in self.cache:
          self.cache[lib] = self._lib_to_proto(lib)  # TODO check for consistency
        self._libs_opt.update(self.cache[lib])
    return self._libs_opt

  def _is_library_class(self, cls: Type) -> bool:
    # TODO write abstract parts into library without crashing
    return inspect.isclass(cls) and issubclass(cls, LibraryElement) and \
           (cls, 'non_library') not in cls._elt_properties

  def _lib_to_proto(self, lib: ModuleType) -> Dict[str, edgir.EltTypes]:
    toplevel_names: Set[str] = set()  # module toplevel and prior "seen" list to avoid duplicating work
    types: Dict[str, edgir.EltTypes] = {}

    def process_class(cls: Type) -> None:
      from .Blocks import BaseBlock
      if self._is_library_class(cls) and cls.__module__.startswith(lib.__name__):  # TODO unify all checks here
        obj = cls()
        obj_name = obj._get_def_name()
        console.print(f"library: {obj_name.split('.')[-1]}")
        if not isinstance(obj, BaseBlock):
          obj_proto = obj._def_to_proto()
        else:
          obj_proto = builder.elaborate_toplevel(obj, f"in elaborating library object {obj}")

        assert obj_name not in types, f"duplicate {obj_name}"
        types[obj_name] = obj_proto

        # Recurse into the object to detect classes that are used internally
        if isinstance(obj, Block):
          for superclass in obj._get_block_bases():
            if superclass._static_def_name() not in types and superclass._static_def_name() not in toplevel_names:
              process_class(superclass)

          for name, subblock in obj._blocks.items():
            if subblock._get_def_name() not in types and subblock._get_def_name() not in toplevel_names:
              process_class(subblock.__class__)  # TODO can we avoid multiple instantiation?

        if isinstance(obj, (Block, Bundle)):
          for name, subport in obj._ports.items():
            if subport._get_def_name() not in types and subport._get_def_name() not in toplevel_names:
              process_class(subport.__class__)  # TODO can we avoid multiple instantiation?

        if isinstance(obj, Port):
          if hasattr(obj, 'link_type') and\
              obj.link_type._static_def_name() not in types and\
              obj.link_type._static_def_name() not in toplevel_names:  # TODO this should be enforced to have a link type?
            process_class(obj.link_type)
          if obj.bridge_type is not None and\
              obj.bridge_type._static_def_name() not in types and \
              obj.bridge_type._static_def_name() not in toplevel_names:
            process_class(obj.bridge_type)
          for adapter_type in obj.adapter_types:
            process_class(adapter_type)

    classes: List[Type[LibraryElement]] = []
    for (name, cls) in inspect.getmembers(lib):
      if self._is_library_class(cls):
        cls_static_name = cls._static_def_name()
        if cls_static_name not in toplevel_names:
          toplevel_names.add(cls_static_name)
          classes.append(cls)


    for cls in classes:
      process_class(cls)

    self.cache[lib] = types

    console.print("")
    return types

  def generate_library_proto(self) -> edgir.Library:
    pb = edgir.Library()
    for name, elt in self.libs().items():
      assert name not in pb.root.members
      if isinstance(elt, edgir.Port):
        pb.root.members[name].port.CopyFrom(elt)
      elif isinstance(elt, edgir.Bundle):
        pb.root.members[name].bundle.CopyFrom(elt)
      elif isinstance(elt, edgir.HierarchyBlock):
        pb.root.members[name].hierarchy_block.CopyFrom(elt)
      elif isinstance(elt, edgir.Link):
        pb.root.members[name].link.CopyFrom(elt)
      else:
        raise ValueError("Unknown type %s in %s=%s" % (elt.__class__, name, elt))
    return pb

  @classmethod
  def elaborate_toplevel(cls, block: Block) -> edgir.Design:
    """Elaborates the toplevel design, putting initializers of its "parent" into itself.
    TODO: initializers should be separated, perhaps put into the Design level"""
    console.print(f"elaborate: {block._get_def_name().split('.')[-1]}")

    fake_toplevel = Block()
    assert builder.get_curr_context() is None  # TODO can this be pushed into builder like elaborate_toplevel?
    block_bound = block._bind(fake_toplevel, ignore_context=True)

    # for initializers from the top-level, create the initializer constraints in the block itself
    top_init = block._initializer_to(block_bound)
    if not BoolExpr._is_true_lit(top_init):
      block_bound.constrain(top_init, "(top_init)")

    block_pb = builder.elaborate_toplevel(block_bound, f"in elaborating toplevel design {block_bound}")

    design = edgir.Design()
    design.contents.CopyFrom(block_pb)
    del design.contents.superclasses[:]  # TODO stack instead of replace superclasses?
    design.contents.superclasses.add().target.name = block._get_def_name()  # TODO dedup w/ InstantiationTransform

    console.print("")
    return design

  def _generate_design(self, design: edgir.Design, refinements: DesignRefinement, continue_on_error: bool, name: str) ->\
      Tuple[edgir.Design, GeneratorTransform]:
    console.print(f"generate: {name.split('.')[-1]}")
    generator_transform = GeneratorTransform(self.libs(), refinements, continue_on_error=continue_on_error)
    new_design = generator_transform.transform_design(design)
    console.print("")
    return new_design, generator_transform

  def generate_block(self, lib_block: Block, constrs: Dict[TransformUtil.Path, edgir.LitTypes] = {}, *,
                     continue_on_error=False) -> edgir.Design:
    refinements = copy.deepcopy(EmptyRefinement)
    refinements.param_settings.update(constrs)
    elaborated = self.elaborate_toplevel(lib_block)
    generated = self._generate_design(elaborated, refinements,
                                      continue_on_error=continue_on_error, name=lib_block._get_def_name())[0]
    return generated
