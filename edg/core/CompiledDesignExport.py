from typing import Optional, Dict, List, Any, Union

from pydantic import RootModel, BaseModel

"""A compiled design, as a human-readable Pydantic / JSON-able version of the IR data structure."""


class CompiledParam(BaseModel):
    path: List[str]
    type: str
    expr: Optional[str]  # expression used in assign, if available
    value: Optional[Any]  # solved value, if available


class CompiledPortArray(BaseModel):
    ports: Dict[str, "CompiledPort"]


class CompiledPort(BaseModel):
    path: List[str]
    cls: str  # self class
    # path of connected port, if connected
    # for block ports, this is either the link port or the exported port
    # for link ports, this is the block port
    connected_path: Optional[List[str]]
    params: Dict[str, CompiledParam]
    ports: Dict[str, "CompiledPort"]


class CompiledLink(BaseModel):
    path: List[str]
    cls: str  # self class
    params: Dict[str, CompiledParam]
    ports: Dict[str, CompiledPort]
    links: Dict[str, "CompiledLink"]


class CompiledBlock(BaseModel):
    path: List[str]
    cls: str  # self class
    superclasses: List[str]  # all superclasses
    params: Dict[str, CompiledParam]
    ports: Dict[str, Union[CompiledPortArray, CompiledPort]]
    blocks: Dict[str, "CompiledBlock"]  # sub-blocks
    links: Dict[str, CompiledLink]
    # TODO: all constraints?
