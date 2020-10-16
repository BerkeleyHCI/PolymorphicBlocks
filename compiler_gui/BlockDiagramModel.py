from __future__ import annotations
from typing import NamedTuple, Optional, Dict, Any, List, Union, Tuple  # can't import OrderedDict
from abc import abstractmethod

from collections import OrderedDict
from itertools import chain
from enum import Enum

from edg import edgir
from edg import TransformUtil as tfu


class LinkPortDir(Enum):
  SOURCE = 1
  SINK = 2
  BIDIR = 3


class LinkLike:
  @abstractmethod
  def all_ports(self) -> List[tfu.Path]: ...
  @abstractmethod
  def path(self) -> tfu.Path: ...


class Export(LinkLike):
  def __repr__(self) -> str:
    return f"Export({self.exterior} <> {self.interior})"

  def __init__(self, exterior: tfu.Path, interior: tfu.Path):
    self.exterior = exterior
    self.interior = interior

  def all_ports(self) -> List[tfu.Path]:
    return [self.exterior, self.interior]

  def path(self) -> tfu.Path:
    return self.exterior


class Link(LinkLike):
  def __repr__(self) -> str:
    return f"Link({self.link_path} = {self.ports})"

  def __init__(self, link_path: tfu.Path, link: edgir.Link):
    self.link_path = link_path
    self.link = link
    self.ports: OrderedDict[str, List[tfu.Path]] = OrderedDict()
    for port_name, _ in edgir.ordered_ports(link):
      assert port_name not in self.ports, f"duplicate port name {port_name}"
      self.ports[port_name] = []

  def all_ports(self) -> List[tfu.Path]:
    return list(chain(*[target_ports for port_name, target_ports in self.ports.items()]))

  def path(self) -> tfu.Path:
    return self.link_path


class Block():
  def __init__(self, path: tfu.Path, block: edgir.HierarchyBlock):
    self.path = path
    self.block = block

    self.ports: OrderedDict[str, List[tfu.Path]] = OrderedDict()

    self.subblocks: OrderedDict[str, 'Block'] = OrderedDict()  # abs block path -> Block obj
    self.sublinks: OrderedDict[str, LinkLike] = OrderedDict()  # abs link / external port path -> Link obj

    for port_name, _ in edgir.ordered_ports(block):
      assert port_name not in self.ports, f"duplicate port name {port_name}"
      self.ports[port_name] = []

    for link_name, link in edgir.ordered_links(block):
      link_path = path.append_link(link_name)
      assert link_name not in self.sublinks, f"duplicate link name {link_name}"
      self.sublinks[link_name] = Link(link_path, link.link)

    # TODO control maximum recursion depth?
    for subblock_name, subblock in edgir.ordered_blocks(block):
      if subblock.HasField('hierarchy'):
        subblock_path = path.append_block(subblock_name)
        assert subblock_name not in self.subblocks, f"duplicate link name {subblock_name}"
        self.subblocks[subblock_name] = Block(subblock_path, subblock.hierarchy)

    # build list of connections by link, so we can make an aggregate pass at directionality
    for constr_name, constr in block.constraints.items():
      if constr.HasField('connected'):
        assert constr.connected.link_port.HasField('ref')
        assert constr.connected.block_port.HasField('ref')
        (link_port_path, _) = path.follow(constr.connected.link_port.ref, block)
        (block_port_path, _) = path.follow(constr.connected.block_port.ref, block)
        assert len(link_port_path.links) == 1
        link_obj = self.sublinks[link_port_path.links[0]]
        assert isinstance(link_obj, Link)
        # TODO make sure following path components are array indexes?
        link_obj.ports[link_port_path.ports[0]].append(block_port_path)
        assert len(block_port_path.ports) == 1
        self.subblocks[block_port_path.blocks[-1]].ports[block_port_path.ports[0]].append(link_port_path)
      elif constr.HasField('exported'):
        assert constr.exported.internal_block_port.HasField('ref')
        assert constr.exported.exterior_port.HasField('ref')
        (internal_block_port_path, _) = path.follow(constr.exported.internal_block_port.ref, block)
        (exterior_port_path, _) = path.follow(constr.exported.exterior_port.ref, block)
        pseudolink_name = '.'.join(exterior_port_path.ports)
        # Discard inner paths, so everything goes to one exterior port
        self.sublinks[pseudolink_name] = Export(exterior_port_path, internal_block_port_path)
        assert len(internal_block_port_path.ports) == 1
        self.subblocks[internal_block_port_path.blocks[-1]].ports[internal_block_port_path.ports[0]].append(exterior_port_path)

  def max_depth(self) -> int:
    def process(block: Block, curr: int) -> int:
      if not block.subblocks:
        return curr
      depths = [process(subblock, curr + 1) for subblock in block.subblocks.values()]
      return max(depths)
    return process(self, 0)

