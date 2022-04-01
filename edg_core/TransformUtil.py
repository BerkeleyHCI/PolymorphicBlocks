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

  def append_block(self, name: str) -> Path:
    assert not self.links and not self.ports and not self.params, f"tried to append block {name} to {self}"
    return Path(self.blocks + (name, ), self.links, self.ports, self.params)

  def append_link(self, name: str) -> Path:
    assert not self.ports and not self.params, f"tried to append link {name} to {self}"
    return Path(self.blocks, self.links + (name, ), self.ports, self.params)

  def append_port(self, name: str) -> Path:
    assert not self.params, f"tried to append port {name} to {self}"
    return Path(self.blocks, self.links, self.ports + (name, ), self.params)

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
      if (isinstance(curr, edgir.Port) or isinstance(curr, edgir.Bundle) or
          isinstance(curr, edgir.HierarchyBlock) or isinstance(curr, edgir.Link)) \
          and name in curr.params:
        return self.append_param(name)._follow_partial_steps(steps[1:], curr.params[name])
      elif (isinstance(curr, edgir.Bundle) or isinstance(curr, edgir.Link) or
            isinstance(curr, edgir.HierarchyBlock)) and name in curr.ports:
        path = self.append_port(name)
        port = edgir.resolve_portlike(curr.ports[name])
        return path._follow_partial_steps(steps[1:], port)
      elif isinstance(curr, edgir.PortArray) and curr.HasField('ports') and name in curr.ports.ports:
        path = self.append_port(name)
        port = edgir.resolve_portlike(curr.ports.ports[name])
        return path._follow_partial_steps(steps[1:], port)
      elif isinstance(curr, edgir.HierarchyBlock) and name in curr.blocks:
        return self.append_block(name)._follow_partial_steps(steps[1:], edgir.resolve_blocklike(curr.blocks[name]))
      elif (isinstance(curr, edgir.HierarchyBlock) or isinstance(curr, edgir.Link)) and name in curr.links.keys():
        return self.append_link(name)._follow_partial_steps(steps[1:], edgir.resolve_linklike(curr.links[name]))
      else:
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
      for name, port in edgir.ordered_ports(elt.bundle):
        self._traverse_portlike(context.append_port(name), port)
    elif elt.HasField('array') and elt.array.HasField('ports'):
      for idx, port in elt.array.ports.ports.items():
        self._traverse_portlike(context.append_port(idx), port)
    else:
      raise ValueError(f"_traverse_portlike encountered unknown type {elt} at {context}")

  def _traverse_block(self, context: TransformContext, elt: edgir.HierarchyBlock) -> None:
    try:
      self.visit_block(context, elt)
    except Exception as e:
      raise type(e)(f"(while visiting Block at {context}) " + str(e)) \
        .with_traceback(sys.exc_info()[2])

    for name, port in edgir.ordered_ports(elt):
      self._traverse_portlike(context.append_port(name), port)
    for name, link in edgir.ordered_links(elt):
      self._traverse_linklike(context.append_link(name), link)
    for name, block in edgir.ordered_blocks(elt):
      self._traverse_blocklike(context.append_block(name), block)

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

      for name, port in elt.link.ports.items():
        self._traverse_portlike(context.append_port(name), port)

      for name, link in elt.link.links.items():
        self._traverse_linklike(context.append_link(name), link)
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
    for name, port in design_copy.contents.ports.items():
      self._traverse_portlike(root_context.append_port(name), port)
    for name, link in design_copy.contents.links.items():
      self._traverse_linklike(root_context.append_link(name), link)
    for name, block in edgir.ordered_blocks(design_copy.contents):
      self._traverse_blocklike(root_context.append_block(name), block)

    return design_copy
