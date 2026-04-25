from typing import Optional, Dict, List, Any, Union, Mapping, Literal

from pydantic import BaseModel

from edg import edgir
from edg.core.FnTransformUtil import FnTransformBase
from edg.core.TransformUtil import TransformContext, Path

"""A compiled design, as a human-readable Pydantic / JSON-able version of the IR data structure."""


class CompiledParam(BaseModel):
    path: str
    # TODO support array sub-type
    type: Union[
        Literal["floating"], Literal["integer"], Literal["boolean"], Literal["text"], Literal["range"], Literal["array"]
    ]
    expr: Optional[str]  # expression used in assign, if available
    value: Optional[Any]  # solved value, if available


class CompiledPortArray(BaseModel):
    ports: Dict[str, "CompiledPort"]


class CompiledPort(BaseModel):
    path: str
    cls: str  # self class
    # path of connected port, if connected
    # for block ports, this is either the link port or the exported port
    # for link ports, this is the block port
    connected_path: Optional[List[str]]
    params: Dict[str, CompiledParam]
    ports: Dict[str, "CompiledPort"]


class CompiledLink(BaseModel):
    path: str
    cls: str  # self class
    params: Dict[str, CompiledParam]
    ports: Dict[str, CompiledPort]
    links: Dict[str, "CompiledLink"]


class CompiledBlock(BaseModel):
    path: str
    cls: str  # self class
    superclasses: List[str]  # all superclasses
    params: Dict[str, CompiledParam]
    ports: Dict[str, Union[CompiledPortArray, CompiledPort]]
    blocks: Dict[str, "CompiledBlock"]  # sub-blocks
    links: Dict[str, CompiledLink]
    # TODO: all constraints?


class CompiledDesignExportTransform(FnTransformBase[CompiledPort, CompiledBlock, CompiledLink]):
    """Transform a design into the CompiledBlock and friend data structure for export to a human-readable format."""

    @staticmethod
    def _path_to_path(path: Path) -> str:
        return ".".join(path.to_tuple())

    @staticmethod
    def _libpath_to_str(libpath: edgir.LibraryPath) -> str:
        return libpath.target.name

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
                param_pair.name: CompiledParam(
                    path=self._path_to_path(context.path.append_param(param_pair.name)),
                    type=param_pair.value.WhichOneof("val"),
                    expr=None,  # TODO IMPLEMENT ME
                    value=None,  # TODO IMPLEMENT ME
                )
                for param_pair in elt.params
            },
            ports=dict(ports),
            blocks=dict(blocks),
            links=dict(links),
        )

    def transform_port(
        self,
        context: TransformContext,
        elt: Union[edgir.Port, edgir.PortArray],
        ports: Mapping[str, CompiledPort],
    ) -> CompiledPort:
        return CompiledPort(
            path=self._path_to_path(context.path),
            cls=self._libpath_to_str(elt.self_class),
            connected_path=None,  # TODO IMPLEMENT ME
            params={},  # TODO IMPLEMENT ME
            ports=dict(ports),
        )

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
                param_pair.name: CompiledParam(
                    path=self._path_to_path(context.path.append_param(param_pair.name)),
                    type=param_pair.value.WhichOneof("val"),
                    expr=None,  # TODO IMPLEMENT ME
                    value=None,  # TODO IMPLEMENT ME
                )
                for param_pair in elt.params
            },
            ports=dict(ports),
            links=dict(links),
        )
