import unittest

from edg import *
from .ExampleTestUtils import run_test


class TestDatalogger(BoardTop):
  def contents(self) -> None:
    super().contents()

    self.pwr_conn = self.Block(CalSolPowerConnector())
    self.usb_conn = self.Block(UsbCReceptacle())

    self.usb_forced_current = self.Block(ForcedElectricalCurrentDraw(forced_current_draw=(0, 0.5)*Amp))
    self.connect(self.usb_conn.pwr, self.usb_forced_current.pwr_in)

    self.gnd_merge1 = self.Block(MergedElectricalSource())
    self.connect(self.usb_conn.gnd, self.gnd_merge1.sink1)
    self.connect(self.pwr_conn.gnd, self.gnd_merge1.sink2)
    self.gnd_merge2 = self.Block(MergedElectricalSource())
    self.connect(self.gnd_merge1.source, self.gnd_merge2.sink1)
    # second slow reserved for the RTC battery

    self.pwr_5v_merge = self.Block(MergedElectricalSource())
    self.connect(self.usb_forced_current.pwr_out, self.pwr_5v_merge.sink1)

    with self.implicit_connect(
        ImplicitConnect(self.gnd_merge2.source, [Common]),
    ) as imp:
      (self.pwr_5v,), _ = self.chain(
        self.pwr_conn.pwr,
        imp.Block(BuckConverter(output_voltage=(4.85, 5.4)*Volt)),
        self.pwr_5v_merge.sink2
      )

      (self.buffer, self.pwr_3v3), _ = self.chain(
        self.pwr_5v_merge.source,
        imp.Block(BufferedSupply(charging_current=(0.4, 0.5)*Amp, sense_resistance=0.47*Ohm(tol=0.01),
                                 voltage_drop=(0, 0.4)*Volt)),
        imp.Block(LinearRegulator(output_voltage=3.3*Volt(tol=0.05)))
      )

    self.outline = self.Block(Outline_Pn1332())
    self.duck = self.Block(DuckLogo())

    self.vin = self.connect(self.pwr_conn.pwr)
    self.v5 = self.connect(self.pwr_5v_merge.source)
    self.v5_buffered = self.connect(self.buffer.pwr_out)
    self.v3v3 = self.connect(self.pwr_3v3.pwr_out)  # TODO better auto net names
    self.gnd = self.connect(self.gnd_merge2.source)

    with self.implicit_connect(
      ImplicitConnect(self.pwr_3v3.pwr_out, [Power]),
      ImplicitConnect(self.pwr_3v3.gnd, [Common]),
    ) as imp:
      self.mcu = imp.Block(Lpc1549_64(frequency=12 * MHertz(tol=0.005)))
      (self.swd, ), _ = self.chain(imp.Block(SwdCortexTargetHeader()), self.mcu.swd)
      (self.crystal, ), _ = self.chain(self.mcu.xtal, imp.Block(OscillatorCrystal(frequency=12 * MHertz(tol=0.005))))  # TODO can we not specify this and instead infer from MCU specs?

      self.connect(self.mcu.usb_0, self.usb_conn.usb)

      (self.can, ), _ = self.chain(self.mcu.new_io(CanControllerPort, pin=[51, 53]), imp.Block(CalSolCanBlock()))

      self.can_gnd_load = self.Block(ElectricalLoad())
      self.connect(self.can.can_gnd, self.can_gnd_load.pwr)
      self.can_pwr_load = self.Block(ElectricalLoad())
      self.connect(self.can.can_pwr, self.can_pwr_load.pwr)

      # mcu_i2c = self.mcu.new_io(I2cMaster)  # no devices, ignored for now
      # self.i2c_pullup = imp.Block(I2cPullup())
      # self.connect(self.i2c_pullup.i2c, mcu_i2c)

      sd_spi = self.mcu.new_io(SpiMaster, pin=[17, 15, 19])
      self.sd = imp.Block(SdSocket())
      self.connect(sd_spi, self.sd.spi)
      self.connect(self.mcu.new_io(DigitalBidir, pin=11), self.sd.cs)
      (self.cd_pull, ), _ = self.chain(
        self.mcu.new_io(DigitalBidir, pin=16),
        imp.Block(PullupResistor(4.7 * kOhm(tol=0.05))),
        self.sd.cd)

      xbee_uart = self.mcu.new_io(UartPort, pin=[58, 54])
      self.xbee = imp.Block(Xbee_S3b())
      self.connect(xbee_uart, self.xbee.data)
      (self.xbee_assoc, ), _ = self.chain(
        self.xbee.associate,
        imp.Block(IndicatorLed(current_draw=(0.5, 2)*mAmp)))  # XBee DIO current is -2 -> 2 mA

      aux_spi = self.mcu.new_io(SpiMaster, pin=[5, 6, 7])
      self.rtc = imp.Block(Pcf2129())
      self.connect(aux_spi, self.rtc.spi)
      self.connect(self.mcu.new_io(DigitalBidir, pin=64), self.rtc.cs)
      self.bat = imp.Block(Cr2032())
      self.connect(self.bat.pwr, self.rtc.pwr_bat)
      self.connect(self.bat.gnd, self.gnd_merge2.sink2)

      self.eink = imp.Block(E2154fs091())
      self.connect(aux_spi, self.eink.spi)
      self.connect(self.mcu.new_io(DigitalBidir, pin=1), self.eink.busy)
      self.connect(self.mcu.new_io(DigitalBidir, pin=2), self.eink.reset)
      self.connect(self.mcu.new_io(DigitalBidir, pin=3), self.eink.dc)
      self.connect(self.mcu.new_io(DigitalBidir, pin=4), self.eink.cs)

      self.ext = imp.Block(BlueSmirf())
      self.connect(self.mcu.new_io(UartPort, pin=[60, 61]), self.ext.data)
      self.connect(self.mcu.new_io(DigitalBidir, pin=62), self.ext.cts)
      self.connect(self.mcu.new_io(DigitalBidir, pin=59), self.ext.rts)

      self.rgb1 = imp.Block(IndicatorSinkRgbLed())  # system RGB 1
      self.connect(self.mcu.new_io(DigitalBidir, pin=31), self.rgb1.red)
      self.connect(self.mcu.new_io(DigitalBidir, pin=32), self.rgb1.green)
      self.connect(self.mcu.new_io(DigitalBidir, pin=30), self.rgb1.blue)

      self.rgb2 = imp.Block(IndicatorSinkRgbLed())  # sd card RGB
      self.connect(self.mcu.new_io(DigitalBidir, pin=28), self.rgb2.red)
      self.connect(self.mcu.new_io(DigitalBidir, pin=29), self.rgb2.green)
      self.connect(self.mcu.new_io(DigitalBidir, pin=25), self.rgb2.blue)

      self.rgb3 = imp.Block(IndicatorSinkRgbLed())
      self.connect(self.mcu.new_io(DigitalBidir, pin=46), self.rgb3.red)
      self.connect(self.mcu.new_io(DigitalBidir, pin=39), self.rgb3.green)
      self.connect(self.mcu.new_io(DigitalBidir, pin=38), self.rgb3.blue)

      sw_pull_model = PullupResistor(4.7 * kOhm(tol=0.05))
      (self.sw1, self.sw1_pull), _ = self.chain(imp.Block(DigitalSwitch()), imp.Block(sw_pull_model), self.mcu.new_io(DigitalBidir, pin=33))
      (self.sw2, self.sw2_pull), _ = self.chain(imp.Block(DigitalSwitch()), imp.Block(sw_pull_model), self.mcu.new_io(DigitalBidir, pin=23))

    with self.implicit_connect(
        ImplicitConnect(self.pwr_3v3.gnd, [Common]),
    ) as imp:
      div_model = VoltageDivider(output_voltage=3 * Volt(tol=0.15), impedance=(100, 1000) * Ohm)
      (self.v12sense, ), _ = self.chain(self.pwr_conn.pwr, imp.Block(div_model), self.mcu.new_io(AnalogSink, pin=10))
      (self.v5sense, ), _ = self.chain(self.pwr_5v.pwr_out, imp.Block(div_model), self.mcu.new_io(AnalogSink, pin=9))
      (self.vscsense, ), _ = self.chain(self.buffer.sc_out, imp.Block(div_model), self.mcu.new_io(AnalogSink, pin=8))

    self.hole = ElementDict[MountingHole]()
    for i in range(3):
      self.hole[i] = self.Block(MountingHole_M4())

    self.leadfree = self.Block(LeadFreeIndicator())
    self.id = self.Block(IdDots4())

  def refinements(self) -> Refinements:
    return super().refinements() + Refinements(
      instance_refinements=[
        (['pwr_5v'], Tps561201),
        (['pwr_3v3'], Ldl1117),
        (['buffer', 'amp'], Mcp6001),
      ]
    )


class DataloggerTestCase(unittest.TestCase):
  def test_design(self) -> None:
    run_test(TestDatalogger)
