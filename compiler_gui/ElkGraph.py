from __future__ import annotations
from typing import NamedTuple, Optional, Dict, Any, List, Union, Tuple  # can't import OrderedDict
from abc import abstractmethod

from .BlockDiagramModel import Block, LinkLike, Link, Export

import subprocess
import time
from enum import Enum
from collections import OrderedDict
import os

from edg import edgir
from edg import TransformUtil as tfu

from py4j.java_gateway import JavaGateway  # type: ignore

gateway = JavaGateway()


class LinkPortDir(Enum):
  SOURCE = 1
  SINK = 2
  BIDIR = 3


class ElkGraph():
  gateway: Optional[JavaGateway] = None
  elk_process: Optional[Any] = None

  @classmethod
  def start_gateway(cls):
    if os.path.exists('compiler_gui/resources/java/py4j_elk/out/artifacts/py4j_elk_jar/py4j_elk.jar'):
      jar_path = 'compiler_gui/resources/java/py4j_elk/out/artifacts/py4j_elk_jar/py4j_elk.jar'
      print("Using development JAR")
    elif os.path.exists('compiler_gui/resources/java/py4j_elk.jar'):
      jar_path = 'compiler_gui/resources/java/py4j_elk.jar'
      print("Using precompiled JAR")
    else:
      raise ValueError("No elk/py4j JAR found")

    cls.elk_process = subprocess.Popen(
      'java -jar ' + jar_path,
      shell=True,  # apparently makes it possible for py4j to open the socket w/ subprocess?!
      stdin=subprocess.PIPE,
      stdout=subprocess.PIPE)
    assert cls.elk_process.stdout is not None
    output = cls.elk_process.stdout.readline().decode('utf-8')
    if output.strip().rstrip() != "Gateway Server Started":
      cls.elk_process.kill()
      raise ChildProcessError(f"unexpected output from ELK JAR: {output}")
    time.sleep(0.2)  # needed for the connection to open?!
    cls.gateway = JavaGateway()  # TODO this is global, maybe shouldn't be?

  @classmethod
  def close_gateway(cls):
    assert cls.gateway is not None and cls.elk_process is not None
    cls.gateway.close()
    cls.elk_process.stdin.write(b"\n")

  def __init__(self, root_block: Block, depth: int = 1):
    if self.gateway is None:
      raise RuntimeError("ELK JAR Gateway not started. Call ElkGraph.start_gateway.")

    self.blocks: Dict[str, tfu.Path] = {}
    self.ports: Dict[str, tfu.Path] = {}
    self.links: Dict[str, tfu.Path] = {}

    self.root = gateway.createGraph()
    self._process_block(root_block, self.root, {}, depth - 1, {})
    self.root = gateway.layout(self.root)

  def to_json(self, omit_layout: bool = False) -> str:
    return gateway.jsonFromElk(self.root, omit_layout)

  def _process_block(self, block: Block, containing_node: Any, port_nodes: Dict[tfu.Path, Any],
                     remaining_depth: int, port_dirs: Dict[tfu.Path, LinkPortDir]) -> None:
    # instantiate the remaining links and blocks
    subblock_port_nodes: Dict[tfu.Path, Any] = {}
    subblock_nodes: Dict[str, Any] = {}
    for subblock_name, subblock_obj in block.subblocks.items():
      subblock_path = subblock_obj.path
      subblock_class = subblock_obj.block.superclasses[0].target.name.split('.')[-1]  # TODO dedup with superclass-to-str
      subblock_node = gateway.createNode(containing_node, f"{subblock_name}: {subblock_class}")
      subblock_nodes[subblock_name] = subblock_node
      self.blocks[subblock_node.getIdentifier()] = subblock_path
      gateway.setMinSize(subblock_node, 200, 0)
      for subblock_port_name, subblock_port in subblock_obj.ports.items():
        subblock_port_path = subblock_path.append_port(subblock_port_name)
        subblock_port_node = gateway.createPort(subblock_node, subblock_port_name)
        subblock_port_nodes[subblock_port_path] = subblock_port_node
        self.ports[subblock_port_node.getIdentifier()] = subblock_port_path

    subblock_port_dirs: Dict[tfu.Path, LinkPortDir] = {}
    all_port_nodes = port_nodes.copy()
    all_port_nodes.update(subblock_port_nodes)
    for link_path, link_obj in block.sublinks.items():
      link_port_dirs = self._make_link_edges(link_obj, all_port_nodes, containing_node, port_dirs)
      subblock_port_dirs.update(link_port_dirs)

    # recurse inside blocks as necessary
    if remaining_depth > 0:
      for subblock_name, subblock_obj in block.subblocks.items():
        self._process_block(subblock_obj, subblock_nodes[subblock_name], subblock_port_nodes,
                            remaining_depth - 1, subblock_port_dirs)

  @classmethod
  def _link_port_dir(cls, link_class: edgir.LibraryPath, link_port: str) -> LinkPortDir:
    if link_class.target.name in ["electronics_model.DigitalPorts.DigitalLink",
                                  "electronics_model.ElectricalPorts.ElectricalLink",
                                  "electronics_model.AnalogPort.AnalogLink",
                                  "electronics_model.SpeakerPort.SpeakerLink"]:
      if link_port in ('source', 'single_sources'):
        return LinkPortDir.SOURCE
      elif link_port in ('sinks', 'sink'):
        return LinkPortDir.SINK
      elif link_port in ('bidirs', 'passives'):
        return LinkPortDir.BIDIR
    elif link_class.target.name == "electronics_model.PassivePort.PassiveLink":
      return LinkPortDir.BIDIR
    elif link_class.target.name == "electronics_model.CrystalPort.CrystalLink":
      if link_port == 'crystal':
        return LinkPortDir.SINK
      elif link_port == 'driver':
        return LinkPortDir.SOURCE
    elif link_class.target.name == "electronics_model.DebugPorts.SwdLink":
      if link_port == 'host':
        return LinkPortDir.SOURCE
      elif link_port == 'device':
        return LinkPortDir.SINK
    elif link_class.target.name == "electronics_model.UartPort.UartLink":
      if link_port == 'a':
        return LinkPortDir.SOURCE
      elif link_port == 'b':
        return LinkPortDir.SINK
    elif link_class.target.name == "electronics_model.UsbPort.UsbLink":
      if link_port == 'host':
        return LinkPortDir.SOURCE
      elif link_port == 'device' or link_port == 'passive':
        return LinkPortDir.SINK
    elif link_class.target.name == "electronics_model.SpiPort.SpiLink":
      if link_port == 'master':
        return LinkPortDir.SOURCE
      elif link_port == 'devices':
        return LinkPortDir.SINK
    elif link_class.target.name == "electronics_model.I2cPort.I2cLink":
      if link_port == 'master' or link_port == 'pull':
        return LinkPortDir.SOURCE
      elif link_port == 'devices':
        return LinkPortDir.SINK
    elif link_class.target.name == "electronics_model.CanPort.CanLogicLink":
      if link_port == 'controller':
        return LinkPortDir.SOURCE
      elif link_port == 'transceiver':
        return LinkPortDir.SINK
    elif link_class.target.name == "electronics_model.CanPort.CanDiffLink":
      if link_port == 'nodes':
        return LinkPortDir.BIDIR

    print(f"unknown direction for {link_class} port {link_port}")
    return LinkPortDir.BIDIR

    # raise ValueError(f"unknown direction for {link_class} port {link_port}")

  def _make_link_edges(self, link_obj: LinkLike, port_nodes: Dict[tfu.Path, Any],
                      container_node: Any, parent_port_dirs: Dict[tfu.Path, LinkPortDir]) -> Dict[tfu.Path, LinkPortDir]:
    source_targets: List[tfu.Path] = []
    sink_targets: List[tfu.Path] = []
    bidir_targets: List[tfu.Path] = []

    port_dirs: Dict[tfu.Path, LinkPortDir] = {}

    if isinstance(link_obj, Link):
      for port_name, port_targets in link_obj.ports.items():
        for port_target in port_targets:
          dir = self._link_port_dir(link_obj.link.superclasses[0], port_name)
          if dir == LinkPortDir.SOURCE:
            source_targets.append(port_target)
            port_dirs[port_target] = LinkPortDir.SOURCE
          elif dir == LinkPortDir.SINK:
            sink_targets.append(port_target)
            port_dirs[port_target] = LinkPortDir.SINK
          else:
            bidir_targets.append(port_target)
    elif isinstance(link_obj, Export):
      bidir_targets.append(link_obj.exterior)  # this must get added first to properly set directionality
      bidir_targets.append(link_obj.interior)
    else:
      raise ValueError(f"bad link_obj {link_obj}")

    # resolve exterior port directions first where possible
    bidir_resolved = []
    for bidir_target in bidir_targets:
      if bidir_target in parent_port_dirs:  # if an exterior port, use that direction
        parent_port_dir = parent_port_dirs[bidir_target]
        if parent_port_dir == LinkPortDir.SOURCE:
          sink_targets.append(bidir_target)
          port_dirs[bidir_target] = LinkPortDir.SINK
          bidir_resolved.append(bidir_target)
        elif parent_port_dir == LinkPortDir.SINK:
          source_targets.append(bidir_target)
          port_dirs[bidir_target] = LinkPortDir.SOURCE
          bidir_resolved.append(bidir_target)
        else:
          raise ValueError(f"bad parent_port_dir {parent_port_dir} for {bidir_target}")
    for bidir_target in bidir_resolved:
      bidir_targets.remove(bidir_target)

    # then resolve the rest of the bidir stragglers
    for bidir_target in bidir_targets:
      if not source_targets:  # we assume the first non-source connect is a source
        source_targets.append(bidir_target)
        port_dirs[bidir_target] = LinkPortDir.SOURCE
      else:  # ... and everything else is a sink
        sink_targets.append(bidir_target)
        port_dirs[bidir_target] = LinkPortDir.SINK

    def simple_port(port_path: tfu.Path) -> tfu.Path:
      return tfu.Path(port_path.blocks, port_path.links, (port_path.ports[0], ), ())

    if isinstance(link_obj, Link) and \
        link_obj.link.superclasses[0].target.name == "electronics_model.ElectricalPorts.ElectricalLink" and \
        len(sink_targets) > 3:  # create tunnels for high-fanout power rails
      link_rawname = link_obj.path().links[-1]
      if link_rawname.startswith('_anon'):
        link_name = source_targets[0].ports[0]
      else:
        link_name = link_obj.path().links[-1]

      for i, source_target in enumerate(source_targets):
        # rawname needed in id suffix for disambiguation if bridges not collapsed, since link_name ends up as inner_link
        node = gateway.createNode(container_node, link_name, f"({link_rawname}:sources_{i})")
        edge = gateway.createEdge(container_node, f"{link_obj.path()}_{source_target}",
                                  port_nodes[simple_port(source_target)],
                                  node)
        self.links[edge.getIdentifier()] = link_obj.path()
      for i, sink_target in enumerate(sink_targets):  # TODO make less janky
        node = gateway.createNode(container_node, link_name, f"({link_rawname}:sinks_{i})")
        edge = gateway.createEdge(container_node, f"{link_obj.path()}_{sink_target}",
                                  node,
                                  port_nodes[simple_port(sink_target)])
        self.links[edge.getIdentifier()] = link_obj.path()
    elif sink_targets and source_targets:  # create directed edges
      for source_target in source_targets:
        for sink_target in sink_targets:
          if sink_target.block_component() == source_target.block_component():  # TODO also needed elsewhere?
            print(f"discarding malformed edge from {source_target} -> {sink_target} in {link_obj.path()}")
            continue
          edge = gateway.createEdge(container_node, f"{link_obj.path()}_{source_target}_{sink_target}",
                                    port_nodes[simple_port(source_target)],
                                    port_nodes[simple_port(sink_target)])
          self.links[edge.getIdentifier()] = link_obj.path()
    elif sink_targets:  # create all-to-all bidirectional edge
      print(f"no sources in {link_obj}")
      for bidir_target in sink_targets:
        for bidir_target2 in sink_targets:
          if bidir_target != bidir_target2:
            edge = gateway.createEdge(container_node, f"{link_obj.path()}_{bidir_target}_{bidir_target2}",
                                      port_nodes[simple_port(bidir_target)],
                                      port_nodes[simple_port(bidir_target2)])
            self.links[edge.getIdentifier()] = link_obj.path()
    elif source_targets:  # create all-to-all bidirectional edge
      print(f"no sinks in {link_obj}")
      for bidir_target in source_targets:
        for bidir_target2 in source_targets:
          if bidir_target != bidir_target2:
            edge = gateway.createEdge(container_node, f"{link_obj.path()}_{bidir_target}_{bidir_target2}",
                                      port_nodes[simple_port(bidir_target)],
                                      port_nodes[simple_port(bidir_target2)])
            self.links[edge.getIdentifier()] = link_obj.path()
    else:
      print(f"empty link {link_obj}")

    return port_dirs
