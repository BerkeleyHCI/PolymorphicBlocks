import re
from typing import Callable, Dict, TypeVar, Generic, Tuple

from kinparse import parse_netlist  # type: ignore

from edg_core import Block, Range
from electronics_abstract_parts import Resistor, Capacitor, Opamp
from electronics_model import Port, PartParserUtil
from .KiCadSchematicParser import KiCadSchematic

SymbolParserBlockType = TypeVar('SymbolParserBlockType', bound=Block)
class SymbolParser(Generic[SymbolParserBlockType]):
    def __init__(self, block_gen: Callable[[str, Dict[str, str]], SymbolParserBlockType],
                 pinning: Callable[[SymbolParserBlockType], Dict[str, Port]]):
        # defines how to generate a block given the symbol name and property map
        self.block_gen = block_gen
        # define the pin mapping for a block, from the symbol pin numbers to that block's ports
        self.pinning = pinning


RESISTOR_REGEX = re.compile("^" + f"([\d.]+\s*[{PartParserUtil.SI_PREFIXES}]?)[RΩ]?" +
                            "\s*" + "((?:\+-|\+/-|±)?\s*[\d.]+\s*%?)?" + "$")
RESISTOR_DEFAULT_TOL = 0.05  # TODO this should be unified elsewhere
def parse_resistor(value: str) -> Range:
    match = RESISTOR_REGEX.match(value)
    assert match is not None, f"could not parse resistor from value '{value}'"
    center = PartParserUtil.parse_value(match.group(1), '')
    if match.group(2) is None:
        return Range.from_tolerance(center, RESISTOR_DEFAULT_TOL)
    else:
        return Range.from_tolerance(center, PartParserUtil.parse_tolerance(match.group(2)))


CAPACITOR_REGEX = re.compile("^" + f"([\d.]+\s*[{PartParserUtil.SI_PREFIXES}]?)F?" +
                             "\s*" + "((?:\+-|\+/-|±)?\s*[\d.]+\s*%)?" +
                             "\s*" + f"([\d.]+\s*[{PartParserUtil.SI_PREFIXES}]?\s*V)" + "$")
CAPACITOR_DEFAULT_TOL = 0.20  # TODO this should be unified elsewhere
def parse_capacitor(value: str) -> Tuple[Range, Range]:  # as capacitance, voltage rating
    match = CAPACITOR_REGEX.match(value)
    assert match is not None, f"could not parse capacitor from value '{value}'"
    center = PartParserUtil.parse_value(match.group(1), '')
    voltage = PartParserUtil.parse_value(match.group(3), 'V')
    if match.group(2) is None:
        return (Range.from_tolerance(center, CAPACITOR_DEFAULT_TOL),
                Range(0, voltage))
    else:
        return (Range.from_tolerance(center, PartParserUtil.parse_tolerance(match.group(2))),
                Range(0, voltage))


class KiCadSchematicBlock(Block):
    """A schematic block that can instantiate and connect components based on an imported Kicad schematic.
    Symbols on those schematics can either be inline Python that instantiates a Block, or one of a few
    common components (eg, resistors, capacitors) with parsing rules defined here."""
    SYMBOL_MAP: Dict[str, SymbolParser] = {
        'Device:R': SymbolParser[Resistor](
            lambda symbol, props: Resistor(parse_resistor(props['Value'])),
            lambda block: {'1': block.a, '2': block.b}
        ),
        'Device:C': SymbolParser[Capacitor](
            lambda symbol, props: Capacitor(*parse_capacitor(props['Value'])),
            lambda block: {'1': block.pos, '2': block.neg}
        ),
        'Simulation_SPICE:OPAMP': SymbolParser[Opamp](  # no generic single opamp symbol
            lambda symbol, props: Opamp(),  # note: all ports are typed (VoltageSink, AnalogSink/Source)
            lambda block: {'1': block.inp, '2': block.inn, '3': block.out, '4': block.pwr, '5': block.gnd}
        ),
    }

    def import_kicad(self, filepath: str):
        with open(filepath, "r") as file:
            file_data = file.read()
        sch = KiCadSchematic(file_data)

        pinnings: Dict[str, Dict[str, Port]] = {}  # map from refdes to {pin number -> port}
        blocks: Dict[str, Block] = {}
        for symbol in sch.symbols:
            if hasattr(self, symbol.refdes):  # if block already created, use schematic just for connectivity
                assert not symbol.properties['Value'] or symbol.properties['Value'] == '~',\
                    f"{symbol.refdes} has both code block and non-empty value"
                block = getattr(self, symbol.refdes)
            elif symbol.lib in self.SYMBOL_MAP:
                block = self.Block(self.SYMBOL_MAP[symbol.lib].block_gen(symbol.lib, symbol.properties))
                setattr(self, symbol.refdes, block)
            else:
                raise Exception(f"Unknown symbol {symbol.lib}")

            if symbol.lib in self.SYMBOL_MAP:  # resolve the pinning, independently of the block creation logic
                pinning = self.SYMBOL_MAP[symbol.lib].pinning(block)
            else:
                raise Exception(f"Unknown pinning for {symbol.refdes}")

            assert symbol.refdes not in pinnings
            pinnings[symbol.refdes] = pinning
            blocks[symbol.refdes] = block

        for net in sch.nets:
            net_ports = [pinnings[pin.refdes][pin.pin_number] for pin in net.pins]
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
