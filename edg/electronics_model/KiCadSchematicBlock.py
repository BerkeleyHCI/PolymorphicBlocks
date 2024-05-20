import inspect
import os
from abc import abstractmethod
from typing import Type, Any, Optional, Mapping, Dict, List, Callable, Tuple, TypeVar, cast

from edg_core import Block, GeneratorBlock, BasePort, Port, Vector, init_in_parent, ArrayStringLike, StringLike, \
    non_library, Bundle, InternalBlock
from .CircuitBlock import FootprintBlock
from .VoltagePorts import CircuitPort
from .PassivePort import Passive
from .KiCadImportableBlock import KiCadInstantiableBlock, KiCadImportableBlock
from .KiCadSchematicParser import KiCadSchematic, KiCadPin, KiCadLabel, KiCadGlobalLabel, KiCadHierarchicalLabel, \
    KiCadPowerLabel, KiCadSymbol, KiCadLibSymbol


@non_library
class KiCadBlackboxBase(InternalBlock):
    """Abstract class for black box handlers, which parses a KiCad symbol and creates the corresponding Block."""
    BlackboxSelfType = TypeVar('BlackboxSelfType', bound='KiCadBlackboxBase')

    @classmethod
    @abstractmethod
    def block_from_symbol(cls: Type[BlackboxSelfType], symbol: KiCadSymbol, lib: KiCadLibSymbol) -> \
            Tuple[BlackboxSelfType, Callable[[BlackboxSelfType], Mapping[str, BasePort]]]:
        """Creates a blackbox block from a schematic symbol. Returns the block template and a function that given
        the block, returns mapping from the schematic pin name to the associated port."""
        ...


class KiCadBlackbox(KiCadBlackboxBase, FootprintBlock, GeneratorBlock, InternalBlock):
    """A footprint block that is fully defined (both value fields and structural pins) by its argument parameters
    and has all passive ports.
    """
    @classmethod
    def block_from_symbol(cls, symbol: KiCadSymbol, lib: KiCadLibSymbol) -> \
            Tuple['KiCadBlackbox', Callable[['KiCadBlackbox'], Mapping[str, BasePort]]]:
        pin_numbers = [pin.number for pin in lib.pins]
        refdes_prefix = symbol.properties.get('Refdes Prefix', symbol.refdes.rstrip('0123456789?'))
        block_model = KiCadBlackbox(
            pin_numbers, refdes_prefix, symbol.properties['Footprint'],
            kicad_part=symbol.lib, kicad_value=symbol.properties.get('Value', ''),
            kicad_datasheet=symbol.properties.get('Datasheet', ''))
        def block_pinning(block: KiCadBlackbox) -> Mapping[str, BasePort]:
            return {pin: block.ports.request(pin) for pin in pin_numbers}
        return block_model, block_pinning

    @init_in_parent
    def __init__(self, kicad_pins: ArrayStringLike, kicad_refdes_prefix: StringLike, kicad_footprint: StringLike,
                 kicad_part: StringLike, kicad_value: StringLike, kicad_datasheet: StringLike):
        super().__init__()
        self.ports = self.Port(Vector(Passive()), optional=True)
        self.kicad_refdes_prefix = self.ArgParameter(kicad_refdes_prefix)
        self.kicad_footprint = self.ArgParameter(kicad_footprint)
        self.kicad_part = self.ArgParameter(kicad_part)
        self.kicad_value = self.ArgParameter(kicad_value)
        self.kicad_datasheet = self.ArgParameter(kicad_datasheet)

        self.kicad_pins = self.ArgParameter(kicad_pins)
        self.generator_param(self.kicad_pins)

    def generate(self):
        super().generate()
        mapping = {pin_name: self.ports.append_elt(Passive(), pin_name)
                   for pin_name in self.get(self.kicad_pins)}
        self.ports.defined()
        self.footprint(self.kicad_refdes_prefix, self.kicad_footprint, mapping,
                       part=self.kicad_part, value=self.kicad_value, datasheet=self.kicad_datasheet)


