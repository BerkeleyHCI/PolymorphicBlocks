from __future__ import annotations
from typing import *
import sys  # for exception chaining

import edgir


class PathException(Exception):
  pass


class Path(NamedTuple):  # internal helper type
  blocks: Tuple[str, ...]
  links: Tuple[str, ...]
  ports: Tuple[str, ...]
  params: Tuple[str, ...]

  def __hash__(self) -> int:
    return hash((self.blocks, self.links, self.ports, self.params))

  def __eq__(self, other) -> bool:
    return isinstance(other, Path) and self.blocks == other.blocks and self.links == other.links and \
           self.ports == other.ports and self.params == other.params

  def __repr__(self) -> str:
    if not self.blocks and not self.links and not self.ports and not self.params:
      return '(root)'
    else:
      return '.'.join(self.blocks + self.links + self.ports + self.params)

  @classmethod
  def empty(cls) -> Path:
    return Path((), (), (), ())

  def startswith(self, prefix: Path) -> bool:
    if self.blocks == prefix.blocks:  # exact match, check subpaths
      if self.links == prefix.links:
        if self.ports == prefix.ports:
          return len(self.params) >= len(prefix.params) and self.params[:len(prefix.params)] == prefix.params
        elif len(self.ports) >= len(prefix.ports) and self.ports[:len(prefix.ports)] == prefix.ports:
          return (not self.params) and (not prefix.params)
        else:
          return False

      elif len(self.links) >= len(prefix.links) and self.links[:len(prefix.links)] == prefix.links:
        return (not self.ports) and (not prefix.ports) and (not self.params) and (not prefix.params)
      else:
        return False

    elif len(self.blocks) >= len(prefix.blocks) and self.blocks[:len(prefix.blocks)] == prefix.blocks:
      # partial match, check subpaths don't exist
      return (not self.links) and (not prefix.links) and (not self.ports) and (not prefix.ports) and \
        (not self.params) and (not prefix.params)
    else:  # no match
      return False

  def append_block(self, *names: str) -> Path:
    assert not self.links and not self.ports and not self.params, f"tried to append block {names} to {self}"
    return Path(self.blocks + tuple(names), self.links, self.ports, self.params)

  def append_link(self, *names: str) -> Path:
    assert not self.ports and not self.params, f"tried to append link {names} to {self}"
    return Path(self.blocks, self.links + tuple(names), self.ports, self.params)

  def append_port(self, *names: str) -> Path:
    assert not self.params, f"tried to append port {names} to {self}"
    return Path(self.blocks, self.links, self.ports + tuple(names), self.params)

  def append_param(self, name: str) -> Path:
    return Path(self.blocks, self.links, self.ports, self.params + (name, ))

  def block_component(self) -> Path:
    return Path(self.blocks, (), (), ())

  def link_component(self, must_have_link=True) -> Path:
    if must_have_link:
      assert self.links
    return Path(self.blocks, self.links, (), ())

  def to_tuple(self) -> Tuple[str, ...]:
    return self.blocks + self.links + self.ports + self.params

  def to_local_path(self) -> edgir.LocalPath:
    path = edgir.LocalPath()
    for block in self.blocks:
      path.steps.add().name = block
    for link in self.links:
      path.steps.add().name = link
    for port in self.ports:
      path.steps.add().name = port
    for param in self.params:
      path.steps.add().name = param
    return path

  def _follow_partial_steps(self, steps: List[edgir.LocalStep], curr: edgir.EltTypes) -> \
      Tuple[Optional[List[edgir.LocalStep]], Tuple[Path, edgir.EltTypes]]:
    if not steps:
      return None, (self, curr)
    elif steps[0].HasField('name'):
      name = steps[0].name
      if isinstance(curr, (edgir.Port, edgir.Bundle, edgir.HierarchyBlock, edgir.Link)):
        param_opt = edgir.pair_get_opt(curr.params, name)
        if param_opt is not None:
          return self.append_param(name)._follow_partial_steps(steps[1:], param_opt)
      if isinstance(curr, (edgir.Bundle, edgir.Link, edgir.HierarchyBlock, edgir.LinkArray)):
        port_opt = edgir.pair_get_opt(curr.ports, name)
        if port_opt is not None:
          return self.append_port(name)._follow_partial_steps(steps[1:], edgir.resolve_portlike(port_opt))
      if isinstance(curr, edgir.PortArray) and curr.HasField('ports'):
        port_opt = edgir.pair_get_opt(curr.ports.ports, name)
        if port_opt is not None:
          return self.append_port(name)._follow_partial_steps(steps[1:], edgir.resolve_portlike(port_opt))
      if isinstance(curr, edgir.HierarchyBlock):
        block_opt = edgir.pair_get_opt(curr.blocks, name)
        if block_opt is not None:
          return self.append_block(name)._follow_partial_steps(steps[1:], edgir.resolve_blocklike(block_opt))
      if isinstance(curr, (edgir.HierarchyBlock, edgir.Link, edgir.LinkArray)):
        link_opt = edgir.pair_get_opt(curr.links, name)
        if link_opt is not None:
          return self.append_link(name)._follow_partial_steps(steps[1:], edgir.resolve_linklike(link_opt))

      return steps, (self, curr)
    elif steps[0].HasField('reserved_param'):
      return steps, (self, curr)  # Path does not understand special paths
    else:
      raise PathException(f"unknown step {steps[0]} when following path")

  def follow_partial(self, path: edgir.LocalPath, curr: edgir.EltTypes) -> \
      Tuple[Optional[List[edgir.LocalStep]], Tuple[Path, edgir.EltTypes]]:
    """Follows a edgir.LocalPath from curr, returning any unused path elements.
    Returns: (unused path elements postfix, (destination full path, destination object))"""
    try:
      return self._follow_partial_steps(list(path.steps), curr)
    except PathException as e:
      import sys
      raise type(e)(f"(while following {edgir.local_path_to_str(path)} from {self}) " + str(e)) \
        .with_traceback(sys.exc_info()[2])

  def follow(self, path: edgir.LocalPath, curr: edgir.EltTypes) -> Tuple[Path, edgir.EltTypes]:
    """Follows a edgir.LocalPath from curr. Raises an exception if there are unused path elements.
    Returns: (destination full path, destination object)"""
    remaining, (end_path, end_elt) = self.follow_partial(path, curr)
    if remaining is not None:
      raise ValueError(f"can't follow {edgir.local_path_to_str(path)} from {self}, have unused path elements {remaining} from {end_path}")
    else:
      return (end_path, end_elt)


