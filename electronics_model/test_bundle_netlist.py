import unittest

from edg_core import *
from .CanPort import CanDiffPort
from .CircuitBlock import FootprintBlock
from .DigitalPorts import DigitalSource, DigitalSink
from .SpiPort import SpiController, SpiPeripheral
from .UartPort import UartPort
from .footprint import Pin, Block as FBlock  # TODO cleanup naming
from .test_netlist import NetlistTestCase


class TestFakeSpiMaster(FootprintBlock):
  def __init__(self) -> None:
    super().__init__()

    self.spi = self.Port(SpiController())
    self.cs_out_1 = self.Port(DigitalSource())
    self.cs_out_2 = self.Port(DigitalSource())

  def contents(self) -> None:
    super().contents()
    self.footprint(  # it's anyone's guess why the resistor array is a SPI master
      'R', 'Resistor_SMD:R_Array_Concave_2x0603',
      {
        '0': self.cs_out_1,  # the mythical and elusive pin 0
        '1': self.cs_out_2,
        '2': self.spi.sck,
        '3': self.spi.miso,
        '4': self.spi.mosi,
      },
      value='WeirdSpiMaster'
    )


class TestFakeSpiSlave(FootprintBlock):
  def __init__(self) -> None:
    super().__init__()

    self.spi = self.Port(SpiPeripheral())
    self.cs_in = self.Port(DigitalSink())

  def contents(self) -> None:
    super().contents()
    self.footprint(  # it's anyone's guess why this resistor array has a different pinning in slave mode
      'R', 'Resistor_SMD:R_Array_Concave_2x0603',
      {
        '1': self.spi.sck,
        '2': self.spi.mosi,
        '3': self.spi.miso,
        '4': self.cs_in,
      },
      value='WeirdSpiSlave'
    )


class TestSpiCircuit(Block):
  def contents(self) -> None:
    super().contents()

    self.controller = self.Block(TestFakeSpiMaster())
    self.peripheral1 = self.Block(TestFakeSpiSlave())
    self.peripheral2 = self.Block(TestFakeSpiSlave())

    self.spi_link = self.connect(self.controller.spi, self.peripheral1.spi, self.peripheral2.spi)
    self.cs1_link = self.connect(self.controller.cs_out_1, self.peripheral1.cs_in)
    self.cs2_link = self.connect(self.controller.cs_out_2, self.peripheral2.cs_in)


class TestFakeUartBlock(FootprintBlock):
  def __init__(self) -> None:
    super().__init__()

    self.port = self.Port(UartPort())

  def contents(self) -> None:
    super().contents()
    self.footprint(
      'R', 'Resistor_SMD:R_0603_1608Metric',
      {
        '1': self.port.tx,
        '2': self.port.rx
      },
      value='1k'
    )


class TestUartCircuit(Block):
  def contents(self) -> None:
    super().contents()

    self.a = self.Block(TestFakeUartBlock())
    self.b = self.Block(TestFakeUartBlock())

    self.link = self.connect(self.a.port, self.b.port)


class TestFakeCanBlock(FootprintBlock):
  def __init__(self) -> None:
    super().__init__()

    self.port = self.Port(CanDiffPort())

  def contents(self) -> None:
    super().contents()
    self.footprint(
      'R', 'Resistor_SMD:R_0603_1608Metric',
      {
        '1': self.port.canh,
        '2': self.port.canl
      },
      value='120'
    )


class TestCanCircuit(Block):
  def contents(self) -> None:
    super().contents()

    self.node1 = self.Block(TestFakeCanBlock())
    self.node2 = self.Block(TestFakeCanBlock())
    self.node3 = self.Block(TestFakeCanBlock())

    self.link = self.connect(self.node1.port, self.node2.port, self.node3.port)


