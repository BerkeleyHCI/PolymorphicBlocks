from electronics_abstract_parts import *


class Pcf2129_Device(DiscreteChip, FootprintBlock):
  """RTC with integrated crystal. SO-16 version"""
  def __init__(self) -> None:
    super().__init__()

    self.pwr = self.Port(VoltageSink(
      voltage_limits=(1.8, 4.2) * Volt,
      current_draw=(0, 800) * uAmp
    ), [Power])
    self.pwr_bat = self.Port(VoltageSink(
      voltage_limits=(1.8, 4.2) * Volt,
      current_draw=(0, 100) * nAmp
    ))
    self.gnd = self.Port(Ground(), [Common])

    dio_model = DigitalBidir(
      voltage_limits=(-0.5, self.pwr.link().voltage.lower() + 0.5),
      current_draw=(0, 0),
      voltage_out=(0, self.pwr.link().voltage.lower()),
      current_limits=(-1, 1) * mAmp,  # TODO higher sink current on SDA/nCE
      input_thresholds=(0.25 * self.pwr.link().voltage.upper(),
                        0.7 * self.pwr.link().voltage.upper()),
      output_thresholds=(0, self.pwr.link().voltage.upper()),
    )

    self.spi = self.Port(SpiSlave(dio_model), [Output])
    self.cs = self.Port(DigitalSink.from_bidir(dio_model))

    opendrain_model = DigitalSingleSource.low_from_supply(self.gnd)  # TODO -1 - 1 mAmp current limit?
    self.clkout = self.Port(opendrain_model, optional=True)
    self.int = self.Port(opendrain_model, optional=True)

    self.bbs = self.Port(VoltageSource(
      voltage_out=self.pwr_bat.link().voltage
    ))

  def contents(self):
    super().contents()
    self.footprint(
      'U', 'Package_SO:SOIC-16W_7.5x10.3mm_P1.27mm',
      {
        '1': self.spi.sck,  # also I2C SCL
        '2': self.spi.mosi,
        '3': self.spi.miso,
        '4': self.cs,  # also I2C SDA
        '5': self.gnd,  # IFS interface select
        # '6': ,  # nTS, active low timestamp input with internal 200k pullup
        '7': self.clkout,
        '8': self.gnd,
        '13': self.int,
        '14': self.bbs,  # output voltage, battery-backed
        '15': self.pwr_bat,
        '16': self.pwr,
      },
      mfr='NXP', part='PCF2129T',
      datasheet='https://www.nxp.com/docs/en/data-sheet/PCF2129.pdf'
    )


class Pcf2129(RealtimeClock, Block):
  """RTC with integrated crystal. SO-16 version"""
  def __init__(self) -> None:
    super().__init__()

    self.ic = self.Block(Pcf2129_Device())
    self.pwr = self.Port(VoltageSink(), [Power])
    self.pwr_bat = self.Export(self.ic.pwr_bat)
    self.gnd = self.Export(self.ic.gnd, [Common])

    self.spi = self.Export(self.ic.spi)
    self.cs = self.Export(self.ic.cs)
    self.clkout = self.Export(self.ic.clkout, optional=True)
    self.int = self.Export(self.ic.int, optional=True)

  def contents(self):
    super().contents()

    (self.vdd_res, ), _ = self.chain(
      self.pwr,
      self.Block(SeriesPowerResistor(330*Ohm(tol=0.05), (0, 800)*uAmp)),
      self.ic.pwr)

    with self.implicit_connect(
        ImplicitConnect(self.gnd, [Common])
    ) as imp:
      self.vdd_cap_0 = imp.Block(DecouplingCapacitor(
        capacitance=0.1*uFarad(tol=0.2),
      ))
      self.vdd_cap_1 = imp.Block(DecouplingCapacitor(
        capacitance=4.7*uFarad(tol=0.2),  # TODO actually 6.8 on the datasheet
      ))
      self.connect(self.ic.pwr, self.vdd_cap_0.pwr, self.vdd_cap_1.pwr)

      self.vbat_cap = imp.Block(DecouplingCapacitor(
        capacitance=0.1*uFarad(tol=0.2),
      ))
      self.connect(self.pwr_bat, self.vbat_cap.pwr)

      self.bbs_cap = imp.Block(DecouplingCapacitor(
        capacitance=0.1*uFarad(tol=0.2),  # TODO actually 1-100nF
      ))
      self.connect(self.ic.bbs, self.bbs_cap.pwr)
