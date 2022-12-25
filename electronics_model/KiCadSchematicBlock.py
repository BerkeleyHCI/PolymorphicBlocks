import inspect
import os
from typing import Type, Any, Optional, Mapping, Dict

from edg_core import Block, BasePort
from .VoltagePorts import CircuitPort
from .KiCadImportableBlock import KiCadInstantiableBlock, KiCadImportableBlock
from .KiCadSchematicParser import KiCadSchematic, KiCadPin, KiCadLabel, KiCadGlobalLabel


class KiCadSchematicBlock(Block):
    """A schematic block that can instantiate and connect components based on an imported Kicad schematic.
    Symbols on those schematics can either be inline Python that instantiates a KiCadImportableBlock
    (that defines a symbol pinning), reference existing KiCadImportableBlock defined in HDL, or one of
    a few KiCadInstantiableBlock (eg, resistors, capacitors) that have special value parsing rules.

    For inline Python symbols, it uses the globals environment (including imports) of the calling context,
    and can have local variables explicitly defined. It does not inherit local variables of the calling context.

    Global and local net labels are connected to external ports by name matching, or optionally
    to internal nodes specified via a nodes mapping.

    Passive-typed ports on instantiated components can be converted to the target port model
    via the conversions mapping.

    This Block's interface (ports, parameters) must remain defined in HDL, to support static analysis tools."""
    @staticmethod
    def _port_from_pin(pin: KiCadPin, mapping: Mapping[str, BasePort],
                       conversions: Mapping[str, CircuitPort]) -> BasePort:
        """Returns the Port from a symbol's pin, using the provided mapping and applying conversions as needed."""
        from .PassivePort import Passive

        if pin.pin_number in mapping and pin.pin_name in mapping:
            raise ValueError(f"ambiguous pinning for {pin.refdes}.{pin.pin_number}, "
                             f"mapping defined for both number ${pin.pin_number} and name ${pin.pin_name}")
        elif pin.pin_number in mapping:
            port = mapping[pin.pin_number]
        elif pin.pin_name in mapping:
            port = mapping[pin.pin_name]
        else:
            raise ValueError(f"no pinning for {pin.refdes}.{pin.pin_number}, "
                             f"no mapping defined for either name ${pin.pin_name} or number ${pin.pin_number}")

        if f"{pin.refdes}.{pin.pin_number}" in conversions and f"{pin.refdes}.{pin.pin_name}" in conversions:
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

    def import_kicad(self, filepath: str, locals: Mapping[str, Any] = {},
                     *, nodes: Mapping[str, BasePort] = {}, conversions: Mapping[str, CircuitPort] = {}):
        # ideally SYMBOL_MAP would be a class variable, but this causes a import loop with Opamp,
        # so declaring it here causes it to reference Opamp lazily
        from electronics_abstract_parts import Resistor, Capacitor, Opamp
        SYMBOL_MAP: Mapping[str, Type[KiCadInstantiableBlock]] = {
            'Device:R': Resistor,
            'Device:C': Capacitor,
            'Device:C_Polarized': Capacitor,
            'Simulation_SPICE:OPAMP': Opamp,
            'edg_importable:Opamp': Opamp,
        }

        with open(filepath, "r") as file:
            file_data = file.read()
        sch = KiCadSchematic(file_data)

        blocks_pins: Dict[str, Mapping[str, BasePort]] = {}

        for symbol in sch.symbols:
            if hasattr(self, symbol.refdes):  # sub-block defined in the Python Block, schematic only for connections
                assert not symbol.properties['Value'] or symbol.properties['Value'] == '~',\
                    f"{symbol.refdes} has both code block and non-empty value"
                block = getattr(self, symbol.refdes)
                assert isinstance(block, KiCadImportableBlock), f"{symbol.refdes} not a KiCadImportableBlock"
            elif symbol.properties['Value'].startswith('#'):  # sub-block with inline Python in the value
                inline_code = symbol.properties['Value'][1:]
                # use the caller's globals, since this needs to reflect the caller's imports
                block_model = eval(inline_code, inspect.stack()[1][0].f_globals, locals)
                assert isinstance(block_model, KiCadImportableBlock),\
                    f"block {block_model} created by {inline_code} not KicadImportableBlock"
                block = self.Block(block_model)
                setattr(self, symbol.refdes, block)
            elif symbol.lib in SYMBOL_MAP:  # sub-block with code to parse the value
                block = self.Block(SYMBOL_MAP[symbol.lib].block_from_symbol(symbol.lib, symbol.properties))
                setattr(self, symbol.refdes, block)
            else:
                raise Exception(f"Unknown symbol {symbol.lib}")

            assert symbol.refdes not in blocks_pins
            blocks_pins[symbol.refdes] = block.symbol_pinning(symbol.lib)

        for net in sch.nets:
            net_ports = [self._port_from_pin(pin, blocks_pins[pin.refdes], conversions)
                         for pin in net.pins]
            net_label_names = set()
            for net_label in net.labels:
                if isinstance(net_label, KiCadLabel):  # only these are used for naming the net
                    net_label_names.add(net_label.name)
                elif isinstance(net_label, KiCadGlobalLabel):  # global labels must be connected to ports or nodes
                    if net_label.name in nodes:  # add nodes if needed
                        net_ports.insert(0, nodes[net_label.name])
                    if hasattr(self, net_label.name) and isinstance(getattr(self, net_label.name), BasePort):
                        # connect to boundary port, but not links
                        net_ports.insert(0, getattr(self, net_label.name))
                    assert net_label.name in nodes or hasattr(self, net_label.name),\
                        f"global label {net_label.name} must connect to boundary port or node"
                else:
                    raise ValueError(f"unknown label type {net_label.__class__}")

            connection = self.connect(*net_ports)

            if net_label_names:
                assert len(net_label_names) == 1, "multiple net names not supported"
                net_name = net_label_names.pop()
            else:
                net_name = None
            if net_name is not None:
                assert not hasattr(self, net_name), f"net name {net_name} already exists in Block"
                setattr(self, net_name, connection)

    @classmethod
    def file_path(cls, *names: str) -> str:
        """Returns the path to a file from the current class's directory."""
        dir_path = os.path.dirname(inspect.getfile(cls))
        return os.path.join(dir_path, *names)
