from functools import cmp_to_key
from itertools import chain
from typing import *

import edgir
from edg_core import *


class InvalidNetlistBlockException(BaseException):
  pass


class InvalidPackingException(BaseException):
  pass


class NetBlock(NamedTuple):
  footprint: str
  refdes: str
  part: str
  value: str  # gets written directly to footprint
  full_path: TransformUtil.Path  # full path to this footprint
  path: List[str]  # short path to this footprint
  class_path: List[edgir.LibraryPath]  # classes on short path to this footprint

class NetPin(NamedTuple):
  block_path: TransformUtil.Path  # full path to the block
  pin_name: str

class Net(NamedTuple):
  name: str
  pins: List[NetPin]
  ports: List[TransformUtil.Path]

class Netlist(NamedTuple):
  blocks: List[NetBlock]
  nets: List[Net]


Blocks = Dict[TransformUtil.Path, NetBlock]  # Path -> Block
Edges = Dict[TransformUtil.Path, List[TransformUtil.Path]]  # Port Path -> connected Port Paths
AssertConnected = List[Tuple[TransformUtil.Path, TransformUtil.Path]]
ClassPaths = Dict[TransformUtil.Path, List[edgir.LibraryPath]]  # Path -> class names corresponding to shortened path name
class NetlistTransform(TransformUtil.Transform):
  @staticmethod
  def flatten_port(path: TransformUtil.Path, port: edgir.PortLike) -> Iterable[TransformUtil.Path]:
    if port.HasField('port'):
      return [path]
    elif port.HasField('array') and port.array.HasField('ports'):
      return chain(*[NetlistTransform.flatten_port(path.append_port(port_pair.name), port_pair.value)
                     for port_pair in port.array.ports.ports])
    else:
      raise ValueError(f"don't know how to flatten netlistable port {port}")

  def __init__(self, design: CompiledDesign):
    self.blocks: Blocks = {}
    self.edges: Edges = {}  # as port Paths, including intermediates
    self.pins: Dict[TransformUtil.Path, List[NetPin]] = {}  # mapping from Port to pad
    self.assert_connected: AssertConnected = []
    self.short_paths: Dict[TransformUtil.Path, List[str]] = {TransformUtil.Path.empty(): []}  # seed root
    self.class_paths: ClassPaths = {TransformUtil.Path.empty(): []}  # seed root

    self.design = design

  def process_blocklike(self, path: TransformUtil.Path, block: Union[edgir.Link, edgir.LinkArray, edgir.HierarchyBlock]) -> None:
    if isinstance(block, edgir.HierarchyBlock):
      # generate short paths for children first, for Blocks only
      main_internal_blocks: Dict[str, edgir.BlockLike] = {}
      other_internal_blocks: Dict[str, edgir.BlockLike] = {}
      if isinstance(block, edgir.HierarchyBlock):
        for block_pair in block.blocks:
          subblock = block_pair.value
          # ignore pseudoblocks like bridges and adapters that have no internals
          if not subblock.hierarchy.blocks and 'fp_is_footprint' not in subblock.hierarchy.meta.members.node:
            other_internal_blocks[block_pair.name] = block_pair.value
          else:
            main_internal_blocks[block_pair.name] = block_pair.value

      short_path = self.short_paths[path]
      class_path = self.class_paths[path]

      if len(main_internal_blocks) == 1:
        name = list(main_internal_blocks.keys())[0]
        self.short_paths[path.append_block(name)] = short_path
        self.class_paths[path.append_block(name)] = class_path
      else:
        for (name, subblock) in main_internal_blocks.items():
          self.short_paths[path.append_block(name)] = short_path + [name]
          self.class_paths[path.append_block(name)] = class_path + [subblock.hierarchy.self_class]

      for (name, subblock) in other_internal_blocks.items():
        self.short_paths[path.append_block(name)] = short_path + [name]
        self.class_paths[path.append_block(name)] = class_path + [subblock.hierarchy.self_class]

    if 'nets' in block.meta.members.node:
      # add self as a net
      # list conversion to deal with iterable-once
      flat_ports = list(chain(*[self.flatten_port(path.append_port(port_pair.name), port_pair.value)
                                for port_pair in block.ports]))
      self.edges.setdefault(path, []).extend(flat_ports)
      for port_path in flat_ports:
        self.edges.setdefault(port_path, []).append(path)

    if 'nets_packed' in block.meta.members.node:
      # this connects the first source to all destinations, then asserts all the sources are equal
      # this leaves the sources unconnected, to be connected externally and checked at the end
      src_port_name = block.meta.members.node['nets_packed'].members.node['src'].text_leaf
      dst_port_name = block.meta.members.node['nets_packed'].members.node['dst'].text_leaf
      flat_srcs = list(self.flatten_port(path.append_port(src_port_name), edgir.pair_get(block.ports, src_port_name)))
      flat_dsts = list(self.flatten_port(path.append_port(dst_port_name), edgir.pair_get(block.ports, dst_port_name)))
      assert flat_srcs, "missing source port(s) for packed net"
      for dst_path in flat_dsts:
        self.edges.setdefault(flat_srcs[0], []).append(dst_path)
        self.edges.setdefault(dst_path, []).append(flat_srcs[0])
      for src_path in flat_srcs:  # assert all sources connected
        for dst_path in flat_srcs:
          self.assert_connected.append((src_path, dst_path))

    if 'fp_is_footprint' in block.meta.members.node:
      footprint_name = self.design.get_value(path.to_tuple() + ('fp_footprint',))
      footprint_pinning = self.design.get_value(path.to_tuple() + ('fp_pinning',))
      mfr = self.design.get_value(path.to_tuple() + ('fp_mfr',))
      part = self.design.get_value(path.to_tuple() + ('fp_part',))
      value = self.design.get_value(path.to_tuple() + ('fp_value',))
      refdes = self.design.get_value(path.to_tuple() + ('fp_refdes',))
      lcsc_part = self.design.get_value(path.to_tuple() + ('lcsc_part',))

      assert isinstance(footprint_name, str)
      assert isinstance(footprint_pinning, list)
      assert isinstance(mfr, str) or mfr is None
      assert isinstance(part, str) or part is None
      assert isinstance(value, str) or value is None
      assert isinstance(lcsc_part, str) or lcsc_part is None
      assert isinstance(refdes, str)

      part_comps = [
        part,
        f"({mfr})" if mfr else ""
      ]
      part_str = " ".join(filter(None, part_comps))
      value_str = value if value else (part if part else '')
      self.blocks[path] = NetBlock(
        footprint_name,
        refdes,
        part_str,
        value_str,
        path,
        self.short_paths[path],
        self.class_paths[path],
      )

      for pin_spec in footprint_pinning:
        assert isinstance(pin_spec, str)
        pin_spec_split = pin_spec.split('=')
        assert len(pin_spec_split) == 2
        pin_name = pin_spec_split[0]
        pin_port_path = edgir.LocalPathList(pin_spec_split[1].split('.'))

        src_path = path.follow(pin_port_path, block)[0]
        self.edges.setdefault(src_path, [])  # make sure there is a port entry so single-pin nets are named
        self.pins.setdefault(src_path, []).append(NetPin(path, pin_name))

    for constraint_pair in block.constraints:
      if constraint_pair.value.HasField('connected'):
        self.process_connected(path, block, constraint_pair.value.connected)
      elif constraint_pair.value.HasField('exported'):
        self.process_exported(path, block, constraint_pair.value.exported)
      elif constraint_pair.value.HasField('exportedTunnel'):
        self.process_exported(path, block, constraint_pair.value.exportedTunnel)
      elif constraint_pair.value.HasField('connectedArray'):
        for expanded_connect in constraint_pair.value.connectedArray.expanded:
          self.process_connected(path, block, expanded_connect)
      elif constraint_pair.value.HasField('exportedArray'):
        for expanded_export in constraint_pair.value.exportedArray.expanded:
          self.process_exported(path, block, expanded_export)

  def process_connected(self, path: TransformUtil.Path, current: edgir.EltTypes, constraint: edgir.ConnectedExpr) -> None:
    if constraint.expanded:
      assert len(constraint.expanded) == 1
      self.process_connected(path, current, constraint.expanded[0])
      return
    assert constraint.block_port.HasField('ref')
    assert constraint.link_port.HasField('ref')
    self.connect_ports(
      path.follow(constraint.block_port.ref, current),
      path.follow(constraint.link_port.ref, current))

  def process_exported(self, path: TransformUtil.Path, current: edgir.EltTypes, constraint: edgir.ExportedExpr) -> None:
    if constraint.expanded:
      assert len(constraint.expanded) == 1
      self.process_exported(path, current, constraint.expanded[0])
      return
    assert constraint.internal_block_port.HasField('ref')
    assert constraint.exterior_port.HasField('ref')
    self.connect_ports(
      path.follow(constraint.internal_block_port.ref, current),
      path.follow(constraint.exterior_port.ref, current))

  def connect_ports(self, elt1: Tuple[TransformUtil.Path, edgir.EltTypes], elt2: Tuple[TransformUtil.Path, edgir.EltTypes]) -> None:
    """Recursively connect ports as applicable"""
    if isinstance(elt1[1], edgir.Port) and isinstance(elt2[1], edgir.Port):
      self.edges.setdefault(elt1[0], []).append(elt2[0])
      self.edges.setdefault(elt2[0], []).append(elt1[0])
    elif isinstance(elt1[1], edgir.Bundle) and isinstance(elt2[1], edgir.Bundle):
      elt1_names = list(map(lambda pair: pair.name, elt1[1].ports))
      elt2_names = list(map(lambda pair: pair.name, elt2[1].ports))
      assert elt1_names == elt2_names, f"mismatched bundle types {elt1}, {elt2}"
      for key in elt2_names:
        self.connect_ports(
          (elt1[0].append_port(key), edgir.resolve_portlike(edgir.pair_get(elt1[1].ports, key))),
          (elt2[0].append_port(key), edgir.resolve_portlike(edgir.pair_get(elt2[1].ports, key))))
      # don't need to create the bundle connect, since Bundles can't be CircuitPorts
    else:
      raise ValueError(f"can't connect types {elt1}, {elt2}")

  def visit_block(self, context: TransformUtil.TransformContext, block: edgir.BlockTypes) -> None:
    self.process_blocklike(context.path, block)

  def visit_link(self, context: TransformUtil.TransformContext, link: edgir.Link) -> None:
    self.process_blocklike(context.path, link)

  def visit_linkarray(self, context: TransformUtil.TransformContext, link: edgir.LinkArray) -> None:
    self.process_blocklike(context.path, link)

  @staticmethod
  def name_net(net: Iterable[TransformUtil.Path], net_prefix: str) -> str:
    """Names a net based on all the paths of ports and links that are part of the net."""
    # higher criteria are preferred, True or larger number is preferred
    CRITERIA: List[Callable[[TransformUtil.Path], Union[bool, int]]] = [
      lambda pin: not (pin.blocks and pin.blocks[-1].startswith('(adapter)')),
      lambda pin: not (pin.links and (pin.links[0].startswith('anon') or pin.links[0].startswith('_'))),
      lambda pin: -len(pin.blocks),  # prefer shorter block paths
      lambda pin: len(pin.links),  # prefer longer link paths
      lambda pin: -len(pin.ports),  # prefer shorter (or no) port lengths
      lambda pin: not(pin.ports and pin.ports[-1].isnumeric()),  # disprefer number-only ports
    ]
    def pin_name_goodness(pin1: TransformUtil.Path, pin2: TransformUtil.Path) -> int:
      assert not pin1.params and not pin2.params
      for test in CRITERIA:
        pin1_result = test(pin1)
        pin2_result = test(pin2)
        if pin1_result == pin2_result:
          continue
        if isinstance(pin1_result, bool) and isinstance(pin2_result, bool):
          if pin1_result:
            return -1
          else:
            return 1
        elif isinstance(pin1_result, int) and isinstance(pin2_result, int):
          return pin2_result - pin1_result
        else:
          raise ValueError("mismatched result types")
      return 0
    best_path = sorted(net, key=cmp_to_key(pin_name_goodness))[0]

    return net_prefix + str(best_path)

  def run(self) -> Netlist:
    self.transform_design(self.design.design)

    # Convert to the netlist format
    seen: Set[TransformUtil.Path] = set()
    nets: List[List[TransformUtil.Path]] = []  # lists preserve ordering

    for port, conns in self.edges.items():
      if port not in seen:
        curr_net: List[TransformUtil.Path] = []
        frontier: List[TransformUtil.Path] = [port]  # use BFS to maintain ordering instead of simpler DFS
        while frontier:
          pin = frontier.pop(0)
          if pin not in seen:
            seen.add(pin)
            curr_net.append(pin)
            frontier.extend(self.edges[pin])
        nets.append(curr_net)

    pin_to_net: Dict[TransformUtil.Path, List[TransformUtil.Path]] = {}  # values share reference to nets
    for net in nets:
      for pin in net:
        pin_to_net[pin] = net

    for (connected1, connected2) in self.assert_connected:
      if pin_to_net[connected1] is not pin_to_net[connected2]:
        raise InvalidPackingException(f"packed pins {connected1}, {connected2} not connected")

    board_refdes_prefix = self.design.get_value(('refdes_prefix',))
    if board_refdes_prefix is not None:
      assert isinstance(board_refdes_prefix, str)
      net_prefix = board_refdes_prefix
    else:
      net_prefix = ''
    named_nets = {self.name_net(net, net_prefix): net for net in nets}

    netlist_blocks = [block for path, block in self.blocks.items()]
    netlist_nets = [Net(name,
                        list(chain(*[self.pins[port] for port in net if port in self.pins])),
                        net)
                    for name, net in named_nets.items()]

    return Netlist(netlist_blocks, netlist_nets)
