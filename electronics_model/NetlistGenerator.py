from functools import cmp_to_key
from itertools import chain
from typing import *

import edgir
from edg_core import *

from . import footprint as kicad
# TODO netlist type maybe should be defined in footprint.py?


def flatten_port(path: TransformUtil.Path, port: edgir.PortLike) -> Iterable[TransformUtil.Path]:
  if port.HasField('port'):
    return [path]
  elif port.HasField('array') and port.array.HasField('ports'):
    return chain(*[flatten_port(path.append_port(name), port) for name, port in port.array.ports.ports.items()])
  else:
    raise ValueError(f"don't know how to flatten netlistable port {port}")


class InvalidNetlistBlockException(BaseException):
  pass


Blocks = Dict[TransformUtil.Path, Tuple[str, str]]  # path -> footprint, value
Edges = Dict[TransformUtil.Path, List[TransformUtil.Path]]  # Pins (block name, port / pin name) -> net-connected Pins
Names = Dict[TransformUtil.Path, TransformUtil.Path]  # Path -> shortened path name
Hierarchy = Dict[TransformUtil.Path, str]  # path -> classname
class NetlistCollect(TransformUtil.Transform):
  def process_blocklike(self, path: TransformUtil.Path, block: Union[edgir.Link, edgir.LinkArray, edgir.HierarchyBlock]) -> None:
    # generate short paths for children first
    short_path = self.short_paths[path]

    if 'error' in block.meta.members.node:
      raise InvalidNetlistBlockException(f"attempt to netlist with error block at {path}")
    elif 'abstract' in block.meta.members.node:
      raise InvalidNetlistBlockException(f"attempt to netlist with abstract block at {path}")

    if isinstance(block, edgir.HierarchyBlock):
      self.hierarchy[path] = block.self_class.target.name

    # TODO handle mixed net/connect operations
    if isinstance(block, edgir.Link) and 'nets' in block.meta.members.node:
      # Consolidate single-net link ports into just the link
      for name, _ in block.ports.items():
        self.short_paths[path.append_port(name)] = short_path
    else:
      for name, _ in block.ports.items():
        self.short_paths[path.append_port(name)] = short_path.append_port(name)

    for name, _ in block.links.items():
      self.short_paths[path.append_link(name)] = short_path.append_link(name)

    main_internal_block_names: List[str] = []
    other_internal_block_names: List[str] = []
    if isinstance(block, edgir.HierarchyBlock):
      main_internal_block_names += [block_name for block_name in block.blocks.keys()
                                    if not block_name.startswith('(bridge)') and not block_name.startswith('(adapter)')]
      other_internal_block_names += [block_name for block_name in block.blocks.keys()
                                     if block_name not in main_internal_block_names]

    if len(main_internal_block_names) == 1:
      name = main_internal_block_names[0]
      self.short_paths[path.append_block(name)] = short_path

      for name in other_internal_block_names:
        self.short_paths[path.append_block(name)] = short_path.append_block(name)
    else:
      for name in main_internal_block_names + other_internal_block_names:
        self.short_paths[path.append_block(name)] = short_path.append_block(name)

    if 'nets' in block.meta.members.node:
      # add all-pairs edges
      # list conversion to deal with iterable-once
      flat_ports = list(chain(*[flatten_port(path.append_port(name), port) for name, port in block.ports.items()]))
      for src_path in flat_ports:
        for dst_path in flat_ports:
          if src_path != dst_path:
            self.edges.setdefault(src_path, []).append(dst_path)

    if 'pinning' in block.meta.members.node:
      footprint_name = self.design.get_value(path.to_tuple() + ('fp_footprint',))
      mfr = self.design.get_value(path.to_tuple() + ('fp_mfr',))
      part = self.design.get_value(path.to_tuple() + ('fp_part',))
      value = self.design.get_value(path.to_tuple() + ('fp_value',))
      refdes_prefix = self.design.get_value(path.to_tuple() + ('fp_refdes_prefix',))
      lcsc_part = self.design.get_value(path.to_tuple() + ('lcsc_part',))

      assert isinstance(footprint_name, str)
      assert isinstance(mfr, str) or mfr is None
      assert isinstance(part, str) or part is None
      assert isinstance(value, str) or value is None
      assert isinstance(lcsc_part, str) or lcsc_part is None
      assert isinstance(refdes_prefix, str)

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

      self.blocks[path] = (
        footprint_name,
        # Uncomment one to set value field
        # TODO this should be a user flag
        value_str  # including manufacturer
        # lcsc_part or ""
        # value  # for TPs
      )

      refdes_id = self.refdes_last.get(refdes_prefix, 0) + 1
      self.refdes_last[refdes_prefix] = refdes_id

      # Uncomment one to set refdes type
      # TODO this should be a user flag
      # self.names[path] = TransformUtil.Path.empty().append_block(refdes_prefix + str(refdes_id))
      self.names[path] = self.short_paths[path]

      for pin_name, pin_path_pb in block.meta.members.node['pinning'].members.node.items():
        pin_path = path.append_port(pin_name)
        self.pins.add(pin_path)
        self.short_paths[pin_path] = short_path.append_port(pin_name)

        path_value = edgir.ValueExpr().FromString(pin_path_pb.bin_leaf)
        assert path_value.HasField('ref')
        src_path = path.follow(path_value.ref, block)[0]

        # Create a unidirectional edge from the port to the footprint pin
        self.edges.setdefault(src_path, []).append(pin_path)
        self.edges.setdefault(pin_path, [])  # create a dummy entry

        self.names[pin_path] = self.names[path].append_port(pin_name)

    for name, constraint in block.constraints.items():
      if constraint.HasField('connected'):
        self.process_connected(path, block, constraint.connected)
      elif constraint.HasField('exported'):
        self.process_exported(path, block, constraint.exported)
      elif constraint.HasField('exportedTunnel'):
        self.process_exported(path, block, constraint.exportedTunnel)

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
      assert elt1[1].ports.keys() == elt2[1].ports.keys(), f"mismatched bundle types {elt1}, {elt2}"
      for key in elt1[1].ports.keys():
        self.connect_ports(
          (elt1[0].append_port(key), edgir.resolve_portlike(elt1[1].ports[key])),
          (elt2[0].append_port(key), edgir.resolve_portlike(elt2[1].ports[key])))
      # don't need to create the bundle connect, since Bundles can't be CircuitPorts
    else:
      raise ValueError(f"can't connect types {elt1}, {elt2}")

  def visit_portlike(self, context: TransformUtil.TransformContext, port: edgir.PortLike) -> None:
    self.pins.add(context.path)

    short_path = self.short_paths[context.path]
    if port.HasField('bundle'):  # TODO maybe shorten if just one?
      for name, _ in port.bundle.ports.items():
        self.short_paths[context.path.append_port(name)] = short_path.append_port(name)
    elif port.HasField('array') and port.array.HasField('ports'):
      for name in port.array.ports.ports.keys():
        self.short_paths[context.path.append_port(name)] = short_path.append_port(name)

  def visit_block(self, context: TransformUtil.TransformContext, block: edgir.BlockTypes) -> None:
    self.process_blocklike(context.path, block)

  def visit_link(self, context: TransformUtil.TransformContext, link: edgir.Link) -> None:
    self.process_blocklike(context.path, link)

  def visit_linkarray(self, context: TransformUtil.TransformContext, link: edgir.LinkArray) -> None:
    self.process_blocklike(context.path, link)

  def __init__(self, design: CompiledDesign):
    self.blocks: Blocks = {}
    self.edges: Edges = {}
    self.short_paths: Names = {TransformUtil.Path.empty(): TransformUtil.Path.empty()}  # seed root
    self.hierarchy: Hierarchy = {}
    self.pins: Set[TransformUtil.Path] = set()
    self.names: Names = {}

    self.refdes_last: Dict[str, int] = {}

    self.design = design

  def run(self) -> Tuple[Blocks, Edges, Names, Hierarchy, Names]:
    self.transform_design(self.design.design)

    # Sanity check to ensure all pins exist
    for pin_src, pins_dst in self.edges.items():
      assert pin_src in self.pins, f"missing net edge src pin {pin_src}"
      for pin_dst in pins_dst:
        assert pin_dst in self.pins, f"missing net edge dst pin {pin_dst}"

    return (self.blocks, self.edges, self.short_paths, self.hierarchy, self.names)