class TransformContext(NamedTuple):
  path: Path
  design: edgir.Design

  def __repr__(self) -> str:
    return f"TransformContext(path={self.path}, design=...)"

  def append_block(self, name: str) -> TransformContext:
    return TransformContext(self.path.append_block(name), self.design)

  def append_link(self, name: str) -> TransformContext:
    return TransformContext(self.path.append_link(name), self.design)

  def append_port(self, name: str) -> TransformContext:
    return TransformContext(self.path.append_port(name), self.design)


# Preorder traversal needed for: generators (helpful), design inst,
# Postorder traversal needed for: netlisting (but not really)
class Transform():
  """
  Base class that does a preorder traversal and in-place visiting (with modification) of the Design tree.
  Note, the visit_* operations are in-place to keep the local element consistent with the top-level Design reference
  in the Context
  """
  def visit_block(self, context: TransformContext, block: edgir.HierarchyBlock) -> None:
    pass

  def visit_link(self, context: TransformContext, link: edgir.Link) -> None:
    pass

  def visit_linkarray(self, context: TransformContext, link: edgir.LinkArray) -> None:
    pass

  # The visit_*like allows changing the "type", eg lib -> instantiated h-block
  def visit_blocklike(self, context: TransformContext, block: edgir.BlockLike) -> None:
    pass

  def visit_portlike(self, context: TransformContext, port: edgir.PortLike) -> None:
    pass

  def visit_linklike(self, context: TransformContext, link: edgir.LinkLike) -> None:
    pass

  #
  # Internal Traversal Methods
  #
  def _traverse_portlike(self, context: TransformContext, elt: edgir.PortLike) -> None:
    try:
      self.visit_portlike(context, elt)
    except Exception as e:
      raise type(e)(f"(while visiting PortLike at {context}) " + str(e)) \
        .with_traceback(sys.exc_info()[2])

    if elt.HasField('lib_elem'):
      raise ValueError(f"unresolved lib at {context}")
    elif elt.HasField('port'):
      pass  # nothing to recurse into
    elif elt.HasField('bundle'):
      for port_pair in elt.bundle.ports:
        self._traverse_portlike(context.append_port(port_pair.name), port_pair.value)
    elif elt.HasField('array') and elt.array.HasField('ports'):
      for port_pair in elt.array.ports.ports:
        self._traverse_portlike(context.append_port(port_pair.name), port_pair.value)
    else:
      raise ValueError(f"_traverse_portlike encountered unknown type {elt} at {context}")

  def _traverse_block(self, context: TransformContext, elt: edgir.HierarchyBlock) -> None:
    try:
      self.visit_block(context, elt)
    except Exception as e:
      raise type(e)(f"(while visiting Block at {context}) " + str(e)) \
        .with_traceback(sys.exc_info()[2])

    for port_pair in elt.ports:
      self._traverse_portlike(context.append_port(port_pair.name), port_pair.value)
    for link_pair in elt.links:
      self._traverse_linklike(context.append_link(link_pair.name), link_pair.value)
    for block_pair in elt.blocks:
      self._traverse_blocklike(context.append_block(block_pair.name), block_pair.value)

  def _traverse_blocklike(self, context: TransformContext, elt: edgir.BlockLike) -> None:
    try:
      self.visit_blocklike(context, elt)
    except Exception as e:
      raise type(e)(f"(while visiting PortLike at {context}) " + str(e)) \
        .with_traceback(sys.exc_info()[2])

    if elt.HasField('lib_elem'):
      raise ValueError(f"unresolved lib at {context}")
    elif elt.HasField('hierarchy'):
      self._traverse_block(context, elt.hierarchy)
    else:
      raise ValueError(f"_traverse_blocklike encountered unknown type {elt} at {context}")

  def _traverse_linklike(self, context: TransformContext, elt: edgir.LinkLike) -> None:
    try:
      self.visit_linklike(context, elt)
    except Exception as e:
      raise type(e)(f"(while visiting LinkLike at {context}) " + str(e)) \
        .with_traceback(sys.exc_info()[2])

    if elt.HasField('lib_elem'):
      raise ValueError(f"unresolved lib at {context}")
    elif elt.HasField('link'):
      try:
        self.visit_link(context, elt.link)
      except Exception as e:
        raise type(e)(f"(while visiting Link at {context}) " + str(e)) \
          .with_traceback(sys.exc_info()[2])

      for port_pair in elt.link.ports:
        self._traverse_portlike(context.append_port(port_pair.name), port_pair.value)

      for link_pair in elt.link.links:
        self._traverse_linklike(context.append_link(link_pair.name), link_pair.value)
    elif elt.HasField('array'):
      try:
        self.visit_linkarray(context, elt.array)
      except Exception as e:
        raise type(e)(f"(while visiting LinkArray at {context}) " + str(e)) \
          .with_traceback(sys.exc_info()[2])

      for port_pair in elt.array.ports:
        self._traverse_portlike(context.append_port(port_pair.name), port_pair.value)

      for link_pair in elt.array.links:
        self._traverse_linklike(context.append_link(link_pair.name), link_pair.value)
    else:
      raise ValueError(f"_traverse_linklike encountered unknown type {elt} at {context}")

  def transform_design(self, design: edgir.Design) -> edgir.Design:
    design_copy = edgir.Design()
    design_copy.CopyFrom(design)  # create a copy so we can mutate in-place

    # TODO: toplevel is nonuniform w/ BlockLike, so we copy transform_blocklike and traverse_blocklike
    # TODO: this can't handle instantiation at the top level
    root_context = TransformContext(Path.empty(), design_copy)
    self.visit_block(root_context, design_copy.contents)

    # TODO dedup w/ _transform_blocklike
    for port_pair in design_copy.contents.ports:
      self._traverse_portlike(root_context.append_port(port_pair.name), port_pair.value)
    for link_pair in design_copy.contents.links:
      self._traverse_linklike(root_context.append_link(link_pair.name), link_pair.value)
    for block_pair in design_copy.contents.blocks:
      self._traverse_blocklike(root_context.append_block(block_pair.name), block_pair.value)

    return design_copy