class BundleNetlistTestCase(unittest.TestCase):
  def test_spi_netlist(self) -> None:
    net = NetlistTestCase.generate_net(TestSpiCircuit)

    self.assertEqual(net.nets['cs1_link'], [
      Pin('controller', '0'),
      Pin('peripheral1', '4'),
    ])
    self.assertEqual(net.nets['cs2_link'], [
      Pin('controller', '1'),
      Pin('peripheral2', '4'),
    ])
    self.assertEqual(net.nets['spi_link.sck'], [
      Pin('controller', '2'),
      Pin('peripheral1', '1'),
      Pin('peripheral2', '1'),
    ])
    self.assertEqual(net.nets['spi_link.mosi'], [
      Pin('controller', '4'),
      Pin('peripheral1', '2'),
      Pin('peripheral2', '2'),
    ])
    self.assertEqual(net.nets['spi_link.miso'], [
      Pin('controller', '3'),
      Pin('peripheral1', '3'),
      Pin('peripheral2', '3'),
    ])

    self.assertEqual(net.blocks['controller'], FBlock('Resistor_SMD:R_Array_Concave_2x0603', 'R1', '', 'WeirdSpiMaster',
                                                      ['controller'], ['controller'],
                                                      ['electronics_model.test_bundle_netlist.TestFakeSpiMaster']))
    self.assertEqual(net.blocks['peripheral1'], FBlock('Resistor_SMD:R_Array_Concave_2x0603', 'R2', '', 'WeirdSpiSlave',
                                                       ['peripheral1'], ['peripheral1'],
                                                       ['electronics_model.test_bundle_netlist.TestFakeSpiSlave']))
    self.assertEqual(net.blocks['peripheral2'], FBlock('Resistor_SMD:R_Array_Concave_2x0603', 'R3', '', 'WeirdSpiSlave',
                                                       ['peripheral2'], ['peripheral2'],
                                                       ['electronics_model.test_bundle_netlist.TestFakeSpiSlave']))

  def test_uart_netlist(self) -> None:
    net = NetlistTestCase.generate_net(TestUartCircuit)

    self.assertEqual(net.nets['link.a_tx'], [
      Pin('a', '1'),
      Pin('b', '2')
    ])
    self.assertEqual(net.nets['link.b_tx'], [
      Pin('a', '2'),
      Pin('b', '1')
    ])
    self.assertEqual(net.blocks['a'], FBlock('Resistor_SMD:R_0603_1608Metric', 'R1', '', '1k',
                                             ['a'], ['a'],
                                             ['electronics_model.test_bundle_netlist.TestFakeUartBlock']))
    self.assertEqual(net.blocks['b'], FBlock('Resistor_SMD:R_0603_1608Metric', 'R2', '', '1k',
                                             ['b'], ['b'],
                                             ['electronics_model.test_bundle_netlist.TestFakeUartBlock']))

  def test_can_netlist(self) -> None:
    net = NetlistTestCase.generate_net(TestCanCircuit)

    self.assertEqual(net.nets['link.canh'], [
      Pin('node1', '1'),
      Pin('node2', '1'),
      Pin('node3', '1')
    ])
    self.assertEqual(net.nets['link.canl'], [
      Pin('node1', '2'),
      Pin('node2', '2'),
      Pin('node3', '2')
    ])
    self.assertEqual(net.blocks['node1'], FBlock('Resistor_SMD:R_0603_1608Metric', 'R1', '', '120',
                                                 ['node1'], ['node1'],
                                                 ['electronics_model.test_bundle_netlist.TestFakeCanBlock']))
    self.assertEqual(net.blocks['node2'], FBlock('Resistor_SMD:R_0603_1608Metric', 'R2', '', '120',
                                                 ['node2'], ['node2'],
                                                 ['electronics_model.test_bundle_netlist.TestFakeCanBlock']))
    self.assertEqual(net.blocks['node3'], FBlock('Resistor_SMD:R_0603_1608Metric', 'R3', '', '120',
                                                 ['node3'], ['node3'],
                                                 ['electronics_model.test_bundle_netlist.TestFakeCanBlock']))
