from typing import *

from electronics_abstract_parts import *


class Mcp4921_Device(DiscreteChip, FootprintBlock):
  def __init__(self) -> None:
    super().__init__()
    self.vdd = self.Port(VoltageSink(
      voltage_limits=(2.7, 5.5)*Volt,
      current_draw=(0.5, 400)*uAmp))  # from standby to operating
    self.vss = self.Port(Ground())

    self.vref = self.Port(AnalogSink(
      voltage_limits=(0.25*Volt, self.vdd.link().voltage.upper()),
      current_draw=(0.001, 150)*uAmp,
      impedance=(5000000, 33)*kOhm  # derived from test condition Vref=5 / current draw
    ))
    self.inp = self.Port(AnalogSink(
      voltage_limits=(0, self.vref.link().voltage.lower()),
      current_draw=(-1, 1)*uAmp,
      impedance=(5, 5000)*MOhm  # derived from assumption Vin=5 / 0.001 - 1uA leakage current
    ))

    dio_model = DigitalBidir.from_supply(
      self.vss, self.vdd,
      voltage_limit_tolerance=(-0.6, 0.6)*Volt,
      current_draw=(-10, 10)*uAmp,
      input_threshold_factor=(0.3, 0.7),
    )
    self.spi = self.Port(SpiSlave(dio_model))
    self.cs = self.Port(dio_model)

  def contents(self) -> None:
    self.footprint(
      'U', 'Package_SO:SO-8_3.9x4.9mm_P1.27mm',
      {
        '1': self.vref,
        '2': self.inp,
        '3': self.vss,  # IN-, but because it's so limited this is configured for single-ended mode
        '4': self.vss,
        '5': self.cs,
        '6': self.spi.miso,
        '7': self.spi.sck,
        '8': self.vdd
      },
      mfr='Microchip Technology', part='MCP4921-E/SN',
      datasheet='https://ww1.microchip.com/downloads/en/DeviceDoc/22248a.pdf'
    )


class Mcp4921(Block):
  """MCP4921 12-bit 4.5uS DAC.
  Other chips in series:
  MCP4901 (8 bits), MCP4911 (10 bits), and others with 2 channels or internal Vref
  """
  def __init__(self) -> None:
    super().__init__()
    self.ic = self.Block(Mcp4921_Device())
    self.pwr = self.Export(self.ic.vdd, [Power])
    self.gnd = self.Export(self.ic.vss, [Common])

    self.ref = self.Export(self.ic.vref)
    self.vin = self.Export(self.ic.inp)

    self.spi = self.Export(self.ic.spi)
    self.cs = self.Export(self.ic.cs)
    self.ldac = self.Export(self.ic.ldac)

  def contents(self) -> None:
    super().contents()

    # Datasheet section 6.2, example uses two bypass capacitors
    self.vdd_cap = ElementDict[DecouplingCapacitor]()
    with self.implicit_connect(
        ImplicitConnect(self.pwr, [Power]),
        ImplicitConnect(self.gnd, [Common])
    ) as imp:
      self.vdd_cap[0] = imp.Block(DecouplingCapacitor(0.1 * uFarad(tol=0.2)))
      self.vdd_cap[1] = imp.Block(DecouplingCapacitor(10 * uFarad(tol=0.2)))
