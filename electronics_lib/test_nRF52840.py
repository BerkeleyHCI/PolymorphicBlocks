import unittest

from edg import *
from electronics_lib.Microcontroller_nRF52840 import nRF52840
from examples.ExampleTestUtils import run_test


class TestBlinkyBasic(BoardTop):
  def contents(self):
    super().contents()
    self.mcu = self.Block(nRF52840())

    self.led = self.Block(IndicatorLed())
    self.connect(self.mcu.gnd, self.led.gnd)
    self.connect(self.mcu.new_io(DigitalBidir), self.led.signal)

  def refinements(self) -> Refinements:
    return super().refinements() + Refinements(
      instance_values=[
        (['mcu', 'pin_assigns'], "")
      ]
    )

class Mcp9700_Device(CircuitBlock):
  def __init__(self) -> None:
    super().__init__()
    # block boundary (ports, parameters) definition here
    self.vdd = self.Port(ElectricalSink(
      voltage_limits=(2.3, 5.5)*Volt, current_draw=(0, 15)*uAmp
    ), [Power])
    self.vout = self.Port(AnalogSource(
      voltage_out=(0.1, 2), current_limits=(0, 100)*uAmp,
      impedance=(20, 20)*Ohm
    ), [Output])
    self.gnd = self.Port(Ground(), [Common])

  def contents(self) -> None:
    super().contents()
    # block implementation (subblocks, internal connections, footprint) here
    self.footprint(
      'U', 'Package_TO_SOT_SMD:SOT-23',
      {
        '1': self.vdd,
        '2': self.vout,
        '3': self.gnd,
      },
      mfr='Microchip Technology', part='MCP9700T-E/TT',
      datasheet='http://ww1.microchip.com/downloads/en/DeviceDoc/20001942G.pdf'
    )

class Mcp9700(Block):
  def __init__(self) -> None:
    super().__init__()
    self.ic = self.Block(Mcp9700_Device())
    self.pwr = self.Export(self.ic.vdd, [Power])
    self.gnd = self.Export(self.ic.gnd, [Common])
    self.out = self.Export(self.ic.vout, [Output])

  def contents(self) -> None:
    super().contents()
    with self.implicit_connect(
            ImplicitConnect(self.pwr, [Power]),
            ImplicitConnect(self.gnd, [Common])
    ) as imp:
      self.vdd_cap = imp.Block(DecouplingCapacitor(capacitance=0.1*uFarad(tol=0.2)))

class BlinkyTestCase(unittest.TestCase):
  def test_design_basic(self) -> None:
    run_test(TestBlinkyBasic)
