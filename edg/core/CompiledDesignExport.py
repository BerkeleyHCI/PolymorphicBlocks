from typing import Optional, Dict, List, Any, Union, Mapping, Literal, override
import re

from pydantic import BaseModel

from .. import edgir
from .ConstraintExpr import RangeExpr
from .Range import Range
from .FnTransformUtil import FnTransformBase
from .TransformUtil import TransformContext, Path

"""A compiled design, as a human-readable Pydantic / JSON-able version of the IR data structure."""

PathType = str


class CompiledParam(BaseModel):
    # this is minimalistic so the output json is more compact
    type: str
    value: Optional[Any]  # solved value, if available


class CompiledPortArray(BaseModel):
    ports: Dict[str, "CompiledPort"]


class CompiledPort(BaseModel):
    path: PathType  # provide the full path to allow searchability
    cls: str  # self class
    # path of connected port, if connected
    # for block ports, this is either the link port or the exported port
    # for link ports, this is the block port
    connected_path: Optional[List[PathType]]
    params: Dict[str, CompiledParam]
    ports: Dict[str, "CompiledPort"]


class CompiledLink(BaseModel):
    path: PathType  # provide the full path to allow searchability
    cls: str  # self class
    params: Dict[str, CompiledParam]
    ports: Dict[str, CompiledPort]
    links: Dict[str, "CompiledLink"]


class CompiledBlock(BaseModel):
    path: PathType  # provide the full path to allow searchability
    cls: str  # self class
    superclasses: List[str]  # all superclasses
    params: Dict[str, CompiledParam]
    ports: Dict[str, Union[CompiledPortArray, CompiledPort]]
    blocks: Dict[str, "CompiledBlock"]  # sub-blocks
    links: Dict[str, CompiledLink]
    # TODO: all constraints?


class CompiledDesignExportTransform(FnTransformBase[CompiledPort, CompiledBlock, CompiledLink]):
    """Transform a design into the CompiledBlock and friends data structure for export to a human-readable format."""

    # these values are excluded since they're very large and not very useful
    _EXCLUDED_PARAM_VALUES = ["matching_parts"]

    @staticmethod
    def _path_to_path(path: Path) -> PathType:
        return ".".join(path.to_tuple())

    @staticmethod
    def _libpath_to_str(libpath: edgir.LibraryPath) -> str:
        return libpath.target.name

    @classmethod
    def _param_to_type(cls, elt: edgir.ValInit) -> str:
        param_type = elt.WhichOneof("val")
        assert param_type is not None and param_type != "set" and param_type != "struct"
        if param_type == "array":
            return f"array({cls._param_to_type(elt.array)})"
        return param_type

    def _param_to_compiled(self, path: Path, elt: edgir.ValInit) -> CompiledParam:
        if path.params[-1] in self._EXCLUDED_PARAM_VALUES:
            value: Optional[Any] = "<excluded>"
        else:
            value = self.design.get_value(path.to_local_path())
            if isinstance(value, Range):  # convert to Pydantic friendly
                # JSON can't encode inf / -inf by standard, so convert to strings
                if value == RangeExpr.EMPTY:
                    value = "∅"
                else:
                    lower: Union[float, str] = value.lower
                    upper: Union[float, str] = value.upper
                    if lower == float("inf"):
                        lower = "inf"
                    elif lower == float("-inf"):
                        lower = "-inf"
                    if upper == float("inf"):
                        upper = "inf"
                    elif upper == float("-inf"):
                        upper = "-inf"
                    value = (lower, upper)
        return CompiledParam(
            type=self._param_to_type(elt),
            value=value,
        )

    @override
    def transform_block(
        self,
        context: TransformContext,
        elt: edgir.HierarchyBlock,
        ports: Mapping[str, CompiledPort],
        blocks: Mapping[str, CompiledBlock],
        links: Mapping[str, CompiledLink],
    ) -> CompiledBlock:
        return CompiledBlock(
            path=self._path_to_path(context.path),
            cls=self._libpath_to_str(elt.self_class),
            superclasses=[self._libpath_to_str(cls) for cls in elt.superclasses]
            + [self._libpath_to_str(cls) for cls in elt.super_superclasses],
            params={
                param_pair.name: self._param_to_compiled(context.path.append_param(param_pair.name), param_pair.value)
                for param_pair in elt.params
            },
            ports=dict(ports),
            blocks=dict(blocks),
            links=dict(links),
        )

    @override
    def transform_port(
        self,
        context: TransformContext,
        elt: Union[edgir.Port, edgir.PortArray],
        ports: Mapping[str, CompiledPort],
    ) -> CompiledPort:
        if isinstance(elt, edgir.Port):
            params = {
                param_pair.name: self._param_to_compiled(context.path.append_param(param_pair.name), param_pair.value)
                for param_pair in elt.params
            }
        else:
            params = {}

        return CompiledPort(
            path=self._path_to_path(context.path),
            cls=self._libpath_to_str(elt.self_class),
            connected_path=None,  # TODO IMPLEMENT ME
            params=params,
            ports=dict(ports),
        )

    @override
    def transform_link(
        self,
        context: TransformContext,
        elt: edgir.Link,
        ports: Mapping[str, CompiledPort],
        links: Mapping[str, CompiledLink],
    ) -> CompiledLink:
        return CompiledLink(
            path=self._path_to_path(context.path),
            cls=self._libpath_to_str(elt.self_class),
            params={
                param_pair.name: self._param_to_compiled(context.path.append_param(param_pair.name), param_pair.value)
                for param_pair in elt.params
            },
            ports=dict(ports),
            links=dict(links),
        )

    @staticmethod
    def postprocess_serialized_json(json_str: str) -> str:
        # post-process the json string to compactify the param dict and range lists
        # compress range lists onto one line
        json_str = re.sub(
            r""""type":\s*"range",(\s*)"value":\s*\[\s*([\S]+),\s*([\S]+)\s*\]""",
            lambda m: f""""type": "range",{m.group(1)}"value": [{m.group(2)}, {m.group(3)}]""",
            json_str,
        )
        json_str = re.sub(
            r"""\{\s*"type":\s*"(\S+)",\s*"value":\s*(.+)\s*\}""",
            lambda m: f"""{{ "type": "{m.group(1)}", "value": {m.group(2)} }}""",
            json_str,
        )
        return json_str
