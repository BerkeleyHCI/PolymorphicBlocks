import unittest

from edg_core import *
from .CanPort import CanDiffPort
from .CircuitBlock import FootprintBlock
from .DigitalPorts import DigitalSource, DigitalSink
from .SpiPort import SpiController, SpiPeripheral
from .UartPort import UartPort
from .test_netlist import NetlistTestCase, Net, NetPin, NetBlock


class TestFakeSpiController(FootprintBlock):
  def __init__(self) -> None:
    super().__init__()

    self.spi = self.Port(SpiController())
    self.cs_out_1 = self.Port(DigitalSource())
    self.cs_out_2 = self.Port(DigitalSource())

  def contents(self) -> None:
    super().contents()
    self.footprint(  # it's anyone's guess why the resistor array is a SPI controller
      'R', 'Resistor_SMD:R_Array_Concave_2x0603',
      {
        '0': self.cs_out_1,  # the mythical and elusive pin 0
        '1': self.cs_out_2,
        '2': self.spi.sck,
        '3': self.spi.miso,
        '4': self.spi.mosi,
      },
      value='WeirdSpiController'
    )


class TestFakeSpiPeripheral(FootprintBlock):
  def __init__(self) -> None:
    super().__init__()

    self.spi = self.Port(SpiPeripheral())
    self.cs_in = self.Port(DigitalSink())

  def contents(self) -> None:
    super().contents()
    self.footprint(  # it's anyone's guess why this resistor array has a different pinning in peripheral mode
      'R', 'Resistor_SMD:R_Array_Concave_2x0603',
      {
        '1': self.spi.sck,
        '2': self.spi.mosi,
        '3': self.spi.miso,
        '4': self.cs_in,
      },
      value='WeirdSpiPeripheral'
    )