@non_library
class KiCadSchematicBlock(Block):
    """A schematic block that can instantiate and connect components based on an imported Kicad schematic.
    Symbols on those schematics can either be inline Python that instantiates a KiCadImportableBlock
    (that defines a symbol pinning), reference existing KiCadImportableBlock defined in HDL, or one of
    a few KiCadInstantiableBlock (eg, resistors, capacitors) that have special value parsing rules.

    For inline Python symbols, it uses the globals environment (including imports) of the calling context,
    and can have local variables explicitly defined. It does not inherit local variables of the calling context.

    Global net labels must be connected to external ports (by name matching) or nodes (specified by the
    nodes mapping). Nodes can be None, in which case the global label is not connected (but this is
    different from a no-connect, in that the node can be connected elsewhere such as in the HDL).
    Nodes must be mutually exclusive with external ports.

    Net labels are used for internal schematic connectivity and net naming. Net label names are used
    as link names, and must not collide with any existing object member.

    Passive-typed ports in the schematic can be converted to the target port model via the conversions mapping.

    This Block's interface (ports, parameters) must remain defined in HDL, to support static analysis tools."""
    @staticmethod
    def _port_from_pin(pin: KiCadPin, mapping: Mapping[str, BasePort],
                       conversions: Mapping[str, CircuitPort]) -> BasePort:
        """Returns the Port from a symbol's pin, using the provided mapping and applying conversions as needed."""
        from .PassivePort import Passive

        if pin.pin_number in mapping and pin.pin_name in mapping and pin.pin_number != pin.pin_name:
            raise ValueError(f"ambiguous pinning for {pin.refdes}.{pin.pin_number}, "
                             f"mapping defined for both number ${pin.pin_number} and name ${pin.pin_name}")
        elif pin.pin_number in mapping:
            port = mapping[pin.pin_number]
        elif pin.pin_name in mapping:
            port = mapping[pin.pin_name]
        else:
            raise ValueError(f"no pinning for {pin.refdes}.{pin.pin_number}, "
                             f"no mapping defined for either name ${pin.pin_name} or number ${pin.pin_number}")

        if f"{pin.refdes}.{pin.pin_number}" in conversions and f"{pin.refdes}.{pin.pin_name}" in conversions\
                and pin.pin_number != pin.pin_name:
            raise ValueError(f"ambiguous conversion for {pin.refdes}.{pin.pin_number}, "
                             f"mapping defined for both number ${pin.pin_number} and name ${pin.pin_name}")
        elif f"{pin.refdes}.{pin.pin_number}" in conversions:
            conversion: Optional[CircuitPort] = conversions[f"{pin.refdes}.{pin.pin_number}"]
        elif f"{pin.refdes}.{pin.pin_name}" in conversions:
            conversion = conversions[f"{pin.refdes}.{pin.pin_name}"]
        else:
            conversion = None

        if conversion is not None:
            assert isinstance(port, Passive),\
                f"conversion only allowed on Passive ports, got {pin.refdes}.{pin.pin_number}: {port.__class__.__name__}"
            port = port.adapt_to(conversion)

        return port

    def _port_from_path(self, path: str) -> Optional[BasePort]:
        """Returns the corresponding Port given a path string, recursing into bundles as needed"""
        def inner(root: Any, components: List[str]) -> Optional[BasePort]:
            if not components:
                if isinstance(root, BasePort):
                    return root
                else:
                    return None  # invalid type
            elif hasattr(root, components[0]) and isinstance(root, (Bundle, Block)):
                return inner(getattr(root, components[0]), components[1:])
            else:
                return None
        return inner(self, path.split('.'))

    """
    Import the schematic file specified by the filepath.
    locals specifies variables available to any inline HDL.
    nodes specifies connections to the schematic's boundary ports, where they do not match by name to this 
      Block's boundary ports
    conversions specifies port type conversions (akin to .adapt_to) for Passive-typed ports in the schematic.
    These can either be specified by a pin name (eg, 'R1.1'), in which case the pin is individually adapted,
      or a schematic boundary port name (eg, 'PORT_A'), in which case the pins are connected as a Passive group
      and an adapter is created from the group.
    auto_adapt allows automatically adapting Passive-typed ports in the schematic to the corresponding 
      ideal boundary port type.
    This can be used in conjunction with conversions, though conversions take priority. 
    """
    def import_kicad(self, filepath: str, locals: Mapping[str, Any] = {},
                     *, nodes: Mapping[str, Optional[BasePort]] = {}, conversions: Mapping[str, CircuitPort] = {},
                     auto_adapt: bool = False):
        # ideally SYMBOL_MAP would be a class variable, but this causes a import loop with Opamp,
        # so declaring it here causes it to reference Opamp lazily
        from electronics_abstract_parts import Resistor, Capacitor, Opamp
        SYMBOL_MAP: Mapping[str, Type[KiCadInstantiableBlock]] = {
            'Device:R': Resistor,
            'Device:R_Small': Resistor,
            'Device:C': Capacitor,
            'Device:C_Small': Capacitor,
            'Device:C_Polarized': Capacitor,
            'Device:C_Polarized_Small': Capacitor,
            'Simulation_SPICE:OPAMP': Opamp,
            'edg_importable:Opamp': Opamp,
        }

        with open(filepath, "r", encoding='utf-8') as file:
            file_data = file.read()
        sch = KiCadSchematic(file_data)

        blocks_pins: Dict[str, Mapping[str, BasePort]] = {}

        for symbol in sch.symbols:
            if 'Footprint' in symbol.properties and symbol.properties['Footprint']:  # footprints are blackboxed
                handler: Type[KiCadBlackboxBase] = KiCadBlackbox  # default
                if 'edg_blackbox' in symbol.properties:
                    handler_name = symbol.properties['edg_blackbox']
                    container_globals = inspect.stack()[1][0].f_globals
                    assert handler_name in container_globals, \
                        f"edg_blackbox handler {handler_name} must be imported into current global scope"
                    handler = container_globals[handler_name]
                    assert issubclass(handler, KiCadBlackboxBase), \
                        f"edg_blackbox handler {handler_name} must subclass KiCadBlackboxBase"

                block_model, block_pinning_creator = handler.block_from_symbol(
                    symbol, sch.lib_symbols[symbol.lib_ref])
                blackbox_block = self.Block(block_model)
                block_pinning = block_pinning_creator(blackbox_block)
                setattr(self, symbol.refdes, blackbox_block)
            elif hasattr(self, symbol.refdes):  # sub-block defined in the Python Block, schematic only for connections
                assert not symbol.properties['Value'] or symbol.properties['Value'] == '~',\
                    f"{symbol.refdes} has both code block and non-empty value"
                block = getattr(self, symbol.refdes)
                block_pinning = block.symbol_pinning(symbol.lib)
                assert isinstance(block, KiCadImportableBlock), f"{symbol.refdes} not a KiCadImportableBlock"
            elif symbol.properties['Value'].startswith('#'):  # sub-block with inline Python in the value
                inline_code = symbol.properties['Value'][1:]
                # use the caller's globals, since this needs to reflect the caller's imports
                block_model = eval(inline_code, inspect.stack()[1][0].f_globals, locals)
                assert isinstance(block_model, KiCadImportableBlock),\
                    f"block {block_model} created by {inline_code} not KicadImportableBlock"
                block = self.Block(block_model)
                block_pinning = block.symbol_pinning(symbol.lib)
                setattr(self, symbol.refdes, block)
            elif symbol.lib in SYMBOL_MAP:  # sub-block with code to parse the value
                block = self.Block(SYMBOL_MAP[symbol.lib].block_from_symbol(symbol.lib, symbol.properties))
                block_pinning = block.symbol_pinning(symbol.lib)
                setattr(self, symbol.refdes, block)
            else:
                raise Exception(f"Unknown symbol {symbol.lib}")

            assert symbol.refdes not in blocks_pins
            blocks_pins[symbol.refdes] = block_pinning

        for net in sch.nets:
            net_ports = [self._port_from_pin(pin, blocks_pins[pin.refdes], conversions)
                         for pin in net.pins]
            boundary_ports: List[Tuple[BasePort, str]] = []
            net_label_names = set()
            port_label_names = set()
            for net_label in net.labels:
                if isinstance(net_label, (KiCadLabel, KiCadPowerLabel)):  # only these are used for naming the net
                    net_label_names.add(net_label.name)
                elif isinstance(net_label, (KiCadGlobalLabel, KiCadHierarchicalLabel)):  # must connect to port or node
                    port_label_names.add(net_label.name)  # add to set to deduplicate
                else:
                    raise ValueError(f"unknown label type {net_label.__class__}")

            for global_label_name in port_label_names:
                global_label_port = self._port_from_path(global_label_name)
                if global_label_name in nodes:  # nodes if needed
                    assert not hasattr(self, global_label_name), \
                        f"global label {global_label_name} has both node and boundary port"
                    node = nodes[global_label_name]
                    if node is not None:
                        boundary_ports.append((node, global_label_name))
                elif global_label_port is not None:
                    # connect to boundary port, but not links
                    boundary_ports.append((global_label_port, global_label_name))
                else:
                    raise ValueError(f"global label {global_label_name} must connect to boundary port or node")

            connection = self.connect(*net_ports)
            can_adapt = net_ports and all([isinstance(x, Passive) for x in net_ports])
            for (boundary_port, boundary_port_name) in boundary_ports:  # generate adapters as needed, port by port
                if boundary_port_name in conversions:
                    assert can_adapt, "conversion to boundary port only allowed for Passive ports"
                    adapted = cast(Passive, net_ports[0]).adapt_to(conversions[boundary_port_name])
                    self.connect(adapted, boundary_port)
                elif auto_adapt and can_adapt and isinstance(boundary_port, CircuitPort) and \
                        not isinstance(boundary_port, Passive):
                    adapted = cast(Passive, net_ports[0]).adapt_to(boundary_port.__class__())
                    self.connect(adapted, boundary_port)
                else:
                    self.connect(connection, boundary_port)

            if net_label_names:
                assert len(net_label_names) == 1, "multiple net names not supported"
                net_name = net_label_names.pop()
            else:
                net_name = None
            if net_name is not None and net_name not in port_label_names:
                # allow port names to overlap with net names, in which case port name takes priority
                assert not hasattr(self, net_name), f"net name {net_name} already exists in Block"
                setattr(self, net_name, connection)

    @classmethod
    def file_path(cls, *names: str) -> str:
        """Returns the path to a file from the current class's directory."""
        dir_path = os.path.dirname(inspect.getfile(cls))
        return os.path.join(dir_path, *names)
