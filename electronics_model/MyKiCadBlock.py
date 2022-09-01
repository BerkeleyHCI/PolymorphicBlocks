from edg_core import Block, abstract_block, init_in_parent, RangeLike, Input, Output
from kinparse import parse_netlist

from electronics_abstract_parts import UnpolarizedCapacitor, Resistor
from electronics_model import VoltageSink, Power, VoltageSource, Common, Ground

class MyKicadBlock(Block):
    def __init__(self) -> None:
        super().__init__()

    def contents(self) -> None:
        super().contents()

        # self.my_port = self.Port(...)
        self.import_kicad('C:\\Users\\Nathan Nguyendinh\\Documents\\PCB Files\\EDG-IDE Simple Circuit\\EDG-IDE Simple Circuit.net')

        # netlist = parse_netlist('C:\\Users\\Nathan Nguyendinh\\Documents\\PCB Files\\EDG-IDE Simple Circuit\\EDG-IDE Simple Circuit.net')
        # print(netlist.parts[0].desc)
        #
        # for part in netlist.parts:
        #     if part.desc == 'Unpolarized capacitor':
        #         setattr(self, part.ref, self.Block(UnpolarizedCapacitor()))
        #     if part.desc == 'Resistor':
        #         setattr(self, part.ref, self.Block(Resistor()))
        #
        # for net in netlist.nets:
        #     portList = []
        #     for pin in net.pins:
        #         component = getattr(self, pin.ref)
        #         if pin.num == "1":
        #             portList.append(component.a)
        #         else:
        #             portList.append(component.b)
        #         print("add to port list " + pin.ref + " pin " + pin.num)
        #     self.connect(*portList)

        # self.connect(self.R1.a, self.R2.a)
        # self.connect(getattr(self, netlist.nets[1].pins[0].ref).b, getattr(self, netlist.nets[1].pins[1].ref).b)
        # portList = [getattr(self, netlist.nets[1].pins[0].ref).b, getattr(self, netlist.nets[1].pins[1].ref).b]
        # self.connect(*portList)

        # for each net:
        #     Define all the ports and put into list
        #     Connect all ports with splat var args connect line of code

    def import_kicad(self, filepath: str):  # internal implementation

        netlist = parse_netlist(filepath)
        print(netlist.parts[0].desc)

        for part in netlist.parts:
            if part.desc == 'Unpolarized capacitor':
                setattr(self, part.ref, self.Block(UnpolarizedCapacitor()))
            if part.desc == 'Resistor':
                setattr(self, part.ref, self.Block(Resistor()))

        for net in netlist.nets:
            portList = []
            for pin in net.pins:
                component = getattr(self, pin.ref)
                if pin.num == "1":
                    portList.append(component.a)
                else:
                    portList.append(component.b)
                print("add to port list " + pin.ref + " pin " + pin.num)
            self.connect(*portList)



    # def import_kicad(self, filename: str):  # internal implementation
    #     # read the netlist, import into some convenient format
    #
    #     netlist = parse_netlist(filename)
    #
    #     # if netlist.parts[0].name == 'Unpolarized Capacitor':
    #     #     self.cap = self.Block(UnpolarizedCapacitor)
    #     #
    #     print(netlist.parts[0].name)
    #     for block_name, block in netlist.components:
    #         setattr(self, block_name, self.Block(make_block_from_mapping(block)))
    #         # setattr = self.block_name, except block_name is a string (set instance variable from a string)
    #
    #     for net_name, net in netlist.nets:
    # # do all the connections
    # # can use getattr(self, block_name)
    #
    # def make_block_from_mapping(self, block) -> Block: ... # internal implementation
    # # for now you can hardcode if statements for the device name
    # # eg if you see Resistor, then create a EDG Resistor and parsing the value as the resistance
    # # this is the more interesting part in the future