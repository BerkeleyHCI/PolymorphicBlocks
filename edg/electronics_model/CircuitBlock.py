from __future__ import annotations

from typing import Generic, Any, Optional, Mapping, Dict, Union, TYPE_CHECKING, Tuple, Iterable, overload, Set

from deprecated import deprecated
from typing_extensions import TypeVar, override

from .KiCadImportableBlock import KiCadImportableBlock
from ..core import *
from ..core.HdlUserExceptions import EdgTypeError

if TYPE_CHECKING:
    from .PassivePort import HasPassivePort, Passive


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
        self.sch_symbol = self.Parameter(StringExpr())
        self.sch_symbol_default = self.Parameter(StringExpr())

        self.fp_mfr = self.Parameter(StringExpr())
        self.fp_part = self.Parameter(StringExpr())
        self.fp_value = self.Parameter(StringExpr())
        self.fp_refdes = self.Parameter(StringExpr())
        self.fp_refdes_prefix = self.Parameter(StringExpr())

        self.fp_pnp_rot = self.Parameter(FloatExpr())
        self.fp_pnp_offset_x = self.Parameter(FloatExpr())
        self.fp_pnp_offset_y = self.Parameter(FloatExpr())

    def schematic_symbol(
        self,
        lib_id: str,
        pinning: Mapping[str, str],
        *,
        pin_names: Optional[Mapping[str, str]] = None,
    ) -> None:
        """Declare a generated schematic symbol: library pin number -> physical pad number.

        This is export-only metadata; Python remains the connectivity source of truth.
        """
        self._assign_schematic_symbol(self.sch_symbol, lib_id, pinning, pin_names)

    def _default_schematic_symbol(self, lib_id: str, pinning: Mapping[str, str]) -> None:
        """Supply category metadata when the concrete part has no explicit symbol."""
        self._assign_schematic_symbol(self.sch_symbol_default, lib_id, pinning, None)

    def _assign_schematic_symbol(
        self, parameter: StringExpr, lib_id: str, pinning: Mapping[str, str], pin_names: Optional[Mapping[str, str]]
    ) -> None:
        import json

        if (
            not isinstance(lib_id, str)
            or ":" not in lib_id
            or not all(lib_id.split(":", 1))
            or not pinning
            or any(not isinstance(k, str) or not k or not isinstance(v, str) or not v for k, v in pinning.items())
        ):
            raise ValueError("schematic_symbol requires Library:Symbol and string pin numbers")
        metadata: Dict[str, Any] = {"lib_id": lib_id, "pinning": dict(pinning)}
        if pin_names is not None:
            if not set(pin_names).issubset(set(pinning.values())) or any(
                not isinstance(v, str) or not v for v in pin_names.values()
            ):
                raise ValueError("schematic pin names must name mapped physical pads")
            metadata["pin_names"] = dict(pin_names)
        self.assign(parameter, json.dumps(metadata, sort_keys=True))

    def _schematic_symbol_for_footprint(self, pinning: Mapping[str, Any]) -> Optional[Tuple[str, Mapping[str, str]]]:
        """Optional category hook; must map verified physical pads to symbol pins."""
        return None

    @overload
    def footprint(
        self,
        refdes: StringLike,
        footprint: StringLike,
        pinning: Mapping[str, Union[Passive, HasPassivePort]],
        mfr: Optional[StringLike] = None,
        part: Optional[StringLike] = None,
        value: Optional[StringLike] = None,
        datasheet: Optional[StringLike] = None,
        pnp_rot: Optional[float] = None,
        pnp_offset: Optional[tuple[float, float]] = None,
    ) -> None: ...

    @overload
    def footprint(
        self,
        refdes: StringLike,
        footprint: StringLike,
        pinning: Mapping[Union[Iterable[str], str], Union[Passive, HasPassivePort]],
        mfr: Optional[StringLike] = None,
        part: Optional[StringLike] = None,
        value: Optional[StringLike] = None,
        datasheet: Optional[StringLike] = None,
        pnp_rot: Optional[float] = None,
        pnp_offset: Optional[tuple[float, float]] = None,
    ) -> None: ...

    def footprint(
        self,
        refdes: StringLike,
        footprint: StringLike,
        pinning: Union[
            Mapping[str, Union[Passive, HasPassivePort]],
            Mapping[Union[Iterable[str], str], Union[Passive, HasPassivePort]],
        ],
        mfr: Optional[StringLike] = None,
        part: Optional[StringLike] = None,
        value: Optional[StringLike] = None,
        datasheet: Optional[StringLike] = None,
        pnp_rot: Optional[float] = None,
        pnp_offset: Optional[tuple[float, float]] = None,
    ) -> None:
        """Creates a footprint in this circuit block.
        Value is a one-line description of the part, eg 680R, 0.01uF, LPC1549, to be used as an aid during layout or
        assembly.
        pnp_rot defines the rotation offset, in degrees, of the footprint for pick-and-place. This amount is added
        (additional CCW rotation) to the rotation of the footprint. This is defined as the rotation from the footprint
        to get to the rotation on the reel, as consistent with JLC's assembly conventions.
        pnp_offset defines the position offset, in mm, of the footprint for pick-and-place. Offsets are applied before
        rotation and are in Kicad space (-y is up).
        """
        from .PassivePort import HasPassivePort, Passive
        from ..core.Blocks import BlockElaborationState, BlockDefinitionError

        if self._elaboration_state not in (
            BlockElaborationState.init,
            BlockElaborationState.contents,
            BlockElaborationState.generate,
        ):
            raise BlockDefinitionError(
                type(self),
                "can't call Footprint(...) outside __init__, contents or generate",
                "call Footprint(...) inside those functions, and remember to make the super() call",
            )

        self.fp_is_footprint = self.Metadata("")

        pinning_array = []
        assigned_pins: Set[str] = set()
        flat_pinning = {}
        for pin_name, pin_port in pinning.items():
            if isinstance(pin_port, HasPassivePort):
                pin_port = pin_port.net
            if not isinstance(pin_port, (CircuitPort, Passive)):
                raise EdgTypeError(f"Footprint(...) pin", pin_port, Passive)

            if isinstance(pin_name, str):
                pin_tuples: Tuple[str, ...] = (pin_name,)
            else:
                pin_tuples = tuple(iter(pin_name))
            for pin in pin_tuples:
                pinning_array.append(f"{pin}={self._path_name_of(pin_port)}")
                assert pin not in assigned_pins, f"duplicate pin name {pin} in footprint pinning"
                assigned_pins.add(pin)
                flat_pinning[pin] = pin_port
        self.assign(self.fp_pinning, pinning_array)
        schematic = self._schematic_symbol_for_footprint(flat_pinning)
        if schematic is not None:
            self._default_schematic_symbol(*schematic)

        self.assign(self.fp_footprint, footprint)
        self.assign(self.fp_refdes_prefix, refdes)
        if mfr is not None:
            self.assign(self.fp_mfr, mfr)
        else:
            self.assign(self.fp_mfr, "")
        if part is not None:
            self.assign(self.fp_part, part)
        else:
            self.assign(self.fp_part, "")
        if value is not None:
            self.assign(self.fp_value, value)
        else:
            self.assign(self.fp_value, "")
        if datasheet is not None:
            self.assign(self.fp_datasheet, datasheet)
        else:
            self.assign(self.fp_datasheet, "")

        # PNP rotation is left explicitly unassigned if not defined
        if pnp_rot is not None:
            self.assign(self.fp_pnp_rot, pnp_rot)
        if pnp_offset is not None:
            self.assign(self.fp_pnp_offset_x, pnp_offset[0])
            self.assign(self.fp_pnp_offset_y, pnp_offset[1])


