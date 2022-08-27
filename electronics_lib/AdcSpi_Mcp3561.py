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

    self.vrefp = self.Port(VoltageSource(
      # voltage_limits=(0.6*Volt, self.avdd.link().voltage.upper()),  # TODO allow input Vrefp
      voltage_out=2.4*Volt(tol=0.02),
      current_limits=0*mAmp(tol=0),
    ))

    input_model = AnalogSink.from_supply(
      self.vss, self.avdd,
      voltage_limit_tolerance=(-0.1, 0.1)*Volt,
      impedance=(20, 510)*kOhm  # varies based on gain
    )
    self.ch = self.Port(Vector(AnalogSink().empty()))
    for i in range(8):
      self.ch.append_elt(input_model, str(i))

    dio_model = DigitalBidir.from_supply(
      self.vss, self.dvdd,
      voltage_limit_tolerance=(-0.3, 0.3)*Volt,
      input_threshold_factor=(0.3, 0.7)
    )
    # Datasheet table 1.1
    self.spi = self.Port(SpiSlave(dio_model, frequency_limit=(0, 10)*MHertz))  # note 20MHz for >2.7V DVdd
    self.cs = self.Port(dio_model)

  def contents(self) -> None:
    # TODO specify part number based on used channels and connected reference
    self.footprint(
      'U', 'Package_SO:TSSOP-20_4.4x6.5mm_P0.65mm',
      {
        '1': self.avdd,
        '2': self.vss,
        '3': self.vss,  # actually Vref-
        '4': self.vrefp,
        '5': self.ch['0'],
        '6': self.ch['1'],
        '7': self.ch['2'],
        '8': self.ch['3'],
        '9': self.ch['4'],
        '10': self.ch['5'],
        '11': self.ch['6'],
        '12': self.ch['7'],
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
  """MCP3561R up-to-24-bit delta-sigma ADC with internal voltage reference.
  """
  def __init__(self) -> None:
    super().__init__()
    self.ic = self.Block(Mcp3561_Device())
    self.pwra = self.Port(VoltageSink.empty())
    self.pwr = self.Port(VoltageSink.empty())
    self.gnd = self.Export(self.ic.vss, [Common])
    self.vref = self.Export(self.ic.vrefp, optional=True)

    self.vins = self.Export(self.ic.ch)

    self.spi = self.Export(self.ic.spi, [Output])
    self.cs = self.Export(self.ic.cs)

  def contents(self) -> None:
    super().contents()

    self.avdd_res = self.Block(SeriesPowerResistor(
      10*Ohm(tol=0.05)
    )).connected(self.pwra, self.ic.avdd)
    self.dvdd_res = self.Block(SeriesPowerResistor(
      10*Ohm(tol=0.05)
    )).connected(self.pwr, self.ic.dvdd)
    with self.implicit_connect(
        ImplicitConnect(self.gnd, [Common]),
    ) as imp:
      cap_model = DecouplingCapacitor(capacitance=0.1*uFarad(tol=0.2))
      self.avdd_cap_0 = imp.Block(cap_model).connected(pwr=self.ic.avdd)
      self.avdd_cap_1 = imp.Block(cap_model).connected(pwr=self.ic.avdd)
      self.dvdd_cap_0 = imp.Block(cap_model).connected(pwr=self.ic.dvdd)
      self.dvdd_cap_1 = imp.Block(cap_model).connected(pwr=self.ic.dvdd)

      self.vref_cap = imp.Block(DecouplingCapacitor(10*uFarad(tol=0.2))).connected(pwr=self.ic.vrefp)
