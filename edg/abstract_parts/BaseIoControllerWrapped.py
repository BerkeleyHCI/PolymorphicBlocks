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
        discard_unremappable: bool = False,
    ) -> Dict[str, str]:
        """Given a remapping dict and a list of pin assigns, returns the mapping as a dict with the remapping applied.
        If invert_remapping is True, the remapping dict is inverted before applying.
        If discard_unremappable is True, assigns not present in the remapping dict are discarded.
        Otherwise, they are passed unmodified.
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
            elif not discard_unremappable:
                remapped_assigns[name.strip()] = pindef  # pass unmodified if not remappable, eg bundle containers
            else:
                pass  # discarded
        return remapped_assigns

    def _generator_param_all_ios(self) -> None:
        # declare all IOs as generator params, required for _remap_pinning_assigns
        for io_port in self._io_ports:
            if isinstance(io_port, Vector):
                self.generator_param(io_port.requested())
            elif isinstance(io_port, Port):
                self.generator_param(io_port.is_connected())
            else:
                raise NotImplementedError(f"unknown port type {io_port}")

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
                    port_name = io_port._name_from(self)
                    assert port_name not in seen_names, f"duplicate pin name {port_name}"
                    remap_port_recursive(io_port, port_name)
                    seen_names.add(port_name)
            else:
                raise NotImplementedError(f"unknown port type {io_port}")

        return pinning, actual_pin_assigns

    @staticmethod
    def _remap_assigns_to_value(assigns: Dict[str, str]) -> List[str]:
        """Given a dict of pin assigns from _remap_pinning_assigns, returns a list of assign strings
        for use in self.actual_pin_assigns"""
        return [f"{name}={assign}" for name, assign in assigns.items()]
