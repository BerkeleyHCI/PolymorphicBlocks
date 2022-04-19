from typing import *

from electronics_abstract_parts import *


class Mcp3561_Device(DiscreteChip, FootprintBlock):
  def __init__(self) -> None:
    super().__init__()
    self.avdd = self.Port(VoltageSink(
      voltage_limits=(2.7, 3.6)*Volt,
      current_draw=(0.0004, 2.5)*mAmp))  # shutdown to max operating currrent
    self.dvdd = self.Port(VoltageSink(
      voltage_limits=(1.8*Volt, self.avdd.link().voltage.upper() + 0.1),
      current_draw=(0.002, 0.37)*mAmp))  # shutdown to max operating current
    self.vss = self.Port(Ground())

    self.vref = self.Port(VoltageSink(
      # voltage_limits=(0.25*Volt, self.vdd.link().voltage.upper()),
      # current_draw=(0.001, 150)*uAmp
    ), optional=True)  # R version has internal voltage reference
    input_model = AnalogSink(

    )
    self.inp = self.Port(AnalogSink.from_supply(
      self.vss, self.avdd,
      voltage_limit_tolerance=(-0.1, 0.1)*Volt,
      impedance=(20, 510)*kOhm  # varies based on gain
    ))

    dio_model = DigitalBidir.from_supply(
      self.vss, self.vdd,
      voltage_limit_tolerance=(-0.3, 0.3)*Volt,
      input_threshold_factor=(0.3, 0.7)
    )
    # Datasheet table 1.1
    self.spi = self.Port(SpiSlave(dio_model, frequency_limit=(0, 10)*MHertz))  # note 20MHz for >2.7V DVdd
    self.cs = self.Port(dio_model)

  def contents(self) -> None:
    self.footprint(
      'U', 'Package_SO:TSSOP-20_4.4x6.5mm_P0.65mm',
      {
        '1': self.avdd,
        '2': self.vss,
        # '3': REFIN-
        '4': self.vref,
        '5': self.inp,
        # '6': CH1
        '13': self.cs,
        '14': self.spi.sck,
        '15': self.spi.mosi,
        '16': self.spi.miso,
        # '17': nIRQ / MDAT
        # '18': MCLK
        '19': self.vss,
        '20': self.dvdd,
      },
      mfr='Microchip Technology', part='MCP3561R-*/ST',
      datasheet='https://ww1.microchip.com/downloads/en/DeviceDoc/MCP3561.2.4R-Data-Sheet-DS200006391A.pdf'
    )


class Mcp3561(Block):
  """MCP3561R up-to-24-bit delta-sigma ADC with interrnal voltage reference.
  """
  def __init__(self) -> None:
    super().__init__()
    self.ic = self.Block(Mcp3561_Device())
    self.pwr = self.Export(self.ic.vdd, [Power])
    self.gnd = self.Export(self.ic.vss, [Common])

    self.ref = self.Export(self.ic.vref)
    self.vin = self.Export(self.ic.inp, [Input])

    self.spi = self.Export(self.ic.spi, [Output])
    self.cs = self.Export(self.ic.cs)

  def contents(self) -> None:
    super().contents()

    # Datasheet Section 6.4: 1uF cap recommended
    self.vdd_cap = self.Block(DecouplingCapacitor(
      capacitance=1*uFarad(tol=0.2),
    )).connected(self.gnd, self.pwr)
