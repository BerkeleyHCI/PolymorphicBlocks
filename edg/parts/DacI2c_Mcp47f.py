from ..abstract_parts import *


class Mcp47f_Device(InternalSubcircuit, FootprintBlock, GeneratorBlock):
  @init_in_parent
  def __init__(self, addr_lsb: IntLike) -> None:
    super().__init__()
    self.vss = self.Port(Ground())
    self.vdd = self.Port(VoltageSink(
      voltage_limits=(2.7, 5.5)*Volt,  # technically down to 1.8 w/ reduced performance
      current_draw=(0.00085, 2.5)*mAmp))  # quad DAC, serial inactive to EE write

    ref_model = VoltageSink(
      voltage_limits=self.vss.link().voltage.hull(self.vdd.link().voltage)
    )
    self.vref0 = self.Port(ref_model)
    self.vref1 = self.Port(ref_model)

    out_ref0_model = AnalogSource.from_supply(
      self.vss, self.vref0,
      signal_out_bound=(0.01*Volt, -0.016*Volt),  # output amp min / max voltages
      current_limits=(-3, 3)*mAmp,  # short circuit current, typ
      impedance=(122, 900)*Ohm  # derived from assumed Vout=Vdd=2.7v, Isc=3-22mA
    )
    out_ref1_model = AnalogSource.from_supply(
      self.vss, self.vref1,
      signal_out_bound=(0.01*Volt, -0.016*Volt),  # output amp min / max voltages
      current_limits=(-3, 3)*mAmp,  # short circuit current, typ
      impedance=(122, 900)*Ohm  # derived from assumed Vout=Vdd=2.7v, Isc=3-22mA
    )
    self.vout0 = self.Port(out_ref0_model, optional=True)
    self.vout1 = self.Port(out_ref1_model, optional=True)
    self.vout2 = self.Port(out_ref0_model, optional=True)
    self.vout3 = self.Port(out_ref1_model, optional=True)

    dio_model = DigitalBidir.from_supply(  # LAT0/1/HVC, same input thresholds for I2C
      self.vss, self.vdd,
      voltage_limit_tolerance=(-0.6, 0.3)*Volt,
      current_limits=(-2, 2)*mAmp,
      input_threshold_factor=(0.3, 0.7)
    )
    self.lat0 = self.Port(dio_model)
    self.lat1 = self.Port(dio_model)
    self.i2c = self.Port(I2cTarget(dio_model, addresses=ArrayIntExpr()))

    self.addr_lsb = self.ArgParameter(addr_lsb)
    self.generator_param(self.addr_lsb)

  def generate(self) -> None:
    super().generate()

    addr_lsb = self.get(self.addr_lsb)
    self.require((addr_lsb < 4) & (addr_lsb >= 0), f"addr_lsb={addr_lsb} must be within [0, 4)")
    self.assign(self.i2c.addresses, [0x60 | addr_lsb])  # fixed for volatile devices

    self.footprint(
      'U', 'Package_SO:TSSOP-20_4.4x6.5mm_P0.65mm',
      {
        '1': self.lat1,
        '2': self.vdd,
        '3': self.vdd if addr_lsb & 1 else self.vss,  # A0
        '4': self.vref0,
        '5': self.vout0,
        '6': self.vout2,
        # '7', '8': nc
        '9': self.vss,
        # '10', '11', '12', '13': nc
        '14': self.vout3,
        '15': self.vout1,
        '16': self.vref1,
        '17': self.vdd if addr_lsb & 2 else self.vss,  # A1
        '18': self.i2c.scl,
        '19': self.i2c.sda,
        '20': self.lat0

      },
      mfr='Microchip Technology', part='MCP47FVB24T-20E/ST',
      datasheet='https://ww1.microchip.com/downloads/aemDocuments/documents/MSLD/ProductDocuments/DataSheets/MCP47FXBX48-Data-Sheet-DS200006368A.pdf'
    )


class Mcp47f(DigitalToAnalog, Block):
  """MCP47FxBx4/8 quad / octal 8/10/12-bit I2C DAC, with selectable internal or external Vref
  """
  def __init__(self, addr_lsb: IntLike = 0) -> None:
    super().__init__()
    self.ic = self.Block(Mcp47f_Device(addr_lsb=addr_lsb))
    self.pwr = self.Export(self.ic.vdd, [Power])
    self.gnd = self.Export(self.ic.vss, [Common])

    self.ref0 = self.Export(self.ic.vref0)
    self.ref1 = self.Export(self.ic.vref1)

    self.out0 = self.Export(self.ic.vout0, optional=True)
    self.out1 = self.Export(self.ic.vout1, optional=True)
    self.out2 = self.Export(self.ic.vout2, optional=True)
    self.out3 = self.Export(self.ic.vout3, optional=True)

    self.i2c = self.Export(self.ic.i2c)
    self.lat0 = self.Export(self.ic.lat0)
    self.lat1 = self.Export(self.ic.lat1)

  def contents(self) -> None:
    super().contents()

    # Datasheet section 6.2, example uses two bypass capacitors
    self.vdd_cap = ElementDict[DecouplingCapacitor]()
    self.vdd_cap[0] = self.Block(DecouplingCapacitor(0.1 * uFarad(tol=0.2))).connected(self.gnd, self.pwr)
    self.vdd_cap[1] = self.Block(DecouplingCapacitor(10 * uFarad(tol=0.2))).connected(self.gnd, self.pwr)
