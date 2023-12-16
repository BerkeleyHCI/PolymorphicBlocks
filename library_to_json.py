# Simple tool that scans for libraries and dumps the whole thing to a proto file
import sys
from typing import TypedDict, Tuple, Optional, Union
import json

from edg_hdl_server.__main__ import LibraryElementIndexer
import edg_core
import edgir
import edg
from edg_core.Builder import builder


def simpleName(target: edgir.ref_pb2.LibraryPath) -> str:
    return target.target.name.split('.')[-1]


class PortJsonDict(TypedDict):
    name: str  # name in parent
    type: str  # type of self; if array refers to the array element type
    is_array: bool
    hint_position: str  # left | right | up | down | '' (empty)

def port_to_dir(name: str, target: edgir.ref_pb2.LibraryPath) -> str:
    simpleTarget = simpleName(target)

    if simpleTarget == 'VoltageSource':
        return 'right'
    elif simpleTarget == 'VoltageSink':
        if name == 'gnd':
            return 'down'
        else:
            return 'up'

    elif simpleTarget == 'DigitalSource':
        return 'right'
    elif simpleTarget == 'DigitalSingleSource':
        return 'right'
    elif simpleTarget == 'DigitalSink':
        return 'left'
    elif simpleTarget == 'DigitalBidir':
        return ''

    elif simpleTarget == 'AnalogSource':
        return 'right'
    elif simpleTarget == 'AnalogSink':
        return 'left'
    elif simpleTarget == 'AnalogBidir':
        return ''

    elif simpleTarget == 'I2cController':
        return 'right'
    elif simpleTarget == 'I2cPullupPort':
        return 'down'
    elif simpleTarget == 'I2cTarget':
        return 'left'

    elif simpleTarget == 'SpiController':
        return 'right'
    elif simpleTarget == 'SpiPeripheral':
        return 'left'

    elif simpleTarget == 'UsbHostPort':
        return 'right'
    elif simpleTarget == 'UsbDevicePort':
        return 'left'
    elif simpleTarget == 'UsbPassivePort':
        return 'left'

    else:
        print(f"unknown direction {simpleTarget}")
        return ''

def pb_to_port(pair: edgir.elem_pb2.NamedPortLike):
    if pair.value.HasField('lib_elem'):
        return PortJsonDict(
            name=pair.name,
            type=simpleName(pair.value.lib_elem),
            is_array=False,
            hint_position=port_to_dir(pair.name, pair.value.lib_elem)
        )
    elif pair.value.HasField('array'):
        return PortJsonDict(
            name=pair.name,
            type=simpleName(pair.value.array.self_class),
            is_array=True,
            hint_position=port_to_dir(pair.name, pair.value.array.self_class)
        )
    else:
        raise ValueError(f"unknown pair value type ${pair.value}")


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
            # convert IR to JsonDict

            ports = [pb_to_port(pair) for pair in block_proto.ports]

            # inspect into the args to get ArgParams
            argParams = []

            block_dict = BlockJsonDict(
                name="",  # empty for libraries
                type=simpleName(block_proto.self_class),
                superClasses=[simpleName(superclass) for superclass in block_proto.superclasses],
                ports=ports,
                argParams=argParams
            )

            text = json.dumps(block_dict)
            print(text)

            sys.exit(0)  # just do one for now
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
        # else:
        #     print(f"Unknown category for class {cls}")

        count += 1

    with open(OUTPUT_FILE, 'wb') as file:
        file.write(pb.SerializeToString())

    print(f"Wrote {count} classes to {OUTPUT_FILE}")