def transform_simplify_bridge(block: Block) -> None:
  deleted_subblocks: List[str] = []
  for subblock_name, subblock_obj in block.subblocks.items():
    if subblock_name.startswith('(bridge)'):
      subblock_path = subblock_obj.path

      assert len(subblock_obj.ports) == 2
      assert len(subblock_obj.ports['inner_link']) == 1
      assert len(subblock_obj.ports['outer_port']) == 1
      inner_link_port_path = subblock_obj.ports['inner_link'][0]
      outer_port_path = subblock_obj.ports['outer_port'][0]
      inner_link_linklike = block.sublinks[inner_link_port_path.links[0]]

      # Collapse into inner link
      assert isinstance(inner_link_linklike, Link)
      # TODO replace w/ insert for order preserving
      inner_link_linklike.ports[inner_link_port_path.ports[0]].remove(subblock_path.append_port('inner_link'))
      inner_link_linklike.ports[inner_link_port_path.ports[0]].append(outer_port_path)
      del block.sublinks['.'.join(outer_port_path.ports)]
      deleted_subblocks.append(subblock_name)

  for deleted_subblock in deleted_subblocks:
    del block.subblocks[deleted_subblock]


def transform_simplify_adapter(block: Block) -> None:
  def link_obj_of(port_path: tfu.Path) -> Tuple[str, LinkLike]:
    if port_path.links and port_path.links[0] in block.sublinks:
      link_name = port_path.links[0]
    elif '.'.join(port_path.ports) in block.sublinks:
      link_name = '.'.join(port_path.ports)
    else:
      raise ValueError(f"unable to find link_obj for {port_path}")
    return (link_name, block.sublinks[link_name])

  deleted_subblocks: List[str] = []
  for subblock_name, subblock_obj in block.subblocks.items():
    if subblock_name.startswith('(adapter)'):
      subblock_path = subblock_obj.path

      assert len(subblock_obj.ports) == 2
      assert len(subblock_obj.ports['src']) == 1
      assert len(subblock_obj.ports['dst']) == 1
      src_port_path = subblock_obj.ports['src'][0]
      dst_port_path = subblock_obj.ports['dst'][0]
      src_link_name, src_link_obj = link_obj_of(src_port_path)
      dst_link_name, dst_link_obj = link_obj_of(dst_port_path)

      # prefer to collapse the src link into dst
      if len(src_link_obj.all_ports()) == 2 and isinstance(dst_link_obj, Link):
        src_far_ports = set(src_link_obj.all_ports()) - {subblock_path.append_port('src')}
        src_far_port = src_far_ports.pop()
        assert not src_far_ports

        dst_link_obj_ports = dst_link_obj.ports[dst_port_path.ports[0]]
        # TODO replace w/ insert for order preserving
        dst_link_obj_ports.remove(subblock_path.append_port('dst'))
        dst_link_obj_ports.append(src_far_port)

        del block.sublinks[src_link_name]
        deleted_subblocks.append(subblock_name)
      elif len(dst_link_obj.all_ports()) == 2 and isinstance(src_link_obj, Link):  # otherwise, collapse dst into src
        dst_far_ports = set(dst_link_obj.all_ports()) - {subblock_path.append_port('dst')}
        dst_far_port = dst_far_ports.pop()
        assert not dst_far_ports

        src_link_obj_ports = src_link_obj.ports[src_port_path.ports[0]]
        # TODO replace w/ insert for order preserving
        src_link_obj_ports.remove(subblock_path.append_port('src'))
        src_link_obj_ports.append(dst_far_port)

        del block.sublinks[dst_link_name]
        deleted_subblocks.append(subblock_name)
      else:
        print(f"unable to collapse adapter {subblock_path}: {subblock_obj.ports['src']} => {subblock_obj.ports['dst']}")

  for deleted_subblock in deleted_subblocks:
    del block.subblocks[deleted_subblock]
