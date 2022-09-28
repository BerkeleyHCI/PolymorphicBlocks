from kinparse import parse_netlist  # type: ignore
from edg_core import Block
from electronics_abstract_parts import Resistor, Capacitor
from electronics_model import Ohm, Farad


class KiCadSchematicBlock(Block):
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

            link_name = net.name + "_link"

            if link_name == '/':            # User-defined net labels prepend '/' to the label
                link_name = link_name[1:]

            setattr(self, link_name, self.connect(*portlist))
        return

    def make_block_from_mapping(self, part) -> Block:
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