def path_to_pin(path: TransformUtil.Path) -> kicad.Pin:
  assert not path.links and not path.params
  return kicad.Pin('.'.join(path.blocks), '.'.join(path.ports))


class Netlist(NamedTuple):
  # TODO use TransformUtil.Path across the board
  blocks: Mapping[str, kicad.Block]  # block name: footprint name
  nets: Mapping[str, Iterable[kicad.Pin]]  # net name: list of member pins
  types: Mapping[TransformUtil.Path, str]  # types of hierarchy components


class NetlistGenerator:
  def generate(self, design: CompiledDesign) -> Netlist:
    # TODO another algorithm is for each block, return its footprints and connected nets, and merge nets incrementally
    blocks, edges, short_paths, hierarchy, names = NetlistCollect(design).run()

    seen: Set[TransformUtil.Path] = set()
    nets: List[Set[TransformUtil.Path]] = []

    for port, conns in edges.items():
      if port not in seen:
        curr_net: Set[TransformUtil.Path] = set()
        def traverse_pin(pin: TransformUtil.Path):
          if pin not in seen:
            seen.add(pin)
            curr_net.add(pin)
            for port in edges[pin]:
              traverse_pin(port)
        traverse_pin(port)
        nets.append(curr_net)

    def name_net(net: Set[TransformUtil.Path]) -> str:
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
        elif len(pin1.ports) == 1 and pin1.ports[0].isnumeric and \
            (len(pin2.ports) != 1 or (pin2.ports and not pin2.ports[-1].isnumeric())):  # disprefer number-only ports
          return 1
        elif len(pin2.ports) == 1 and pin2.ports[0].isnumeric and \
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

    def name_pin(pin: TransformUtil.Path) -> TransformUtil.Path:
      if pin in short_paths:
        return short_paths[pin]
      else:
        return pin

    named_nets = {name_net(set([name_pin(pin) for pin in net])): net for net in nets}

    return Netlist(
      {str(names[block]): kicad.Block(footprint, value, list(short_paths[block].blocks))
        for block, (footprint, value) in blocks.items()},
      {name: set([path_to_pin(names[pin])
        for pin in net if pin in names]) for name, net in named_nets.items()},
      hierarchy
    )
