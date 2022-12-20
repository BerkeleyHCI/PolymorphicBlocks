import inspect
import os
from typing import Dict, Type, Any

from edg_core import Block, Port
from .KiCadImportableBlock import KiCadInstantiableBlock, KiCadImportableBlock
from .KiCadSchematicParser import KiCadSchematic


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
    via the conversions mapping."""
    def import_kicad(self, filepath: str, locals: Dict[str, Any] = {},
                     *, nodes: Dict[str, Port] = {}, conversions: Dict[str, Port] = {}):
        # ideally SYMBOL_MAP would be a class variable, but this causes a import loop with Opamp,
        # so declaring it here causes it to reference Opamp lazily
        from electronics_abstract_parts import Resistor, Capacitor, Opamp
        SYMBOL_MAP: Dict[str, Type[KiCadInstantiableBlock]] = {
            'Device:R': Resistor,
            'Device:C': Capacitor,
            'Simulation_SPICE:OPAMP': Opamp,
        }

        with open(filepath, "r") as file:
            file_data = file.read()
        sch = KiCadSchematic(file_data)

        blocks: Dict[str, KiCadImportableBlock] = {}

        for symbol in sch.symbols:
            if hasattr(self, symbol.refdes):  # sub-block defined in the Python Block, schematic only for connections
                assert not symbol.properties['Value'] or symbol.properties['Value'] == '~',\
                    f"{symbol.refdes} has both code block and non-empty value"
                block = getattr(self, symbol.refdes)
                assert isinstance(block, KiCadImportableBlock)
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

            assert symbol.refdes not in blocks
            blocks[symbol.refdes] = block

        for net in sch.nets:
            net_ports = [blocks[pin.refdes].symbol_pinning(pin.symbol.lib)[pin.pin_number] for pin in net.pins]
            if net.labels:
                assert len(net.labels) == 1, "multiple net names not supported"
                net_name = net.labels[0].name
            else:
                net_name = None

            if net_name is not None and hasattr(self, net_name):  # append to existing port if needed
                net_ports.insert(0, getattr(self, net_name))
            connection = self.connect(*net_ports)

            if net_name is not None and not hasattr(self, net_name):
                setattr(self, net_name, connection)

    @classmethod
    def file_path(cls, *names: str) -> str:
        """Returns the path to a file from the current class's directory."""
        dir_path = os.path.dirname(inspect.getfile(cls))
        return os.path.join(dir_path, *names)
