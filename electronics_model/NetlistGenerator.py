from functools import cmp_to_key
from itertools import chain
from typing import *

import edgir
from edg_core import *
from . import footprint as kicad

class InvalidNetlistBlockException(BaseException):
  pass


class InvalidPackingException(BaseException):
  pass


class Netlist(NamedTuple):  # TODO use TransformUtil.Path across the board
  blocks: Dict[str, kicad.Block]  # block name: footprint name
  nets: Dict[str, List[kicad.Pin]]  # net name: list of member pins


Blocks = Dict[TransformUtil.Path, kicad.Block]  # path -> Block
Edges = Dict[TransformUtil.Path, List[TransformUtil.Path]]  # Pins (block name, port / pin name) -> net-connected Pins
AssertConnected = List[Tuple[TransformUtil.Path, TransformUtil.Path]]
Names = Dict[TransformUtil.Path, TransformUtil.Path]  # Path -> shortened path name
ClassPaths = Dict[TransformUtil.Path, List[str]]  # Path -> class names corresponding to shortened path name
class NetlistTransform(TransformUtil.Transform):
  @staticmethod
  def path_to_pin(path: TransformUtil.Path) -> kicad.Pin:
    assert not path.links and not path.params
    return kicad.Pin('.'.join(path.blocks), '.'.join(path.ports))

  @staticmethod
  def flatten_port(path: TransformUtil.Path, port: edgir.PortLike) -> Iterable[TransformUtil.Path]:
    if port.HasField('port'):
      return [path]
    elif port.HasField('array') and port.array.HasField('ports'):
      return chain(*[NetlistTransform.flatten_port(path.append_port(port_pair.name), port_pair.value)
                     for port_pair in port.array.ports.ports])
    else:
      raise ValueError(f"don't know how to flatten netlistable port {port}")

  def __init__(self, design: CompiledDesign, refdes_mode: str = "pathName"):
    self.blocks: Blocks = {}
    self.edges: Edges = {}
    self.assert_connected: AssertConnected = []
    self.short_paths: Names = {TransformUtil.Path.empty(): TransformUtil.Path.empty()}  # seed root
    self.class_paths: ClassPaths = {TransformUtil.Path.empty(): []}  # seed root
    self.pins: Set[TransformUtil.Path] = set()
    self.names: Names = {}

    self.design = design
    self.refdes_mode = refdes_mode

  def process_blocklike(self, path: TransformUtil.Path, block: Union[edgir.Link, edgir.LinkArray, edgir.HierarchyBlock]) -> None:
    # generate short paths for children first
    short_path = self.short_paths[path]
    class_path = self.class_paths[path]

    # TODO handle mixed net/connect operations
    if isinstance(block, edgir.Link) and 'nets' in block.meta.members.node:
      # Consolidate single-net link ports into just the link
      for port_pair in block.ports:
        self.short_paths[path.append_port(port_pair.name)] = short_path

    else:
      for port_pair in block.ports:
        self.short_paths[path.append_port(port_pair.name)] = short_path.append_port(port_pair.name)

    for link_pair in block.links:
      self.short_paths[path.append_link(link_pair.name)] = short_path.append_link(link_pair.name)
      self.class_paths[path.append_link(link_pair.name)] = class_path + [link_pair.value.link.self_class.target.name]

    main_internal_blocks: Dict[str, edgir.BlockLike] = {}
    other_internal_blocks: Dict[str, edgir.BlockLike] = {}
    if isinstance(block, edgir.HierarchyBlock):
      for block_pair in block.blocks:
        if not block_pair.name.startswith('(bridge)') and not block_pair.name.startswith('(adapter)'):
          main_internal_blocks[block_pair.name] = block_pair.value
        else:
          other_internal_blocks[block_pair.name] = block_pair.value

    if len(main_internal_blocks) == 1:
      name = list(main_internal_blocks.keys())[0]
      self.short_paths[path.append_block(name)] = short_path
      self.class_paths[path.append_block(name)] = class_path
    else:
      for (name, subblock) in main_internal_blocks.items():
        self.short_paths[path.append_block(name)] = short_path.append_block(name)
        self.class_paths[path.append_block(name)] = class_path + [subblock.hierarchy.self_class.target.name]

    for (name, subblock) in other_internal_blocks.items():
      self.short_paths[path.append_block(name)] = short_path.append_block(name)
      self.class_paths[path.append_block(name)] = class_path + [subblock.hierarchy.self_class.target.name]

    if 'nets' in block.meta.members.node:
      # add all-pairs edges
      # list conversion to deal with iterable-once
      flat_ports = list(chain(*[self.flatten_port(path.append_port(port_pair.name), port_pair.value)
                                for port_pair in block.ports]))
      for src_path in flat_ports:
        for dst_path in flat_ports:
          if src_path != dst_path:
            self.edges.setdefault(src_path, []).append(dst_path)

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
      value_comps = [
        part_str,
        value
      ]
      value_str = " - ".join(filter(None, value_comps))

      self.blocks[path] = kicad.Block(
        footprint_name,
        refdes,
        part_str,

        # Uncomment one to set value field
        # TODO this should be a user flag
        value_str,  # including manufacturer
        # lcsc_part or "",

        list(path.blocks),
        list(self.short_paths[path].blocks),
        self.class_paths[path],
      )

      if self.refdes_mode == "pathName":
        self.names[path] = self.short_paths[path]
      elif self.refdes_mode == "refdes":
        self.names[path] = TransformUtil.Path.empty().append_block(refdes)
      else:
        raise ValueError(f"Invalid valueMode value {self.refdes_mode}")

      for pin_spec in footprint_pinning:
        assert isinstance(pin_spec, str)
        pin_spec_split = pin_spec.split('=')
        assert len(pin_spec_split) == 2
        pin_name = pin_spec_split[0]
        port_path = edgir.LocalPathList(pin_spec_split[1].split('.'))

        pin_path = path.append_port(pin_name)
        self.pins.add(pin_path)
        self.short_paths[pin_path] = short_path.append_port(pin_name)

        src_path = path.follow(port_path, block)[0]

        # Create a unidirectional edge from the port to the footprint pin
        self.edges.setdefault(src_path, []).append(pin_path)
        self.edges.setdefault(pin_path, [])  # create a dummy entry

        self.names[pin_path] = self.names[path].append_port(pin_name)

    for constraint_pair in block.constraints:
      if constraint_pair.value.HasField('connected'):
        self.process_connected(path, block, constraint_pair.value.connected)
      elif constraint_pair.value.HasField('exported'):
        self.process_exported(path, block, constraint_pair.value.exported)
      elif constraint_pair.value.HasField('exportedTunnel'):
        self.process_exported(path, block, constraint_pair.value.exportedTunnel)

  def process_connected(self, path: TransformUtil.Path, current: edgir.EltTypes, constraint: edgir.ConnectedExpr) -> None:
    assert constraint.block_port.HasField('ref')
    assert constraint.link_port.HasField('ref')
    self.connect_ports(
      path.follow(constraint.block_port.ref, current),
      path.follow(constraint.link_port.ref, current))

  def process_exported(self, path: TransformUtil.Path, current: edgir.EltTypes, constraint: edgir.ExportedExpr) -> None:
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

  def visit_portlike(self, context: TransformUtil.TransformContext, port: edgir.PortLike) -> None:
    self.pins.add(context.path)

    short_path = self.short_paths[context.path]
    if port.HasField('bundle'):  # TODO maybe shorten if just one?
      for port_pair in port.bundle.ports:
        self.short_paths[context.path.append_port(port_pair.name)] = short_path.append_port(port_pair.name)
    elif port.HasField('array') and port.array.HasField('ports'):
      for port_pair in port.array.ports.ports:
        self.short_paths[context.path.append_port(port_pair.name)] = short_path.append_port(port_pair.name)

  def visit_block(self, context: TransformUtil.TransformContext, block: edgir.BlockTypes) -> None:
    self.process_blocklike(context.path, block)

  def visit_link(self, context: TransformUtil.TransformContext, link: edgir.Link) -> None:
    self.process_blocklike(context.path, link)

  def visit_linkarray(self, context: TransformUtil.TransformContext, link: edgir.LinkArray) -> None:
    self.process_blocklike(context.path, link)

  @staticmethod
  def name_net(net: Iterable[TransformUtil.Path]) -> str:
    """Names a net based on all the paths of ports and links that are part of the net."""
    def pin_name_goodness(pin1: TransformUtil.Path, pin2: TransformUtil.Path) -> int:
      assert not pin1.params and not pin2.params
      # TODO rewrite rules to based on _anon internal depth, though elt[0] is likely where the _anon will be
      if pin1.links and pin1.links[0].startswith('anon') and \
          (not pin2.links or pin2.links[0].startswith('anon')):  # disprefer anon over anything else
        return 1
      elif (not pin1.links or pin1.links[0].startswith('anon')) and \
          (pin2.links and pin2.links[0].startswith('anon')):  # disprefer anon over anything else
        return -1
      elif len(pin1.blocks) != len(pin2.blocks):  # prefer shorter block paths
        return len(pin1.blocks) - len(pin2.blocks)
      elif len(pin1.ports) == 1 and pin1.ports[0].isnumeric() and \
          (len(pin2.ports) != 1 or (pin2.ports and not pin2.ports[-1].isnumeric())):  # disprefer number-only ports
        return 1
      elif len(pin2.ports) == 1 and pin2.ports[0].isnumeric() and \
          (len(pin1.ports) != 1 or (pin1.ports and not pin1.ports[-1].isnumeric())):  # disprefer number-only ports
        return -1
      elif len(pin1.ports) != len(pin2.ports):  # prefer shorter port lengths
        return len(pin1.ports) - len(pin2.ports)
      elif pin1.links and not pin2.links:  # prefer links
        return -1
      elif not pin1.links and pin2.links:
        return 1
      else:  # prefer shorter pin paths
        return len(pin1.ports) - len(pin2.ports)
    best_path = sorted(net, key=cmp_to_key(pin_name_goodness))[0]
    return str(best_path)

  def run(self) -> Netlist:
    self.transform_design(self.design.design)

    # Sanity check to ensure all pins exist
    for pin_src, pins_dst in self.edges.items():
      assert pin_src in self.pins, f"missing net edge src pin {pin_src}"
      for pin_dst in pins_dst:
        assert pin_dst in self.pins, f"missing net edge dst pin {pin_dst}"

    # Convert to the netlist format
    seen: Set[TransformUtil.Path] = set()
    nets: List[List[TransformUtil.Path]] = []  # use lists instead of sets to preserve ordering

    for port, conns in self.edges.items():
      if port not in seen:
        curr_net: List[TransformUtil.Path] = []
        def traverse_pin(pin: TransformUtil.Path):
          if pin not in seen:
            seen.add(pin)
            curr_net.append(pin)
            for port in self.edges[pin]:
              traverse_pin(port)
        traverse_pin(port)
        nets.append(curr_net)

    pin_to_net: Dict[TransformUtil.Path, List[TransformUtil.Path]] = {}  # values share reference to nets
    for net in nets:
      for pin in net:
        pin_to_net[pin] = net

    for (connected1, connected2) in self.assert_connected:
      if pin_to_net[connected1] is not pin_to_net[connected2]:
        raise InvalidPackingException(f"packed pins {connected1}, {connected2} not connected")

    def name_pin(pin: TransformUtil.Path) -> TransformUtil.Path:
      if pin in self.short_paths:
        return self.short_paths[pin]
      else:
        return pin

    named_nets = {self.name_net([name_pin(pin) for pin in net]): net
                  for net in nets}

    netlist_blocks = {str(self.names[block_path]): block
                      for block_path, block in self.blocks.items()}
    netlist_nets = {name: [self.path_to_pin(self.names[pin])
                            for pin in net if pin in self.names]
                    for name, net in named_nets.items()}

    return Netlist(netlist_blocks, netlist_nets)
