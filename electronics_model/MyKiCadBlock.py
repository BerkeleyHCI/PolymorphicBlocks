from kinparse import parse_netlist

from edg_core import Block
from electronics_abstract_parts import Resistor, Capacitor
from electronics_model import Ohm, Passive


class MyKicadBlock(Block):
    def __init__(self) -> None:
        super().__init__()

        self.PORT_A = self.Port(Passive())
        self.PORT_B = self.Port(Passive())
    def contents(self) -> None:
        super().contents()

        self.import_kicad('C:\\Users\\Nathan Nguyendinh\\Documents\\PCB Files\\EDG-IDE Simple Circuit\\EDG-IDE Simple Circuit.net')

    def import_kicad(self, filepath: str):  # internal implementation

        netlist = parse_netlist(filepath)

        for part in netlist.parts:
            setattr(self, part.ref, self.make_block_from_mapping(part))

        for net in netlist.nets:
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

            self.connect(*portlist)

    def make_block_from_mapping(self, part) -> Block:

        if part.desc == 'Unpolarized capacitor':
            return self.Block(Capacitor())
        if part.desc == 'Resistor':
            if part.value == 'R':
                return self.Block(Resistor())
            else:
                return self.Block(Resistor(resistance=int(part.value)*Ohm(tol=0.05)))
