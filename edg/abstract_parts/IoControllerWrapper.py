from typing import Any, Dict, Iterable, List, Mapping, Optional, Tuple, Type, Union
from typing_extensions import override

from ..electronics_interfaces import *
from .IoController import BaseIoController


class BaseIoControllerWrapped(BaseIoController):
    """Base class for IoController wrapped blocks, particularly footprints that are used
    with an outer WrapperSubboardBlock to implement e.g. a dev board or module around a modeling subcircuit.

    Provides some utility functions to remap pin assignments from the model to the footprint.

    In this class, pin_assigns is treated as the model's pin assigns and internally remapped.
    """

    @staticmethod
    def _remap_model_pin_assigns(
        remapping: Dict[str, str], pin_assigns: List[str]
    ) -> Dict[str, Tuple[Optional[str], Optional[str]]]:
        """Given a remapping dict and a list of pin assigns, returns the mapping as a dict with the remapping applied.
        The output is (pin name, pin number), with both being optional.

        Assigns not present in the remapping dict are passed unchanged, eg for non-pin-assigns like bundle containers.

        Internal utility.
        """
        remapped_assigns: Dict[str, Tuple[Optional[str], Optional[str]]] = {}
        for assign in pin_assigns:
            name, pindef = assign.split("=")
            name = name.strip()
            split = pindef.split(",")
            split = [s.strip() for s in split]
            if len(split) == 1:  # should be a bundle name, since pins should have two parts
                assert name not in remapping
                remapped_assigns[name] = (split[0], None)
            elif len(split) == 2:
                pinname, pinnum = split[0], split[1]
                assert pinname in remapping
                remapped_assigns[name] = (pinname, remapping[pinname])
            else:
                raise ValueError(f"unable to parse assign {assign}")

        return remapped_assigns

    def _generator_pin_dict(self) -> Dict[str, Port]:
        """Returns a dict of pin name to port for all IO ports, recursing into bundles Ports.
        This includes both the bundle container Port and their (recursive) contents.
        Users of this may want to filter by the port type.

        For Vector-typed IO ports, this generates the subports and must be authoritative.
        This cannot be used with anything else that generates vector sub-ports.
        This must be a GeneratorBlock with requested() declared as generator params.

        Internal utility.
        """
        assert isinstance(self, GeneratorBlock)

        pin_dict: Dict[str, Port] = {}

        def recurse_port(port: Port, prefix: str) -> None:
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
        self, pin_assigns: Dict[str, Tuple[Optional[str], Optional[str]]], pin_dict: Dict[str, Port]
    ) -> Dict[str, HasPassivePort]:
        """Generates pinning that can be passed into a footprint, given the pin assign dict from _remap_pin_assigns_list
        and pin dict from _generator_pin_dict.

        This requires all pins to be assigned.

        Internal utility.
        """
        pinning: Dict[str, HasPassivePort] = {}

        for name, assign in pin_assigns.items():
            assert name in pin_dict
            port = pin_dict[name]
            if not isinstance(port, HasPassivePort):
                continue  # ignore non-leaf ports
            assert assign[1] is not None, f"pin {name} missing pin number assignment"
            pinning[assign[1]] = port

        return pinning

    @staticmethod
    def _remap_assigns_to_value(assigns: Dict[str, Tuple[Optional[str], Optional[str]]]) -> List[str]:
        """Given a dict of pin assigns from _remap_pinning_assigns, returns a list of assign strings
        for use in self.actual_pin_assigns.

        Internal utility.
        """
        pin_assigns: List[str] = []
        for name, assign in assigns.items():
            if assign[0] is not None and assign[1] is not None:
                pin_assigns.append(f"{name}={assign[0]}, {assign[1]}")
            elif assign[0] is not None:
                pin_assigns.append(f"{name}={assign[0]}")
            elif assign[1] is not None:
                pin_assigns.append(f"{name}={assign[1]}")
            else:
                raise ValueError(f"invalid assign for {name}: {assign}")
        return pin_assigns

    def _make_pinning(
        self,
        fixed_pinning: Mapping[Union[Iterable[str], str], Union[Passive, HasPassivePort]],
        remapping: Dict[str, str],
    ) -> Mapping[Union[Iterable[str], str], Union[Passive, HasPassivePort]]:
        """Creates the footprint pinning dict for the wrapped footprint, given the fixed pinning and
        remapping from pin name to this footprint's pin number.
        This generates pinning for all BaseIoController IOs.
        As a side effect, this assigns self.actual_pin_assigns.

        This wraps the above helpers, this should be used in most cases.
        """
        remapped_pin_assigns = self._remap_model_pin_assigns(remapping, self.get(self.pin_assigns))
        pin_dict = self._generator_pin_dict()
        pinning = dict(fixed_pinning)
        pinning.update(self._remap_to_footprint_pinning(remapped_pin_assigns, pin_dict))
        self.assign(self.actual_pin_assigns, self._remap_assigns_to_value(remapped_pin_assigns))
        return pinning


