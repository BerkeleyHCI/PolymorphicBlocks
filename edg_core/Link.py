from __future__ import annotations

from typing import *

import edgir
from .Array import BaseVector, DerivedVector
from .Blocks import BaseBlock, Connection
from .Core import Refable, non_library
from .Exceptions import *
from .IdentityDict import IdentityDict
from .Ports import BasePort, Port


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
    for cls in self._get_bases_of(BaseBlock):  # type: ignore  # TODO avoid 'only concrete class' error
      assert issubclass(cls, Link)

    pb = self._populate_def_proto_block_base(edgir.Link())
    pb = self._populate_def_proto_block_contents(pb)
    pb = self._populate_def_proto_param_init(pb)
    # specifically ignore the port initializers

    # actually generate the links and connects
    ref_map = self._get_ref_map(edgir.LocalPath())
    self._connects.finalize()
    self._links_order: Dict[str, str] = self.Metadata({})
    for name, connect in self._connects.items_ordered():
      self._links_order[str(len(self._links_order))] = f"{name}"

      connect_elts = connect.make_connection(self, True)
      assert isinstance(connect_elts, Connection.ConnectedLink)

      link_path = edgir.localpath_concat(edgir.LocalPath(), name)
      pb.links[name].lib_elem.target.name = connect_elts.link_type._static_def_name()

      assert not connect_elts.is_link_array
      assert not connect_elts.bridged_connects
      for idx, (self_port, link_port_path) in enumerate(connect_elts.link_connects):
        if isinstance(self_port, BaseVector):
          assert isinstance(self_port, DerivedVector)
          pb.constraints[f"(export){name}_{idx}"].exportedArray.exterior_port.map_extract.container.ref.CopyFrom(ref_map[self_port.base])
          pb.constraints[f"(export){name}_{idx}"].exportedArray.exterior_port.map_extract.path.steps.add().name = \
            self_port.target._name_from(self_port.base._get_elt_sample())
          pb.constraints[f"(export){name}_{idx}"].exportedArray.internal_block_port.ref.CopyFrom(
            edgir.localpath_concat(link_path, link_port_path)
          )
        else:
          pb.constraints[f"(export){name}_{idx}"].exported.exterior_port.ref.CopyFrom(ref_map[self_port])
          pb.constraints[f"(export){name}_{idx}"].exported.internal_block_port.ref.CopyFrom(
            edgir.localpath_concat(link_path, link_port_path)
          )
        self._namespace_order.append(f"(export){name}_{idx}")

    return pb
