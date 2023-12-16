# Simple tool that scans for libraries and dumps the whole thing to a proto file
from typing import TypedDict, Tuple, Optional, Union

from edg_hdl_server.__main__ import LibraryElementIndexer
import edg_core
import edgir
import edg
from edg_core.Builder import builder


class PortJsonDict(TypedDict):
    name: str  # name in parent
    type: str  # type of self; if array refers to the array element type
    is_array: str
    hint_position: str  # left | right | up | down


class ParamJsonDict(TypedDict):
    name: str
    type: str  # int | float | range | string
    defaultValue: Optional[str]  # in Python HDL


class BlockJsonDict(TypedDict):
    name: str  # name in superblock - empty for libraries
    type: str  # type of self
    superClasses: list[str]  # superclasses of self
    ports: list[PortJsonDict]
    argParams: list[ParamJsonDict]


class NetJsonDict(TypedDict):
    name: Optional[str]  # optional net name / label
    ports: list[Tuple[str, str]]  # block name, port name - note, interior connects only


class NetlistJsonDict(TypedDict):
    nets: list[NetJsonDict]



OUTPUT_FILE = "library.edg"

if __name__ == '__main__':
    library = LibraryElementIndexer()

    pb = edgir.Library()

    count = 0
    for cls in library.index_module(edg):
        obj = cls()
        name = cls.__name__
        if isinstance(obj, edg_core.Block):
            print(f"Elaborating block {name}")
            block_proto = builder.elaborate_toplevel(obj)
            pb.root.members[name].hierarchy_block.CopyFrom(block_proto)
        # elif isinstance(obj, edg_core.Link):
        #     print(f"Elaborating link {name}")
        #     link_proto = builder.elaborate_toplevel(obj)
        #     pb.root.members[name].link.CopyFrom(link_proto)
        # elif isinstance(obj, edg_core.Bundle):  # TODO: note Bundle extends Port, so this must come first
        #     print(f"Elaborating bundle {name}")
        #     pb.root.members[name].bundle.CopyFrom(obj._def_to_proto())
        # elif isinstance(obj, edg_core.Port):
        #     print(f"Elaborating port {name}")
        #     pb.root.members[name].port.CopyFrom(obj._def_to_proto())
        else:
            print(f"Unknown category for class {cls}")

        count += 1

    with open(OUTPUT_FILE, 'wb') as file:
        file.write(pb.SerializeToString())

    print(f"Wrote {count} classes to {OUTPUT_FILE}")
