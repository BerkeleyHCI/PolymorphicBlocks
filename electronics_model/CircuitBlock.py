from __future__ import annotations

from typing import *
from edg_core import *

import edgir
from edg_core import IdentityDict  # TODO: this is ugly
from edg_core.ConstraintExpr import Refable

if TYPE_CHECKING:
  from .VoltagePorts import CircuitPort


class Pinning:
  def __init__(self, pins: Mapping[str, CircuitPort]):
    self.pins = pins


class CircuitNet:
  """Electrical net, a copper connection of "pins", to be used inside Links to denote electrical connectivity."""
  def __init__(self, pins: List[CircuitArrayReduction[CircuitPort]]):
    self.pins = pins


T = TypeVar('T', bound=BasePort)
class CircuitArrayReduction(Generic[T]):
  def __init__(self, steps: List[Vector[Any]], port: T):
    self.port = port
    self.steps = steps  # reduction steps


@non_library
class NetBaseBlock(BaseBlock):
  def net(self) -> None:
    """Defines all ports on this block as copper-connected"""
    self.nets = self.Metadata({'_': '_'})  # TODO should be empty


@abstract_block
class FootprintBlock(Block):
  """Block that represents a component that has part(s) and trace(s) on the PCB.
  Provides interfaces that define footprints and copper connections and generates to appropriate metadata.
  """
  # TODO perhaps don't allow part / package initializers since those shouldn't be used
  def __init__(self) -> None:
    super().__init__()
    self.fp_footprint = self.Parameter(StringExpr())
    self.fp_datasheet = self.Parameter(StringExpr())

    self.fp_mfr = self.Parameter(StringExpr())
    self.fp_part = self.Parameter(StringExpr())
    self.fp_value = self.Parameter(StringExpr())
    self.fp_refdes = self.Parameter(StringExpr())
    self.fp_refdes_prefix = self.Parameter(StringExpr())

  def _metadata_to_proto(self, src: Any, path: List[str],
                         ref_map: IdentityDict[Refable, edgir.LocalPath]) -> edgir.Metadata:
    def refable_to_path_expr(ref: Refable) -> edgir.ValueExpr:
      expr = edgir.ValueExpr()
      expr.ref.CopyFrom(ref_map[ref])
      return expr

    if path == ['pinning']:
      fp_pins = {name: refable_to_path_expr(pin).SerializeToString() for name, pin in src.items()}
      return super()._metadata_to_proto(fp_pins, path, ref_map)
    else:
      return super()._metadata_to_proto(src, path, ref_map)

  # TODO: allow value to be taken from parameters, ideally w/ string concat from params
  def footprint(self, refdes: str, footprint: StringLike, pinning: Mapping[str, CircuitPort],
                mfr: Optional[StringLike] = None, part: Optional[StringLike] = None, value: Optional[StringLike] = None,
                datasheet: Optional[StringLike] = None) -> None:
    """Creates a footprint in this circuit block.
    Value is a one-line description of the part, eg 680R, 0.01uF, LPC1549, to be used as a aid during layout or
    assembly"""
    from edg_core.Blocks import BlockElaborationState, BlockDefinitionError
    from .VoltagePorts import CircuitPort

    if self._elaboration_state not in (BlockElaborationState.init, BlockElaborationState.contents,
                                       BlockElaborationState.generate):
      raise BlockDefinitionError(self, "can't call Footprint(...) outside __init__, contents or generate",
                                 "call Footprint(...) inside those functions, and remember to make the super() call")

    # TODO type-check footprints and pins?
    for pin_name, pin_port in pinning.items():
      if not isinstance(pin_port, CircuitPort):
        raise TypeError(f"pin port to Footprint(...) must be CircuitPort, got {pin_port} of type {type(pin_port)}")

    self.pinning = self.Metadata(pinning)

    self.assign(self.fp_footprint, footprint)
    self.assign(self.fp_refdes_prefix, refdes)
    if mfr is not None:
      self.assign(self.fp_mfr, mfr)
    else:
      self.assign(self.fp_mfr, '')
    if part is not None:
      self.assign(self.fp_part, part)
    else:
      self.assign(self.fp_part, '')
    if value is not None:
      self.assign(self.fp_value, value)
    else:
      self.assign(self.fp_value, '')
    if datasheet is not None:
      self.assign(self.fp_datasheet, datasheet)
    else:
      self.assign(self.fp_datasheet, '')


@abstract_block
class NetBlock(NetBaseBlock, Block):
  def contents(self):
    super().contents()
    self.net()


@abstract_block
class CircuitPortBridge(NetBaseBlock, PortBridge):
  def contents(self):
    super().contents()
    self.net()

  def _get_ref_map(self, prefix: edgir.LocalPath) -> IdentityDict[Refable, edgir.LocalPath]:
    if self.__class__ == CircuitPortBridge:  # TODO: hack to allow this to elaborate as abstract class while being invalid
      return IdentityDict()
    return super()._get_ref_map(prefix)


AdapterDstType = TypeVar('AdapterDstType', bound='CircuitPort')
@abstract_block
class CircuitPortAdapter(NetBaseBlock, PortAdapter[AdapterDstType], Generic[AdapterDstType]):
  def contents(self):
    super().contents()
    self.net()

  def _get_ref_map(self, prefix: edgir.LocalPath) -> IdentityDict[Refable, edgir.LocalPath]:
    if self.__class__ == CircuitPortAdapter:  # TODO: hack to allow this to elaborate as abstract class while being invalid
      return IdentityDict()
    return super()._get_ref_map(prefix)


@non_library  # TODO make abstract instead?
class CircuitLink(NetBaseBlock, Link):
  def contents(self):
    super().contents()
    self.net()