class TestSpiCircuit(Block):
  def contents(self) -> None:
    super().contents()

    self.controller = self.Block(TestFakeSpiController())
    self.peripheral1 = self.Block(TestFakeSpiPeripheral())
    self.peripheral2 = self.Block(TestFakeSpiPeripheral())

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

    self.assertIn(Net('cs1_link', [
      NetPin(['controller'], '0'),
      NetPin(['peripheral1'], '4'),
    ], [
      TransformUtil.Path.empty().append_block('controller').append_port('cs_out_1'),
      TransformUtil.Path.empty().append_block('peripheral1').append_port('cs_in'),
    ]), net.nets)
    self.assertIn(Net('cs2_link', [
      NetPin(['controller'], '1'),
      NetPin(['peripheral2'], '4'),
    ], [
      TransformUtil.Path.empty().append_block('controller').append_port('cs_out_2'),
      TransformUtil.Path.empty().append_block('peripheral2').append_port('cs_in'),
    ]), net.nets)
    self.assertIn(Net('spi_link.sck', [
      NetPin(['controller'], '2'),
      NetPin(['peripheral1'], '1'),
      NetPin(['peripheral2'], '1'),
    ], [
      TransformUtil.Path.empty().append_block('controller').append_port('spi', 'sck'),
      TransformUtil.Path.empty().append_block('peripheral1').append_port('spi', 'sck'),
      TransformUtil.Path.empty().append_block('peripheral2').append_port('spi', 'sck'),
    ]), net.nets)
    self.assertIn(Net('spi_link.mosi', [
      NetPin(['controller'], '4'),
      NetPin(['peripheral1'], '2'),
      NetPin(['peripheral2'], '2'),
    ], [
      TransformUtil.Path.empty().append_block('controller').append_port('spi', 'mosi'),
      TransformUtil.Path.empty().append_block('peripheral1').append_port('spi', 'mosi'),
      TransformUtil.Path.empty().append_block('peripheral2').append_port('spi', 'mosi'),
    ]), net.nets)
    self.assertIn(Net('spi_link.miso', [
      NetPin(['controller'], '3'),
      NetPin(['peripheral1'], '3'),
      NetPin(['peripheral2'], '3'),
    ], [
      TransformUtil.Path.empty().append_block('controller').append_port('spi', 'miso'),
      TransformUtil.Path.empty().append_block('peripheral1').append_port('spi', 'miso'),
      TransformUtil.Path.empty().append_block('peripheral2').append_port('spi', 'miso'),
    ]), net.nets)

    self.assertIn(NetBlock('Resistor_SMD:R_Array_Concave_2x0603', 'R1', '', 'WeirdSpiController',
                           ['controller'], ['controller'],
                           ['electronics_model.test_bundle_netlist.TestFakeSpiController']),
                  net.blocks)
    self.assertIn(NetBlock('Resistor_SMD:R_Array_Concave_2x0603', 'R2', '', 'WeirdSpiPeripheral',
                           ['peripheral1'], ['peripheral1'],
                           ['electronics_model.test_bundle_netlist.TestFakeSpiPeripheral']),
                  net.blocks)
    self.assertIn(NetBlock('Resistor_SMD:R_Array_Concave_2x0603', 'R3', '', 'WeirdSpiPeripheral',
                           ['peripheral2'], ['peripheral2'],
                           ['electronics_model.test_bundle_netlist.TestFakeSpiPeripheral']),
                  net.blocks)

  def test_uart_netlist(self) -> None:
    net = NetlistTestCase.generate_net(TestUartCircuit)

    self.assertIn(Net('link.a_tx', [
      NetPin(['a'], '1'),
      NetPin(['b'], '2')
    ], [
      TransformUtil.Path.empty().append_block('a').append_port('port', 'tx'),
      TransformUtil.Path.empty().append_block('b').append_port('port', 'rx'),
    ]), net.nets)
    self.assertIn(Net('link.b_tx', [
      NetPin(['a'], '2'),
      NetPin(['b'], '1')
    ], [
      TransformUtil.Path.empty().append_block('a').append_port('port', 'rx'),
      TransformUtil.Path.empty().append_block('b').append_port('port', 'tx'),
    ]), net.nets)
    self.assertIn(NetBlock('Resistor_SMD:R_0603_1608Metric', 'R1', '', '1k',
                           ['a'], ['a'], ['electronics_model.test_bundle_netlist.TestFakeUartBlock']),
                  net.blocks)
    self.assertIn(NetBlock('Resistor_SMD:R_0603_1608Metric', 'R2', '', '1k',
                           ['b'], ['b'], ['electronics_model.test_bundle_netlist.TestFakeUartBlock']),
                  net.blocks)

  def test_can_netlist(self) -> None:
    net = NetlistTestCase.generate_net(TestCanCircuit)

    self.assertIn(Net('link.canh', [
      NetPin(['node1'], '1'),
      NetPin(['node2'], '1'),
      NetPin(['node3'], '1')
    ], [
      TransformUtil.Path.empty().append_block('node1').append_port('port', 'canh'),
      TransformUtil.Path.empty().append_block('node2').append_port('port', 'canh'),
      TransformUtil.Path.empty().append_block('node3').append_port('port', 'canh'),
    ]), net.nets)
    self.assertIn(Net('link.canl', [
      NetPin(['node1'], '2'),
      NetPin(['node2'], '2'),
      NetPin(['node3'], '2')
    ], [
      TransformUtil.Path.empty().append_block('node1').append_port('port', 'canl'),
      TransformUtil.Path.empty().append_block('node2').append_port('port', 'canl'),
      TransformUtil.Path.empty().append_block('node3').append_port('port', 'canl'),
    ]), net.nets)
    self.assertIn(NetBlock('Resistor_SMD:R_0603_1608Metric', 'R1', '', '120',
                           ['node1'], ['node1'], ['electronics_model.test_bundle_netlist.TestFakeCanBlock']),
                  net.blocks)
    self.assertIn(NetBlock('Resistor_SMD:R_0603_1608Metric', 'R2', '', '120',
                           ['node2'], ['node2'], ['electronics_model.test_bundle_netlist.TestFakeCanBlock']),
                  net.blocks)
    self.assertIn(NetBlock('Resistor_SMD:R_0603_1608Metric', 'R3', '', '120',
                           ['node3'], ['node3'], ['electronics_model.test_bundle_netlist.TestFakeCanBlock']),
                  net.blocks)
