from electronics_abstract_parts import *
from .JlcPart import JlcPart


class Mcp4728_Device(InternalSubcircuit, FootprintBlock, GeneratorBlock, JlcPart):
  @init_in_parent
  def __init__(self) -> None:
    super().__init__()
    self.vss = self.Port(Ground())
    self.vdd = self.Port(VoltageSink(
      voltage_limits=(2.7, 5.5)*Volt,
      current_draw=(0.040, 1400)*uAmp))  # power down to all channels in normal mode

    out_model = AnalogSource.from_supply(
      self.vss, self.vdd,  # assumed Vref=Vdd, also configurable
      current_limits=(-15, 15)*mAmp,  # short circuit current, typ
      impedance=(1, 1)*Ohm  # DC output impednace in normal mode
    )
    self.vout0 = self.Port(out_model, optional=True)
    self.vout1 = self.Port(out_model, optional=True)
    self.vout2 = self.Port(out_model, optional=True)
    self.vout3 = self.Port(out_model, optional=True)

    dio_model = DigitalBidir.from_supply(  # LAT0/1/HVC, same input thresholds for I2C
      self.vss, self.vdd,
      voltage_limit_tolerance=(-0.3, 0.3)*Volt,
      input_threshold_factor=(0.3, 0.7)  # for Vdd >= 2.7v
    )
    self.i2c = self.Port(I2cTarget(dio_model, addresses=[0x60]))  # TODO 3LSBs EEPROM programmable
    self.ldac = self.Port(DigitalSink.from_bidir(dio_model), optional=True)
    self.rdy = self.Port(DigitalSingleSource.low_from_supply(self.vss), optional=True)

    self.generator_param(self.ldac.is_connected())

  def generate(self) -> None:
    super().generate()

    self.footprint(
      'U', 'Package_SO:MSOP-10_3x3mm_P0.5mm',
      {
        '1': self.vdd,
        '2': self.i2c.scl,
        '3': self.i2c.sda,
        '4': self.ldac if self.get(self.ldac.is_connected()) else self.vdd,
        '5': self.rdy,  # float if not connected
        '6': self.vout0,
        '7': self.vout1,
        '8': self.vout2,
        '9': self.vout3,
        '10': self.vss,
      },
      mfr='Microchip Technology', part='MCP4728-E/UN',
      datasheet='https://ww1.microchip.com/downloads/aemDocuments/documents/OTH/ProductDocuments/DataSheets/22187E.pdf'
    )
    self.assign(self.lcsc_part, 'C108207')
    self.assign(self.actual_basic_part, False)


class Mcp4728(DigitalToAnalog, Block):
  """MCP4728 quad 12-bit I2C DAC, with selectable internal or external Vref=Vdd
  """
  def __init__(self) -> None:
    super().__init__()
    self.ic = self.Block(Mcp4728_Device())
    self.pwr = self.Export(self.ic.vdd, [Power])
    self.gnd = self.Export(self.ic.vss, [Common])

    self.out0 = self.Export(self.ic.vout0, optional=True)
    self.out1 = self.Export(self.ic.vout1, optional=True)
    self.out2 = self.Export(self.ic.vout2, optional=True)
    self.out3 = self.Export(self.ic.vout3, optional=True)

    self.i2c = self.Export(self.ic.i2c)
    self.ldac = self.Export(self.ic.ldac, optional=True)  # can update per-channel by i2c
    self.rdy = self.Export(self.ic.rdy, optional=True)  # can be read from i2c

  def contents(self) -> None:
    super().contents()

    self.vdd_cap = ElementDict[DecouplingCapacitor]()
    self.vdd_cap[0] = self.Block(DecouplingCapacitor(0.1 * uFarad(tol=0.2))).connected(self.gnd, self.pwr)
    self.vdd_cap[1] = self.Block(DecouplingCapacitor(10 * uFarad(tol=0.2))).connected(self.gnd, self.pwr)
