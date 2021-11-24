from typing import *

from electronics_abstract_parts import *


class Mcp3201_Device(DiscreteChip, FootprintBlock):
  def __init__(self) -> None:
    super().__init__()
    self.vdd = self.Port(VoltageSink(
      voltage_limits=(2.7, 5.5)*Volt,
      current_draw=(0.5, 400)*uAmp))  # from standby to operating
    self.vss = self.Port(Ground())

    self.vref = self.Port(VoltageSink(
      voltage_limits=(0.25*Volt, self.vdd.link().voltage.lower()),
      current_draw=(0.001, 150)*uAmp
    ))
    self.inp = self.Port(AnalogSink(
      voltage_limits=(0, self.vref.link().voltage.lower()),
      current_draw=(0, 0),  # leakage current not modeled
      impedance=(5, 5000)*MOhm  # derived from assumption Vin=5 / 0.001 - 1uA leakage current
    ))

    dio_model = DigitalBidir.from_supply(
      self.vss, self.vdd,
      voltage_limit_tolerance=(-0.6, 0.6)*Volt,
      current_draw=(0, 0),  # leakage current not modeled
      input_threshold_factor=(0.3, 0.7),
      output_threshold_factor=(0, 1)
    )
    # Datasheet section 6.2, minimum clock speed
    self.spi = self.Port(SpiSlave(dio_model, frequency_limit=(10, 1600)*kHertz))
    self.cs = self.Port(dio_model)

  def contents(self) -> None:
    # Note, B-grade chip has lower INL (+/-1 LSB) compared to C-grade (+/-2 LSB)
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
        '8': self.vdd,
      },
      mfr='Microchip Technology', part='MCP3201T-BI/SN',
      datasheet='https://ww1.microchip.com/downloads/en/DeviceDoc/21290F.pdf'
    )


class Mcp3201(Block):
  """MCP3201 12-bit 100kSPS ADC configured in single-ended mode, since the IN- pin can't do much anyways.

  Some drop-in electrically compatible chips:
  - ADS7822 (12 bit, 200kSPS)
  - MCP3551 (22 bit, low sample rate, delta-sigma)
    - SLIGHTLY DIFFERENT PINNING! SCK and CS swapped!
  """
  def __init__(self) -> None:
    super().__init__()
    self.ic = self.Block(Mcp3201_Device())
    self.pwr = self.Export(self.ic.vdd, [Power])
    self.gnd = self.Export(self.ic.vss, [Common])

    self.ref = self.Export(self.ic.vref)
    self.vin = self.Export(self.ic.inp, [Input])

    self.spi = self.Export(self.ic.spi, [Output])
    self.cs = self.Export(self.ic.cs)

  def contents(self) -> None:
    super().contents()

    # Datasheet Section 6.4: 1uF cap recommended
    with self.implicit_connect(
        ImplicitConnect(self.pwr, [Power]),
        ImplicitConnect(self.gnd, [Common])
    ) as imp:
      self.vdd_cap = imp.Block(DecouplingCapacitor(
        capacitance=1*uFarad(tol=0.2),
      ))