class BaseIoControllerWrapper(BaseIoController):
    """Base class for a block that contains a BaseIoControllerWrapped as the physical footprint
    as well as a non-physical device model.

    This provides utilities to remap pin assignments from the device specification to the model.
    """

    def _export_tap_ios_inner(self, inner: "BaseIoController") -> None:
        """Export-taps all IO ports from some inner BaseIoController.
        This must be a SubboardBlock to support the export_tap connection.
        This must be called in contents() or generate(), after IOs have been defined."""
        from ..core.Blocks import BlockElaborationState

        assert isinstance(self, WrapperSubboardBlock)
        assert self._elaboration_state in (
            BlockElaborationState.contents,
            BlockElaborationState.generate,
        ), "can only run in contents() or generate()"

        inner_ios_by_type = {self._type_of_io(io_port): io_port for io_port in inner._io_ports}
        for self_io in self._io_ports:
            self_io_type = self._type_of_io(self_io)
            assert self_io_type in inner_ios_by_type, f"inner missing IO of type {self_io_type}"
            inner_io = inner_ios_by_type[self_io_type]
            self.export_tap(self_io, inner_io)

    def _generator_pin_type_dict(self) -> Dict[str, Type[Port]]:
        """Returns a dict of pin name to port type for all IO ports, recursing into bundles Ports.
        This includes both the bundle container Port and their (recursive) contents.

        This does not instantiate Vector subports.
        This must be a GeneratorBlock with requested() declared as generator params.

        Internal utility.
        """
        assert isinstance(self, GeneratorBlock)

        pin_type_dict: Dict[str, Type[Port]] = {}

        def recurse_port(port: Port, prefix: str) -> None:
            assert prefix not in pin_type_dict, f"duplicate pin name {prefix}"
            pin_type_dict[prefix] = type(port)

            for subport_name, subport in port._ports.items():
                recurse_port(subport, f"{prefix}.{subport_name}")

        for io_port in self._io_ports:
            if isinstance(io_port, Vector):
                for subport_name in self.get(io_port.requested()):
                    recurse_port(io_port._tpe.empty(), subport_name)
            elif isinstance(io_port, Port):
                if self.get(io_port.is_connected()):
                    port_name = io_port._name_from(self)
                    recurse_port(io_port, port_name)
            else:
                raise NotImplementedError(f"unknown port type {io_port}")

        return pin_type_dict

    def _make_model_pinning(self, remapping: Dict[str, str], device_assigns: List[str]) -> List[str]:
        """Remaps my own assigns (pinned in device-space) to model-space.
        remapping is specified as the forward remapping, from pinname to device pinnum.

        Requires _generator_param_all_ios, so all the IOs names are available.

        In most cases, use _wrap_inner_model_device which provides all the wrapping functionality, though
        this may be useful where other logic needs to happen with parameters.
        """
        inverse_remapping = {v: k for k, v in remapping.items()}

        remapped_assigns: List[str] = []
        pin_types = self._generator_pin_type_dict()

        for assign in device_assigns:
            name, pindef = assign.split("=")
            name = name.strip()
            pindef = pindef.strip()
            assert name in pin_types, f"assign {name} not in IO ports"
            pin_type = pin_types[name]
            if issubclass(pin_type, HasPassivePort):
                if pindef in inverse_remapping:
                    remapped_assigns.append(f"{name}={inverse_remapping[pindef]}")
                elif pindef in remapping:
                    remapped_assigns.append(assign)
                else:
                    raise ValueError(f"assign {assign} has pindef {pindef} not in remapping")
            else:
                remapped_assigns.append(assign)

        return remapped_assigns

    @override
    def _wrap_inner(self, *args: Any, **kwargs: Any) -> None:
        raise NotImplementedError  # use _wrap_inner_model_device instead

    def _wrap_inner_model_device(
        self, model: BaseIoController, device: BaseIoControllerWrapped, remapping: Dict[str, str]
    ) -> None:
        """A version of _wrap_inner, but for the model (non-physical, directly connected) and device (physical,
        export tapped) for a wrapper block.

        Both the model and device should have pin_assigns unassigned, since this will assign them.

        Export IO transforms are not supported. Where needed, the wrapper should instead represent
        the device footprint instead of the application circuit, which should be defined at one level of hierarchy
        higher.

        Requires _generator_param_all_ios, so all the IOs names are available, and pin_assigns to be a generator param.
        """
        self.assign(self.model.pin_assigns, self._make_model_pinning(remapping, self.get(self.pin_assigns)))
        self._export_ios_inner(self.model)
        self.assign(self.io_current_draw, self.model.io_current_draw)

        self.assign(self.device.pin_assigns, self.model.actual_pin_assigns)
        self._export_tap_ios_inner(self.device)
        self.assign(self.actual_pin_assigns, self.device.actual_pin_assigns)
