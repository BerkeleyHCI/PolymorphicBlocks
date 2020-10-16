from __future__ import annotations

from typing import *
from edg_core import *

from edg_core import edgir, IdentityDict  # TODO: this is ugly
from edg_core.ConstraintExpr import Refable

if TYPE_CHECKING:
  from .ElectricalPorts import CircuitPort


class Pinning:
  def __init__(self, pins: Mapping[str, CircuitPort]):
    self.pins = pins


class CircuitNet:
  """Electrical net, a copper connection of ElectricalBase "pins", to be used inside Links to denote electrical
  connectivity."""
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
class CircuitBlock(Block):
  """Block that represents a component that has part(s) and trace(s) on the PCB.
  Provides interfaces that define footprints and copper connections and generates to appropriate metadata.
  """
  # TODO perhaps don't allow part / package initializers since those shouldn't be used
  def __init__(self) -> None:
    super().__init__()
    self.footprint_name = self.Parameter(StringExpr())
    self.datasheet = self.Parameter(StringExpr())

    self.mfr = self.Parameter(StringExpr())
    self.part = self.Parameter(StringExpr())
    self.value = self.Parameter(StringExpr())
    self.refdes = self.Parameter(StringExpr())
    self.refdes_prefix = self.Parameter(StringExpr())

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
  def footprint(self, refdes: str, footprint: str, pinning: Mapping[str, CircuitPort],
                mfr: Optional[StringLike] = None, part: Optional[StringLike] = None, value: Optional[StringLike] = None,
                datasheet: Optional[StringLike] = None) -> None:
    """Creates a footprint in this circuit block.
    Value is a one-line description of the part, eg 680R, 0.01uF, LPC1549, to be used as a aid during layout or
    assembly"""
    from edg_core.Blocks import BlockElaborationState, BlockDefinitionError
    from .ElectricalPorts import CircuitPort

    if self._elaboration_state != BlockElaborationState.contents and \
        self._elaboration_state != BlockElaborationState.generate:
      raise BlockDefinitionError(self, "can't call Footprint(...) outside contents or generate",
                                 "call Footprint(...) inside contents or generate only, and remember to call super().contents() or .generate()")

    # TODO type-check footprints and pins?
    for pin_name, pin_port in pinning.items():
      if not isinstance(pin_port, CircuitPort):
        raise TypeError(f"pin port to Footprint(...) must be CircuitPort, got {pin_port} of type {type(pin_port)}")

    self.pinning = self.Metadata(pinning)

    self.constrain(self.footprint_name == footprint)
    self.constrain(self.refdes_prefix == refdes)
    if mfr is not None:
      self.constrain(self.mfr == mfr)
    else:
      self.constrain(self.mfr == '')
    if part is not None:
      self.constrain(self.part == part)
    else:
      self.constrain(self.part == '')
    if value is not None:
      self.constrain(self.value == value)
    else:
      self.constrain(self.value == '')
    if datasheet is not None:
      self.constrain(self.datasheet == datasheet)
    else:
      self.constrain(self.datasheet == '')


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
