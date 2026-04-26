from typing import Optional, Dict, List, Any, Union, Mapping, Literal, override
import re

from pydantic import BaseModel, RootModel

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


class CompiledPortArray(RootModel[Dict[str, Union["CompiledPort", "CompiledPortArray"]]]):
    pass


class CompiledPort(BaseModel):
    path: PathType  # provide the full path to allow searchability
    cls: str  # self class
    # path of connected port, if connected
    # for block ports, this is the link, if connected to one
    connected_path: Optional[Union[PathType, List[PathType]]]
    # note, link ports do not have parameters (they inherit parameters from connected ports and are deduplicated here)
    params: Dict[str, CompiledParam]
    ports: Dict[str, Union["CompiledPort", CompiledPortArray]]


class CompiledLink(BaseModel):
    path: PathType  # provide the full path to allow searchability
    cls: str  # self class
    params: Dict[str, CompiledParam]
    ports: Dict[str, Union[CompiledPortArray, CompiledPort]]
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


class CompiledDesignExportTransform(
    FnTransformBase[Union[CompiledPort, CompiledPortArray], CompiledBlock, CompiledLink]
):
    """Transform a design into the CompiledBlock and friends data structure for export to a human-readable format."""

    # these values are excluded since they're very large and not very useful
    _EXCLUDED_PARAM_VALUES = ["matching_parts"]

    @staticmethod
    def _path_to_path(path: Path) -> PathType:
        return ".".join(path.to_tuple())

    @staticmethod
    def _localpath_to_path(localpath: edgir.LocalPath) -> PathType:
        return ".".join(edgir.local_path_to_str_list(localpath))

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

    @classmethod
    def _param_value_to_json(cls, value: Any) -> Any:
        if isinstance(value, Range):  # convert to Pydantic friendly
            # JSON can't encode inf / -inf by standard, so convert to strings
            if value == RangeExpr.EMPTY:
                return "∅"
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
                return (lower, upper)
        elif isinstance(value, list):
            return [cls._param_value_to_json(elt) for elt in value]
        else:
            return value

    def _param_to_compiled(self, path: Path, elt: edgir.ValInit) -> CompiledParam:
        if path.params[-1] in self._EXCLUDED_PARAM_VALUES:
            value: Optional[Any] = "<excluded>"
        else:
            value = self._param_value_to_json(self._design.get_value(path.to_local_path()))

        return CompiledParam(
            type=self._param_to_type(elt),
            value=value,
        )

    @override
    def transform_block(
        self,
        context: TransformContext,
        elt: edgir.HierarchyBlock,
        ports: Mapping[str, Union[CompiledPort, CompiledPortArray]],
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
        ports: Mapping[str, Union[CompiledPort, CompiledPortArray]],
    ) -> Union[CompiledPort, CompiledPortArray]:
        if isinstance(elt, edgir.Port):
            if not context.path.links:
                params = {
                    param_pair.name: self._param_to_compiled(
                        context.path.append_param(param_pair.name), param_pair.value
                    )
                    for param_pair in elt.params
                }
            else:
                params = {}

            if not context.path.links:
                link_path_opt = self._design.get_connected_link_port(context.path.to_local_path())
                if link_path_opt is not None:
                    connected_path: Optional[Union[PathType, List[PathType]]] = self._localpath_to_path(link_path_opt)
                else:
                    connected_path = None
            else:
                block_paths_opt = self._design.get_connected_block_ports(context.path.to_local_path())
                if block_paths_opt is not None:
                    connected_path = [self._localpath_to_path(link_path) for link_path in block_paths_opt]
                else:
                    connected_path = None

            return CompiledPort(
                path=self._path_to_path(context.path),
                cls=self._libpath_to_str(elt.self_class),
                connected_path=connected_path,
                params=params,
                ports=dict(ports),
            )
        elif isinstance(elt, edgir.PortArray):
            return CompiledPortArray(dict(ports))
        else:
            raise ValueError(f"unknown port type {type(elt)}")

    @override
    def transform_link(
        self,
        context: TransformContext,
        elt: Union[edgir.Link, edgir.LinkArray],
        ports: Mapping[str, Union[CompiledPort, CompiledPortArray]],
        links: Mapping[str, CompiledLink],
    ) -> CompiledLink:
        if isinstance(elt, edgir.Link):
            params = {
                param_pair.name: self._param_to_compiled(context.path.append_param(param_pair.name), param_pair.value)
                for param_pair in elt.params
            }
        elif isinstance(elt, edgir.LinkArray):
            params = {}
        else:
            raise ValueError(f"unknown link type {type(elt)}")

        return CompiledLink(
            path=self._path_to_path(context.path),
            cls=self._libpath_to_str(elt.self_class),
            params=params,
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
