import re
from typing import Any, Callable, Dict, TypeVar, Generic

from kinparse import parse_netlist  # type: ignore

from edg_core import Block, Range
from electronics_abstract_parts import Resistor, Capacitor
from electronics_model import Ohm, Farad, CircuitPort, PartParserUtil

SymbolParserBlockType = TypeVar('SymbolParserBlockType', bound=Block)
class SymbolParser(Generic[SymbolParserBlockType]):
    def __init__(self, block_gen: Callable[[str, Dict[str, str]], SymbolParserBlockType],
                 pinning: Callable[[SymbolParserBlockType], Dict[str, CircuitPort]]):
        # defines how to generate a block given the symbol name and property map
        self.block_gen = block_gen
        # define the pin mapping for a block, from the symbol pin numbers to that block's ports
        self.pinning = pinning


RESISTOR_REGEX = re.compile("^" + f"([\d.]+\s*[{PartParserUtil.SI_PREFIXES}]?)[RΩ]?" +
                            "\s*" + "((?:\+-|\+/-|±)?\s*[\d.]+\s*%?)?" + "$")
RESISTOR_DEFAULT_TOL = 0.05  # TODO this should be unified elsewhere
def parse_resistor(value: str) -> Range:
    match = RESISTOR_REGEX.match(value)
    assert match is not None, f"could not parse resistance from value '{value}'"
    center = PartParserUtil.parse_value(match.group(1), '')
    if match.group(2) is None:
        return Range.from_tolerance(center, RESISTOR_DEFAULT_TOL)
    else:
        return Range.from_tolerance(center, PartParserUtil.parse_tolerance(match.group(2)))


class KiCadSchematicBlock(Block):
    SYMBOL_MAP = {
        'Device:R': SymbolParser[Resistor](
            lambda symbol, props: Resistor(parse_resistor(props['Value'])),
            lambda block: {'1': block.a, '2': block.b}
        )
    }


    def import_kicad(self, filepath: str):
        netlist = parse_netlist(filepath)

        for part in netlist.parts:
            setattr(self, part.ref, self.make_block_from_mapping(part))

        for net_num, net in enumerate(netlist.nets):
            portlist = []

            for pin in net.pins:
                component = getattr(self, pin.ref)
                if isinstance(component, Resistor):
                    if pin.num == "1":
                        portlist.append(component.a)
                    else:
                        portlist.append(component.b)
                if isinstance(component, Capacitor):
                    if pin.num == "1":
                        portlist.append(component.pos)
                    else:
                        portlist.append(component.neg)

            if hasattr(self, net.name):
                portlist.append(getattr(self, net.name))

            link_name = net.name + "_link"

            if link_name[0] == '/':            # User-defined net labels prepend '/' to the label
                link_name = link_name[1:]

            setattr(self, link_name, self.connect(*portlist))
        return

    def make_block_from_mapping(self, part: Any) -> Block:
        # part is schematic component from kinparse
        if part.desc == 'Unpolarized capacitor':
            if part.value == 'C':
                raise ValueError("Capacitor must have defined capacitance")
            else:
                return self.Block(Capacitor(capacitance=int(part.value)*Farad(tol=0.05)))
        elif part.desc == 'Resistor':
            if part.value == 'R':
                raise ValueError("Resistor must have defined resistance")
            else:
                return self.Block(Resistor(resistance=int(part.value)*Ohm(tol=0.05)))
        return Block()
