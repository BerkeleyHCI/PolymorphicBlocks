from __future__ import annotations

from typing import *

from .. import edgir
from .Array import BaseVector, DerivedVector
from .Blocks import BaseBlock, Connection
from .Core import Refable, non_library
from .HdlUserExceptions import UnconnectableError
from .IdentityDict import IdentityDict
from .Ports import Port


@non_library
class Link(BaseBlock[edgir.Link]):
  def __init__(self) -> None:
    super().__init__()
    self.parent: Optional[Port] = None

  # Returns the ref_map, but with a trailing ALLOCATE for BaseVector ports
  def _get_ref_map_allocate(self, prefix: edgir.LocalPath) -> IdentityDict[Refable, edgir.LocalPath]:
    def map_port_allocate(ref: Refable, path: edgir.LocalPath) -> edgir.LocalPath:
      if isinstance(ref, BaseVector):
        new_path = edgir.LocalPath()
        new_path.CopyFrom(path)
        new_path.steps.append(edgir.LocalStep(allocate=''))
        return new_path
      else:
        return path

    return IdentityDict([(port, map_port_allocate(port, path))
                         for port, path in self._get_ref_map(prefix).items()])

  def _def_to_proto(self) -> edgir.Link:
    pb = self._populate_def_proto_block_base(edgir.Link())
    pb = self._populate_def_proto_param_init(pb)
    pb = self._populate_def_proto_block_contents(pb)
    pb = self._populate_def_proto_description(pb)
    # specifically ignore the port initializers

    # actually generate the links and connects
    ref_map = self._get_ref_map(edgir.LocalPath())
    self._connects.finalize()
    delegated_connects = self._all_delegated_connects()
    for name, connect in self._connects.items_ordered():
      if connect in delegated_connects:
        continue
      connect_names_opt = [self._connects.name_of(c) for c in self._all_connects_of(connect)]
      connect_names = [c for c in connect_names_opt if c is not None and not c.startswith('anon_')]
      if len(connect_names) > 1:
        raise UnconnectableError(f"Multiple names {connect_names} for connect")
      elif len(connect_names) == 1:
        name = connect_names[0]

      connect_elts = connect.make_connection()
      assert isinstance(connect_elts, Connection.ConnectedLink)

      link_path = edgir.localpath_concat(edgir.LocalPath(), name)
      edgir.add_pair(pb.links, name).lib_elem.target.name = connect_elts.link_type._static_def_name()

      assert not connect_elts.is_link_array
      assert not connect_elts.bridged_connects
      for idx, (self_port, link_port_path) in enumerate(connect_elts.link_connects):
        constraint_pb = edgir.add_pair(pb.constraints, f"(export){name}_{idx}")
        if isinstance(self_port, BaseVector):
          assert isinstance(self_port, DerivedVector)
          constraint_pb.exportedArray.exterior_port.map_extract.container.ref.CopyFrom(ref_map[self_port.base])
          constraint_pb.exportedArray.exterior_port.map_extract.path.steps.add().name = \
            self_port.target._name_from(self_port.base._get_elt_sample())
          constraint_pb.exportedArray.internal_block_port.ref.CopyFrom(
            edgir.localpath_concat(link_path, link_port_path)
          )
        else:
          constraint_pb.exported.exterior_port.ref.CopyFrom(ref_map[self_port])
          constraint_pb.exported.internal_block_port.ref.CopyFrom(
            edgir.localpath_concat(link_path, link_port_path)
          )

    return pb
