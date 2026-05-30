from typing import *

from ..electronics_interfaces import *
from .IoController import BaseIoController


class BaseIoControllerWrapped(BaseIoController):
    """Base class for IoController wrapped blocks, particularly footprints that are used
    with an outer WrapperSubboardBlock to implement e.g. a dev board or module around a modeling subcircuit.

    Provides some utility functions to remap pin assignments from the model to the footprint.

    In this class, pin_assigns is treated as the model's pin assigns and internally remapped.
    """

    @staticmethod
    def _remap_pin_assigns_list(
        remapping: Dict[str, str],
        pin_assigns: List[str],
        *,
        invert_remapping: bool = False,
    ) -> Dict[str, str]:
        """Given a remapping dict and a list of pin assigns, returns the mapping as a dict with the remapping applied.
        If invert_remapping is True, the remapping dict is inverted before applying.
        Assigns not present in the remapping dict are passed unchanged, eg for non-pin-assigns like bundle containers.
        """
        if invert_remapping:
            remapping = {v: k for k, v in remapping.items()}

        remapped_assigns = {}
        for assign in pin_assigns:
            name, pindef = assign.split("=")
            pin = pindef.split(",")[0].strip()  # take the first (gpio name) if multiple
            remapped_pin = remapping.get(pin)
            if remapped_pin is not None:
                remapped_assigns[name.strip()] = remapped_pin
            else:
                remapped_assigns[name.strip()] = pindef  # pass unmodified if not remappable, eg bundle containers
        return remapped_assigns

    def _generator_pin_dict(self) -> Dict[str, Port]:
        """Returns a dict of pin name to port for all IO ports, recursing into bundles Ports.
        This includes both the bundle container Port and their (recursive) contents.
        Users of this may want to filter by the port type.

        For Vector-typed IO ports, this generates the subports and must be authoritative.
        This cannot be used with anything else that generates vector sub-ports.
        This must be a GeneratorBlock."""
        assert isinstance(self, GeneratorBlock)

        pin_dict: Dict[str, Port] = {}

        def recurse_port(port: Port, prefix: str = "") -> None:
            assert prefix not in pin_dict, f"duplicate pin name {prefix}"
            pin_dict[prefix] = port

            for subport_name, subport in port._ports.items():
                recurse_port(subport, f"{prefix}.{subport_name}")

        for io_port in self._io_ports:
            if isinstance(io_port, Vector):
                io_port.defined()
                for subport_name in self.get(io_port.requested()):
                    subport = io_port.append_elt(io_port._tpe.empty(), subport_name)
                    recurse_port(subport, subport_name)
            elif isinstance(io_port, Port):
                if self.get(io_port.is_connected()):
                    port_name = io_port._name_from(self)
                    recurse_port(io_port, port_name)
            else:
                raise NotImplementedError(f"unknown port type {io_port}")

        return pin_dict

    def _remap_to_footprint_pinning(
        self, pin_assigns: Dict[str, str], valid_pins: Iterable[str]
    ) -> Dict[str, HasPassivePort]:
        """Given the pin assigns in a dict form as port name -> footprint pin, eg from _remap_pin_assigns_list,
        returns the footprint-compatible form as footprint pin -> port object.

        This simplified pin assignment tool requires all pins to be assigned.
        It does not automatically assign unassigned pins, that is assumed to have happened at a higher level."""
        pinning: Dict[str, HasPassivePort] = {}
        seen_names: Set[str] = set()

        def remap_port_recursive(port: Port, prefix: str = "") -> None:
            """Remaps a port, recursively for bundles"""
            if isinstance(port, HasPassivePort):
                pin = pin_assigns.get(prefix)
                assert pin is not None, f"pin {prefix} not assigned"
                assert pin in valid_pins, f"pin {pin} not in valid pins {valid_pins}"
                pinning[pin] = port

            for subport_name, subport in port._ports.items():
                remap_port_recursive(subport, f"{prefix}.{subport_name}")

        for io_port in self._io_ports:
            if isinstance(io_port, Vector):
                io_port.defined()
                for subport_name in self.get(io_port.requested()):
                    assert subport_name not in seen_names, f"duplicate pin name {subport_name}"
                    seen_names.add(subport_name)
                    subport = io_port.append_elt(io_port._tpe.empty(), subport_name)
                    remap_port_recursive(subport, subport_name)
            elif isinstance(io_port, Port):
                if self.get(io_port.is_connected()):
                    port_name = io_port._name_from(self)
                    assert port_name not in seen_names, f"duplicate pin name {port_name}"
                    seen_names.add(port_name)
                    remap_port_recursive(io_port, port_name)
            else:
                raise NotImplementedError(f"unknown port type {io_port}")

        return pinning

    @staticmethod
    def _remap_assigns_to_value(assigns: Dict[str, str]) -> List[str]:
        """Given a dict of pin assigns from _remap_pinning_assigns, returns a list of assign strings
        for use in self.actual_pin_assigns"""
        return [f"{name}={assign}" for name, assign in assigns.items()]
