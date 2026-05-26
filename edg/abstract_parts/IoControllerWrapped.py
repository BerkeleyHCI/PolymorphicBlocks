from typing import *

from ..electronics_interfaces import *
from .IoController import BaseIoController


class IoControllerWrapped(BaseIoController):
    """Base class for IoController wrapped blocks, particularly footprints that are used
    with an outer WrapperSubboardBlock to implement e.g. a dev board or module around a modeling subcircuit.

    Provides some utility functions to remap pin assignments from the model to the footprint.

    In this class, pin_assigns is treated as the model's pin assigns and internally remapped.
    """

    def _remap_pinning_assigns(
        self, model_pin_assigns: List[str], remapping: Dict[str, str]
    ) -> Tuple[Dict[str, HasPassivePort], Dict[str, str]]:
        """Given the actual pin assignments and a remapping dict, returns the pinning dict for the footprint
        and the updated actual pin assignments.
        Generates concrete ports elements for IO Vectors"""
        pinning: Dict[str, HasPassivePort] = {}
        actual_pin_assigns: Dict[str, str] = {}
        seen_names: Set[str] = set()

        model_pin_assigns_dict: Dict[str, str] = {}
        for assign in model_pin_assigns:
            name, pindef = assign.split("=")
            pins = pindef.split(",")
            model_pin_assigns_dict[name.strip()] = pins[0].strip()  # use the GPIO name

        def remap_port_recursive(port: Port, prefix: str = "") -> None:
            """Remaps a port, recursively for bundles"""
            if isinstance(port, HasPassivePort):
                if prefix not in model_pin_assigns_dict:
                    raise ValueError(f"pin {prefix} not assigned")
                pin = model_pin_assigns_dict[prefix]
                if pin not in remapping:
                    raise ValueError(f"pin {pin} not in remapping")
                remapped_pin = remapping[pin]
                pinning[remapped_pin] = port
                actual_pin_assigns[prefix] = f"{pin}, {remapped_pin}"

            for subport_name, subport in port._ports.items():
                remap_port_recursive(subport, f"{prefix}.{subport_name}")

        for io_port in self._io_ports:
            if isinstance(io_port, Vector):
                io_port.defined()
                for subport_name in self.get(io_port.requested()):
                    assert subport_name not in seen_names, f"duplicate pin name {subport_name}"
                    subport = io_port.append_elt(io_port._tpe.empty(), subport_name)
                    remap_port_recursive(subport, subport_name)
                    seen_names.add(subport_name)
            elif isinstance(io_port, Port):
                if self.get(io_port.is_connected()):
                    raise NotImplementedError("TODO implement me")
            else:
                raise NotImplementedError(f"unknown port type {io_port}")

        return pinning, actual_pin_assigns

    def _remap_assigns_to_value(self, assigns: Dict[str, str]) -> List[str]:
        """Given a dict of pin assigns from _remap_pinning_assigns, returns a list of assign strings
        for use in self.actual_pin_assigns"""
        return [f"{name}={assign}" for name, assign in assigns.items()]
