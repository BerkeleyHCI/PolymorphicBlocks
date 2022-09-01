from edg import *

from edg import *
from electronics_model.MyKiCadBlock import MyKicadBlock


class L293dd_Device(DiscreteChip, FootprintBlock):
    def __init__(self) -> None:
        super().__init__()
        self.vss = self.Port(VoltageSink(voltage_limits=(4.5, 36) * Volt, current_draw=RangeExpr()))
        self.vs = self.Port(VoltageSink(
            voltage_limits=(self.vss.link().voltage.lower(), 36 * Volt), current_draw=RangeExpr())
        )
        self.gnd = self.Port(Ground())


class L293dd(Block):
    def __init__(self) -> None:
        super().__init__()
        self.ic = self.Block(L293dd_Device())
        self.vs = self.Export(self.ic.vs)
        self.vss = self.Export(self.ic.vss)
        self.gnd = self.Export(self.ic.gnd, [Common])

    def contents(self) -> None:
        super().contents()

        self.vdd_cap = ElementDict[DecouplingCapacitor]()
        self.vdd_cap[0] = self.Block(DecouplingCapacitor(0.1 * uFarad(tol=0.2))).connected(self.gnd, self.vss)
        self.vdd_cap[1] = self.Block(DecouplingCapacitor(1 * uFarad(tol=0.2))).connected(self.gnd, self.vs)


class EXKicadBlock(Block):

    def __init__(self) -> None:
        super().__init__()
        self.res = None

    def contents(self) -> None:
        super().contents()
        if True:
          self.res = self.Block(Resistor())
        else:
          self.cap = self.Block(DecouplingCapacitor())

        if self.res is not None:
          self.cap = self.Block(UnpolarizedCapacitor())


class BlinkyExample(BoardTop):
    def __init__(self):
        super().__init__()
        self.test = self.Block(MyKicadBlock())
        self.res1 = self.Block(Resistor())
        self.res2 = self.Block(Resistor())
        self.cap1 = self.Block(DecouplingCapacitor())
        self.connect(self.res2.a, self.res1.a)
        # self.connect(self.res1.b, self.res2.b)
        portList = [self.res1.b, self.res2.b]
        self.connect(*portList)

    def contents(self) -> None:
        super().contents()


if __name__ == "__main__":
    compile_board_inplace(BlinkyExample)
