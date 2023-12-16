# Simple tool that scans for libraries and dumps the whole thing to a proto file
import sys
from typing import TypedDict, Tuple, Optional
import json
import inspect

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

def port_to_dir(name: str, target: edgir.ref_pb2.LibraryPath) -> Optional[str]:
    simpleTarget = simpleName(target)

    if simpleTarget == 'Passive':
        return None

    elif simpleTarget == 'VoltageSource':
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
        return None

    elif simpleTarget == 'AnalogSource':
        return 'right'
    elif simpleTarget == 'AnalogSink':
        return 'left'
    elif simpleTarget == 'AnalogBidir':
        return None

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
        return None

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
    type: str  # int | float | bool | range | string | array
    default_value: Optional[str]  # in Python HDL


class BlockJsonDict(TypedDict):
    name: str  # name in superblock - empty for libraries
    type: str  # type of self
    superClasses: list[str]  # superclasses of self
    ports: list[PortJsonDict]
    argParams: list[ParamJsonDict]
    is_abstract: bool


class NetJsonDict(TypedDict):
    name: Optional[str]  # optional net name / label
    ports: list[Tuple[str, str]]  # block name, port name - note, interior connects only


class NetlistJsonDict(TypedDict):
    nets: list[NetJsonDict]


OUTPUT_FILE = "library.json"

if __name__ == '__main__':
    library = LibraryElementIndexer()

    pb = edgir.Library()

    all_blocks = []

    count = 0
    for cls in library.index_module(edg):
        # from edg import IndicatorLed
        # cls = IndicatorLed

        obj = cls()
        name = cls.__name__
        if isinstance(obj, edg_core.Block):
            print(f"Elaborating block {name}")
            block_proto = builder.elaborate_toplevel(obj)
            # convert IR to JsonDict

            ports = [pb_to_port(pair) for pair in block_proto.ports]

            # inspect into the args to get ArgParams
            argParams = []
            sig = inspect.signature(cls.__init__)
            for param_name, param in list(sig.parameters.items())[1:]:  # drop 'self'
                # TODO NEED TO RECURSE FOR *ARGS / **KWARGS
                if param.kind in [inspect.Parameter.VAR_POSITIONAL, inspect.Parameter.VAR_KEYWORD,
                                  inspect.Parameter.POSITIONAL_OR_KEYWORD, inspect.Parameter.POSITIONAL_ONLY,
                                  inspect.Parameter.KEYWORD_ONLY]:
                    param_pb = edgir.pair_get_opt(block_proto.params, param_name)
                    if param_pb is not None:
                        if param.default is inspect.Parameter.empty:
                            default_value = None
                        elif isinstance(param.default, (int, float, str, bool)):
                            default_value = param.default
                        elif isinstance(param.default, tuple) and len(param.default) == 2 and \
                                isinstance(param.default[0], (int, float)) and isinstance(param.default[1], (int, float)):
                            default_value = param.default
                        elif isinstance(param.default, edg_core.Range):
                            range = param.default
                            default_value = (range.lower, range.upper)
                        elif isinstance(param.default, edg_core.RangeExpr):
                            if isinstance(param.default.binding, edg_core.ConstraintExpr.RangeLiteralBinding):
                                range = param.default.binding.value
                                default_value = (range.lower, range.upper)
                            else:
                                print(f"{name}.{param_name}: bad binding {param.default.binding}")
                        elif isinstance(param.default, edg_core.FloatExpr):
                            if isinstance(param.default.binding, edg_core.ConstraintExpr.FloatLiteralBinding):
                                default_value = param.default.binding.value
                            else:
                                print(f"{name}.{param_name}: bad binding {param.default.binding}")
                        elif isinstance(param.default, edg_core.BoolExpr):
                            if isinstance(param.default.binding, edg_core.ConstraintExpr.BoolLiteralBinding):
                                default_value = param.default.binding.value
                            else:
                                print(f"{name}.{param_name}: bad binding {param.default.binding}")
                        elif isinstance(param.default, edg_core.StringExpr):
                            if isinstance(param.default.binding, edg_core.ConstraintExpr.StringLiteralBinding):
                                default_value = param.default.binding.value
                            else:
                                print(f"{name}.{param_name}: bad binding {param.default.binding}")
                        else:
                            print(f"{name}.{param_name}: failed to parse default {param.default}")
                            default_value = None

                        if param_pb.HasField('floating'):
                            param_type = 'float'
                        elif param_pb.HasField('integer'):
                            param_type = 'int'
                        elif param_pb.HasField('boolean'):
                            param_type = 'bool'
                        elif param_pb.HasField('text'):
                            param_type = 'str'
                        elif param_pb.HasField('range'):
                            param_type = 'range'
                        elif param_pb.HasField('array'):
                            param_type = 'array'
                        else:
                            raise ValueError(f"{name}.{param_name} unknown param type {param_pb}")

                        argParams.append(ParamJsonDict(
                            name=param_name,
                            type=param_type,
                            defaultValue=default_value
                        ))
                    else:
                        print(f"missing param {param_name} in {name}")

            block_dict = BlockJsonDict(
                name="",  # empty for libraries
                type=simpleName(block_proto.self_class),
                superClasses=[simpleName(superclass) for superclass in block_proto.superclasses],
                ports=ports,
                argParams=argParams,
                is_abstract=block_proto.is_abstract
            )

            all_blocks.append(block_dict)
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

    print(f"Writing {count} classes to {OUTPUT_FILE}")

    with open(OUTPUT_FILE, 'w') as file:
        file.write(json.dumps(all_blocks, indent=2))