@non_library
class WrapperFootprintBlock(FootprintBlock):
    """Block that has a footprint and optional internal contents, but the netlister ignores internal components.
    Useful for, for example, a breakout board where the modelling details are provided by internal chip blocks,
    but needs to show up as only a carrier board footprint.
    EXPERIMENTAL - API SUBJECT TO CHANGE."""

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        super().__init__(*args, **kwargs)
        self.fp_is_wrapper = self.Metadata("A")  # TODO replace with not metadata, eg superclass inspection


AdapterDstType = TypeVar("AdapterDstType", covariant=True, bound=Port, default=Port)


@non_library
class KicadImportablePortAdapter(KiCadImportableBlock, PortAdapter[AdapterDstType], Generic[AdapterDstType]):
    @override
    def symbol_pinning(self, symbol_name: str) -> Dict[str, BasePort]:
        assert symbol_name == "edg_importable:Adapter"
        return {"1": self.src, "2": self.dst}


CircuitLinkType = TypeVar("CircuitLinkType", bound=Link, covariant=True, default=Link)


@deprecated("Use compositional Passive sub-port instead")
class CircuitPort(Port[CircuitLinkType], Generic[CircuitLinkType]):
    """Electrical connection that represents a single port into a single copper net"""

    pass


@non_library
@deprecated("Use compositional passive and connect nets instead of inheriting")
class NetBaseBlock(BaseBlock):
    def net(self) -> None:
        """Defines all ports on this block as copper-connected"""
        self.nets = self.Metadata({"_": "_"})  # TODO should be empty


@abstract_block
@deprecated("Use compositional passive and connect nets instead of inheriting")
class NetBlock(InternalBlock, NetBaseBlock, Block):
    @override
    def contents(self) -> None:
        super().contents()
        self.net()


@abstract_block
@deprecated("Use compositional passive and connect nets instead of inheriting")
class CircuitPortBridge(NetBaseBlock, PortBridge):
    @override
    def contents(self) -> None:
        super().contents()
        self.net()


@abstract_block
@deprecated("Use compositional passive and connect nets instead of inheriting")
class CircuitPortAdapter(KicadImportablePortAdapter[AdapterDstType], NetBaseBlock, Generic[AdapterDstType]):
    @override
    def contents(self) -> None:
        super().contents()
        self.net()


@non_library
@deprecated("Use compositional passive and connect nets instead of inheriting")
class CircuitLink(NetBaseBlock, Link):
    @override
    def contents(self) -> None:
        super().contents()
        self.net()
