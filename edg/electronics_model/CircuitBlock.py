from __future__ import annotations

from typing import *

from .. import edgir
from ..core import *
from ..core import IdentityDict  # TODO: this is ugly
from ..core.ConstraintExpr import Refable
from .KiCadImportableBlock import KiCadImportableBlock


CircuitLinkType = TypeVar('CircuitLinkType', bound=Link, covariant=True)
class CircuitPort(Port[CircuitLinkType], Generic[CircuitLinkType]):
  """Electrical connection that represents a single port into a single copper net"""
  pass


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


@non_library
class FootprintBlock(Block):
  """Block that represents a component that has part(s) and trace(s) on the PCB.
  Provides interfaces that define footprints and copper connections and generates to appropriate metadata.
  """
  # TODO perhaps don't allow part / package initializers since those shouldn't be used
  def __init__(self, *args: Any, **kwargs: Any) -> None:
    super().__init__(*args, **kwargs)
    self.fp_footprint = self.Parameter(StringExpr())
    self.fp_pinning = self.Parameter(ArrayStringExpr())
    self.fp_datasheet = self.Parameter(StringExpr())

    self.fp_mfr = self.Parameter(StringExpr())
    self.fp_part = self.Parameter(StringExpr())
    self.fp_value = self.Parameter(StringExpr())
    self.fp_refdes = self.Parameter(StringExpr())
    self.fp_refdes_prefix = self.Parameter(StringExpr())

  # TODO: allow value to be taken from parameters, ideally w/ string concat from params
  def footprint(self, refdes: StringLike, footprint: StringLike, pinning: Mapping[str, CircuitPort],
                mfr: Optional[StringLike] = None, part: Optional[StringLike] = None, value: Optional[StringLike] = None,
                datasheet: Optional[StringLike] = None) -> None:
    """Creates a footprint in this circuit block.
    Value is a one-line description of the part, eg 680R, 0.01uF, LPC1549, to be used as a aid during layout or
    assembly"""
    from ..core.Blocks import BlockElaborationState, BlockDefinitionError
    from .VoltagePorts import CircuitPort

    if self._elaboration_state not in (BlockElaborationState.init, BlockElaborationState.contents,
                                       BlockElaborationState.generate):
      raise BlockDefinitionError(type(self), "can't call Footprint(...) outside __init__, contents or generate",
                                 "call Footprint(...) inside those functions, and remember to make the super() call")

    self.fp_is_footprint = self.Metadata("")

    pinning_array = []
    for pin_name, pin_port in pinning.items():
      if not isinstance(pin_port, CircuitPort):
        raise TypeError(f"pin port to Footprint(...) must be CircuitPort, got {pin_port} of type {type(pin_port)}")
      pinning_array.append(f'{pin_name}={pin_port._name_from(self)}')
    self.assign(self.fp_pinning, pinning_array)

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


@non_library
class WrapperFootprintBlock(FootprintBlock):
  """Block that has a footprint and optional internal contents, but the netlister ignores internal components.
  Useful for, for example, a breakout board where the modelling details are provided by internal chip blocks,
  but needs to show up as only a carrier board footprint.
  EXPERIMENTAL - API SUBJECT TO CHANGE."""
  def __init__(self, *args: Any, **kwargs: Any) -> None:
    super().__init__(*args, **kwargs)
    self.fp_is_wrapper = self.Metadata("A")  # TODO replace with not metadata, eg superclass inspection


@abstract_block
class NetBlock(InternalBlock, NetBaseBlock, Block):
  def contents(self) -> None:
    super().contents()
    self.net()


@abstract_block
class CircuitPortBridge(NetBaseBlock, PortBridge):
  def contents(self) -> None:
    super().contents()
    self.net()


AdapterDstType = TypeVar('AdapterDstType', bound='CircuitPort')
@abstract_block
class CircuitPortAdapter(KiCadImportableBlock, NetBaseBlock, PortAdapter[AdapterDstType], Generic[AdapterDstType]):
  def symbol_pinning(self, symbol_name: str) -> Dict[str, BasePort]:
    assert symbol_name == 'edg_importable:Adapter'
    return {'1': self.src, '2': self.dst}

  def contents(self) -> None:
    super().contents()
    self.net()


@non_library  # TODO make abstract instead?
class CircuitLink(NetBaseBlock, Link):
  def contents(self) -> None:
    super().contents()
    self.net()
