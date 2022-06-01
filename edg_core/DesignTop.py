from typing import TypeVar, Union, List, Tuple, Dict

import edgir
from .Ports import Port
from .ArrayExpr import ArrayExpr
from .ConstraintExpr import ConstraintExpr
from .Exceptions import BlockDefinitionError
from .IdentityDict import IdentityDict
from .Blocks import BlockElaborationState
from .HierarchyBlock import Block
from .MultipackBlock import MultipackBlock, PackedBlockAllocate, PackedBlockPortArray, PackedBlockParamArray
from .Refinements import Refinements, DesignPath


class DesignTop(Block):
  """A top-level design, which may not have ports (including exports), but may define refinements.
  """
  def __init__(self) -> None:
    super().__init__()
    self._packed_blocks = IdentityDict[Union[Block, PackedBlockAllocate], DesignPath]()  # multipack part -> packed block (as path)

  def Port(self, *args, **kwargs):
    raise ValueError("Can't create ports on design top")

  def Export(self, *args, **kwargs):
    raise ValueError("Can't create ports on design top")

  def refinements(self) -> Refinements:
    """Defines top-level refinements.
    Subclasses should define refinements by stacking new refinements on a super().refinements() call."""
    return Refinements()

  def multipack(self):
    """Defines multipack packing rules, by defining multipack devices and providing packing connections.
    Subclasses should define multipack by stacking on top of super().multipack()."""
    pass

  # TODO make this non-overriding? - this needs to call multipack after contents
  def _elaborated_def_to_proto(self) -> edgir.HierarchyBlock:
    assert self._elaboration_state == BlockElaborationState.post_init
    self._elaboration_state = BlockElaborationState.contents
    self.contents()
    self.multipack()
    self._elaboration_state = BlockElaborationState.post_contents
    return self._def_to_proto()

  def _populate_def_proto_block_contents(self, pb: edgir.HierarchyBlock) -> edgir.HierarchyBlock:
    """Add multipack constraints"""
    pb = super()._populate_def_proto_block_contents(pb)

    # Since ConstraintExpr arrays don't have the allocate construct (like connects),
    # we need to aggregate them into a packed array format (instead of generating a constraint for each element)
    # constr name -> (assign dst, assign src elt)
    packed_params: Dict[str, Tuple[edgir.LocalPath, List[edgir.LocalPath]]] = {}

    for multipack_part, packed_path in self._packed_blocks.items():
      if isinstance(multipack_part, Block):
        multipack_block = multipack_part._parent
        multipack_part_block = multipack_part
      elif isinstance(multipack_part, PackedBlockAllocate):
        multipack_block = multipack_part.parent._parent
        assert isinstance(multipack_part.parent._elt_sample, Block)  # may be optional
        multipack_part_block = multipack_part.parent._elt_sample
      else:
        raise TypeError
      assert isinstance(multipack_block, MultipackBlock)
      multipack_name = self._name_of_child(multipack_block)
      multipack_ref_base = edgir.LocalPath()
      multipack_ref_base.steps.add().name = multipack_name
      multipack_ref_map = multipack_block._get_ref_map(multipack_ref_base)

      packing_rule = multipack_block._get_block_packing_rule(multipack_part)
      packed_ref_base = edgir.LocalPath()
      for packed_path_part in packed_path:
        packed_ref_base.steps.add().name = packed_path_part
      packed_ref_map = multipack_part_block._get_ref_map(packed_ref_base)

      if isinstance(multipack_part, Block):
        part_name = multipack_block._name_of_child(multipack_part)
      elif isinstance(multipack_part, PackedBlockAllocate):
        part_name = multipack_block._name_of_child(multipack_part.parent)
        assert multipack_part.suggested_name, "multipack parts must have suggested name, for consistency"
        part_name += f"[{multipack_part.suggested_name}]"
      else:
        raise TypeError

      for exterior_port, packed_port in packing_rule.tunnel_exports.items():
        if isinstance(packed_port, Port):
          packed_port_port = packed_port
        elif isinstance(packed_port, PackedBlockPortArray):
          packed_port_port = packed_port.port
        else:
          raise TypeError
        packed_port_name = multipack_part_block._name_of_child(packed_port_port)
        exported_tunnel = pb.constraints[f"(packed){multipack_name}.{part_name}.{packed_port_name}"].exportedTunnel
        exported_tunnel.internal_block_port.ref.CopyFrom(multipack_ref_map[exterior_port])
        if isinstance(packed_port, PackedBlockPortArray):
          assert isinstance(multipack_part, PackedBlockAllocate)
          assert multipack_part.suggested_name
          exported_tunnel.internal_block_port.ref.steps.add().allocate = multipack_part.suggested_name
        exported_tunnel.exterior_port.ref.CopyFrom(packed_ref_map[packed_port_port])

      for multipack_param, packed_param in packing_rule.tunnel_assigns.items():
        if isinstance(packed_param, ConstraintExpr):
          packed_param_name = multipack_part_block._name_of_child(packed_param)
          assign_tunnel = pb.constraints[f"(packed){multipack_name}.{part_name}.{packed_param_name}"].assignTunnel
          assign_tunnel.dst.CopyFrom(multipack_ref_map[multipack_param])
          assign_tunnel.src.ref.CopyFrom(packed_ref_map[packed_param])
        elif isinstance(packed_param, PackedBlockParamArray):
          multipack_param_name = multipack_block._name_of_child(multipack_param)
          constr_name = f"(packed){multipack_name}.{multipack_param_name}"

          packed_params.setdefault(constr_name, (multipack_ref_map[multipack_param], []))[1].append(
            packed_ref_map[packed_param.param])

        else:
          raise TypeError

    # Generate packed array assigns (see comment near top of function)
    for constr_name, (assign_dst, assign_srcs) in packed_params.items():
      assign_tunnel = pb.constraints[constr_name].assignTunnel
      assign_tunnel.dst.CopyFrom(assign_dst)
      assign_src_vals = assign_tunnel.src.array.vals
      for assign_src in assign_srcs:
        assign_src_vals.add().ref.CopyFrom(assign_src)

    return pb

  PackedBlockType = TypeVar('PackedBlockType', bound=MultipackBlock)
  def PackedBlock(self, tpe: PackedBlockType) -> PackedBlockType:
    """Instantiates a multipack block, that can be used to pack constituent blocks arbitrarily deep in the design."""
    # TODO: additional checks and enforcement beyond what Block provides - eg disallowing .connect operations
    return self.Block(tpe)

  def pack(self, multipack_part: Union[Block, PackedBlockAllocate], path: DesignPath) -> None:
    """Packs a block (arbitrarily deep in the design tree, specified as a path) into a PackedBlock multipack block."""
    if self._elaboration_state not in \
        [BlockElaborationState.init, BlockElaborationState.contents, BlockElaborationState.generate]:
      raise BlockDefinitionError(self, "can only define multipack in init, contents, or generate")
    if isinstance(multipack_part, Block):
      multipack_block = multipack_part._parent
    elif isinstance(multipack_part, PackedBlockAllocate):
      multipack_block = multipack_part.parent._parent
    else:
      raise TypeError
    assert isinstance(multipack_block, MultipackBlock), "block must be a part of a MultipackBlock"
    assert self._blocks.name_of(multipack_block), "containing MultipackBlock must be a PackedBlock"
    self._packed_blocks[multipack_part] = path
