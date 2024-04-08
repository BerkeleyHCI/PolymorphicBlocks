from edg_core import *
from abc import abstractmethod


class SvgPcbTemplateBlock:
    """EXPERIMENTAL! MAY CHANGE, NOT API-STABLE!

    A Block that can generate a SVG-PCB (https://github.com/leomcelroy/svg-pcb) layout template.
    This defines the per-class methods (including per-class code generation), the actual board-level code composition
    and generation of non-templated footprints exists in the backend."""
    def _svgpcb_init(self) -> None:
        """Initializes this Block for SVGPCB template generation. Called from the backend."""
        raise NotImplementedError

    def _svgpcb_pathname(self) -> str:
        """Infrastructure method, returns the pathname for this Block as a JS-code-friendly string."""
        raise NotImplementedError

    def _svgpcb_get(self, param: ConstraintExpr) -> str:
        """Infrastructure method, returns the value of the ConstraintExpr as a JS literal.
        Ranges are mapped to a two-element list."""
        raise NotImplementedError

    def _svgpcb_fn_name(self) -> str:
        """Infrastructure method (optionally user override-able), returns the SVGPCB function name
        for the template. This must be unique per-Block (so the pathname is encoded by default)."""
        return f"""{self.__class__.__name__}_{self._svgpcb_pathname()}"""

    @abstractmethod
    def _svgpcb_template(self) -> str:
        """IMPLEMENT ME. Returns the SVGPCB layout template code as JS function named _svgpcb_fn_name.
        First argument must be xy (the XY origin of the block, defined from top-level code), but
        can have additional arguments (which must have defaults).

        Footprint IDs should be prefixed with _svgpcb_pathname, using underscores as additional separators.
        Use _svgpcb_get to get parameter values.
        """
        raise NotImplementedError("implement me!")
