from typing import List, Optional, TypeVar

from electronics_model import *
from .IoController import BaseIoController


@non_library
class BaseIoControllerExportable(BaseIoController, GeneratorBlock):
    """BaseIoController wrapper (this is a BaseIoController, which wraps another BaseIoController)
    which automatically exports my IOs from the internal IOs in an extensible way (additional connects
    to internal IOs are allowed).
    The export is also customizable, e.g. if additional subcircuits are needed for some connection.
    Also defines a function for adding additional internal pin assignments.
    The internal device (self.ic) must have been created (e.g., in contents()) before this generate() is called."""
    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self.ic: BaseIoController
        self.generator_param(self.pin_assigns)

    def contents(self):  # TODO can this be deduplicated w/ BaseIoControllerPinmapGenerator?
        super().contents()
        for io_port in self._io_ports:  # defined in contents() so subclass __init__ can define additional _io_ports
            if isinstance(io_port, Vector):
                self.generator_param(io_port.requested())
            elif isinstance(io_port, Port):
                self.generator_param(io_port.is_connected())
            else:
                raise NotImplementedError(f"unknown port type {io_port}")

    ExportType = TypeVar('ExportType', bound=Port)
    def _make_export_vector(self, self_io: ExportType, inner_vector: Vector[ExportType], name: str,
                            assign: Optional[str]) -> Optional[str]:
        """Connects my external IO to some inner IO, for a requested port in my array-typed IO.
        This function can be overloaded to handle special cases, e.g. if additional circuitry is required.
        Called within generate, has access to generator params.
        Returns the assignment to pass into the inner Block, can be None to delete the existing record."""
        self.connect(self_io, inner_vector.request(name))
        return assign

    def _make_export_port(self, self_io: ExportType, inner_io: ExportType) -> None:
        """Connects my external IO to some inner IO.
        This function can be overloaded to handle special cases, e.g. if additional circuitry is required.
        Called within generate, has access to generator params."""
        self.connect(self_io, inner_io)

    def _inner_pin_assigns(self, assigns: List[str]) -> List[str]:
        """Integration point to define pin assigns to pass to the inner device.
        Called within generate (has access to generator params), and after modifications from make_export_*."""
        return assigns

    def generate(self):
        super().generate()
        inner_ios_by_type = {self._type_of_io(io_port): io_port for io_port in self.ic._io_ports}

        # mutated in-place during _make_export_*
        assigns: List[Optional[str]] = self.get(self.pin_assigns).copy()
        assign_index_by_name = {assign.split('=')[0]: i for i, assign in enumerate(assigns)}

        for self_io in self._io_ports:
            self_io_type = self._type_of_io(self_io)
            assert self_io_type in inner_ios_by_type, f"inner missing IO of type {self_io_type}"
            inner_io = inner_ios_by_type[self_io_type]

            if isinstance(self_io, Vector):
                self_io.defined()
                assert isinstance(inner_io, Vector)
                for io_requested in self.get(self_io.requested()):
                    self_io_elt = self_io.append_elt(self_io.elt_type().empty(), io_requested)
                    assign_index = assign_index_by_name.get(io_requested)
                    if assign_index is not None:
                        assign = assigns[assign_index]
                    else:
                        assign = None
                    new_assign = self._make_export_vector(self_io_elt, inner_io, io_requested, assign)
                    if assign_index is not None:
                        assigns[assign_index] = new_assign
                    elif new_assign is not None:
                        assigns.append(new_assign)
            else:
                assert isinstance(self_io, Port) and isinstance(inner_io, Port)
                if self.get(self_io.is_connected()):
                    self._make_export_port(self_io, inner_io)

        self.assign(self.io_current_draw, self.ic.io_current_draw)

        filtered_assigns = [assign for assign in assigns if assign is not None]
        self.assign(self.ic.pin_assigns, self._inner_pin_assigns(filtered_assigns))
        self.assign(self.actual_pin_assigns, self.ic.actual_pin_assigns)
