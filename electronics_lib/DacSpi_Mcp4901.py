from typing import *

from electronics_abstract_parts import *


class Mcp4921_Device(DiscreteChip, FootprintBlock):
  def __init__(self) -> None:
    super().__init__()
    self.vdd = self.Port(VoltageSink(
      voltage_limits=(2.7, 5.5)*Volt,
      current_draw=(3.3, 350)*uAmp))  # from software shutdown to operating
    self.vss = self.Port(Ground())

    self.vref = self.Port(VoltageSink(
      voltage_limits=(0.04*Volt, self.vdd.link().voltage.lower() - 0.04),
      current_draw=(0, 0)  # input current not specified
    ))
    self.vout = self.Port(AnalogSource(
      voltage_out=(0.01, self.vref.link().voltage.lower() - 0.04),
      current_limits=(-15, 15)*mAmp,  # short circuit current, typ
      impedance=(171, 273)*Ohm  # derived from assumed Vout=2Vref=4.096, Isc=24mA or 15mA
    ))

    dio_model = DigitalBidir.from_supply(
      self.vss, self.vdd,
      voltage_limit_tolerance=(-0.3, 0.3)*Volt,
      current_draw=(0, 0),  # leakage current not modeled
      current_limits=(-25, 25)*mAmp,
      input_threshold_factor=(0.2, 0.7)
    )
    self.ldac = self.Port(dio_model)
    self.spi = self.Port(SpiSlave(dio_model, frequency_limit=(0, 20)*MHertz))
    self.cs = self.Port(dio_model)

  def contents(self) -> None:
    self.footprint(
      'U', 'Package_SO:SOIC-8_3.9x4.9mm_P1.27mm',
      {
        '1': self.vdd,
        '2': self.cs,
        '3': self.spi.sck,
        '4': self.spi.mosi,
        '5': self.ldac,
        '6': self.vref,
        '7': self.vss,
        '8': self.vout,
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
    self.out = self.Export(self.ic.vout, [Output])

    self.spi = self.Export(self.ic.spi, [Input])
    self.cs = self.Export(self.ic.cs)
    self.ldac = self.Export(self.ic.ldac)

  def contents(self) -> None:
    super().contents()

    # Datasheet section 6.2, example uses two bypass capacitors
    self.vdd_cap = ElementDict[DecouplingCapacitor]()
    self.vdd_cap[0] = self.Block(DecouplingCapacitor(0.1 * uFarad(tol=0.2))).connected(self.gnd, self.pwr)
    self.vdd_cap[1] = self.Block(DecouplingCapacitor(10 * uFarad(tol=0.2))).connected(self.gnd, self.pwr)
