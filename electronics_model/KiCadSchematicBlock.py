import re
from typing import Dict, Type

from kinparse import parse_netlist  # type: ignore

from edg_core import Block
from electronics_abstract_parts import Resistor, Capacitor, Opamp
from electronics_model import KiCadInstantiableBlock, KiCadImportableBlock
from .KiCadSchematicParser import KiCadSchematic


class KiCadSchematicBlock(Block):
    """A schematic block that can instantiate and connect components based on an imported Kicad schematic.
    Symbols on those schematics can either be inline Python that instantiates a Block, or one of a few
    common components (eg, resistors, capacitors) with parsing rules defined here."""
    SYMBOL_MAP: Dict[str, Type[KiCadInstantiableBlock]] = {
        'Device:R': Resistor,
        'Device:C': Capacitor,
        # 'Simulation_SPICE:OPAMP': Opamp,
    }

    def import_kicad(self, filepath: str):
        with open(filepath, "r") as file:
            file_data = file.read()
        sch = KiCadSchematic(file_data)

        blocks: Dict[str, KiCadImportableBlock] = {}

        for symbol in sch.symbols:
            if hasattr(self, symbol.refdes):  # if block already created, use schematic just for connectivity
                assert not symbol.properties['Value'] or symbol.properties['Value'] == '~',\
                    f"{symbol.refdes} has both code block and non-empty value"
                block = getattr(self, symbol.refdes)
                assert isinstance(block, KiCadImportableBlock)
            elif symbol.lib in self.SYMBOL_MAP:
                block = self.Block(self.SYMBOL_MAP[symbol.lib].block_from_symbol(symbol.lib, symbol.properties))
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
