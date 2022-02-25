import unittest

from edg import *


class TestDatalogger(BoardTop):
  def contents(self) -> None:
    super().contents()

    self.pwr_conn = self.Block(CalSolPowerConnector())
    self.usb_conn = self.Block(UsbCReceptacle())

    self.usb_forced_current = self.Block(ForcedVoltageCurrentDraw(forced_current_draw=(0, 0.5) * Amp))
    self.connect(self.usb_conn.pwr, self.usb_forced_current.pwr_in)

    self.gnd_merge1 = self.Block(MergedVoltageSource())
    self.connect(self.usb_conn.gnd, self.gnd_merge1.sink1)
    self.connect(self.pwr_conn.gnd, self.gnd_merge1.sink2)
    self.gnd_merge2 = self.Block(MergedVoltageSource())
    self.connect(self.gnd_merge1.source, self.gnd_merge2.sink1)
    # second slow reserved for the RTC battery

    self.pwr_5v_merge = self.Block(MergedVoltageSource())
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

      (self.can, ), self.can_chain = self.chain(self.mcu.new_io(CanControllerPort), imp.Block(CalSolCanBlock()))
      self.can.can.not_connected()

      # TODO need proper support for exported unconnected ports
      self.can_gnd_load = self.Block(VoltageLoad())
      self.connect(self.can.can_gnd, self.can_gnd_load.pwr)
      self.can_pwr_load = self.Block(VoltageLoad())
      self.connect(self.can.can_pwr, self.can_pwr_load.pwr)

      # mcu_i2c = self.mcu.new_io(I2cMaster)  # no devices, ignored for now
      # self.i2c_pullup = imp.Block(I2cPullup())
      # self.connect(self.i2c_pullup.i2c, mcu_i2c)

      sd_spi = self.mcu.new_io(SpiMaster)
      self.sd = imp.Block(SdSocket())
      self.sd_spi_net = self.connect(sd_spi, self.sd.spi)
      self.sd_cs_net = self.connect(self.mcu.new_io(DigitalBidir), self.sd.cs)
      (self.cd_pull, ), self.sd_cd_pull_chain = self.chain(
        self.mcu.new_io(DigitalBidir),
        imp.Block(PullupResistor(4.7 * kOhm(tol=0.05))),
        self.sd.cd)

      xbee_uart = self.mcu.new_io(UartPort)
      self.xbee = imp.Block(Xbee_S3b())
      self.xbee_uart_net = self.connect(xbee_uart, self.xbee.data)
      (self.xbee_assoc, ), _ = self.chain(
        self.xbee.associate,
        imp.Block(IndicatorLed(current_draw=(0.5, 2)*mAmp)))  # XBee DIO current is -2 -> 2 mA

      aux_spi = self.mcu.new_io(SpiMaster)
      self.rtc = imp.Block(Pcf2129())
      self.aux_spi_net = self.connect(aux_spi, self.rtc.spi)
      self.rtc_cs_net = self.connect(self.mcu.new_io(DigitalBidir), self.rtc.cs)
      self.bat = imp.Block(Cr2032())
      self.connect(self.bat.pwr, self.rtc.pwr_bat)
      self.connect(self.bat.gnd, self.gnd_merge2.sink2)

      self.eink = imp.Block(E2154fs091())
      self.connect(aux_spi, self.eink.spi)
      self.eink_busy_net = self.connect(self.mcu.new_io(DigitalBidir), self.eink.busy)
      self.eink_reset_net = self.connect(self.mcu.new_io(DigitalBidir), self.eink.reset)
      self.eink_dc_net = self.connect(self.mcu.new_io(DigitalBidir), self.eink.dc)
      self.eink_cs_net = self.connect(self.mcu.new_io(DigitalBidir), self.eink.cs)

      self.ext = imp.Block(BlueSmirf())
      self.ext_uart_net = self.connect(self.mcu.new_io(UartPort), self.ext.data)
      self.ext_cts_net = self.connect(self.mcu.new_io(DigitalBidir), self.ext.cts)
      self.ext_rts_net = self.connect(self.mcu.new_io(DigitalBidir), self.ext.rts)

      self.rgb1 = imp.Block(IndicatorSinkRgbLed())  # system RGB 1
      self.rgb1_red_net = self.connect(self.mcu.new_io(DigitalBidir), self.rgb1.red)
      self.rgb1_grn_net = self.connect(self.mcu.new_io(DigitalBidir), self.rgb1.green)
      self.rgb1_blue_net = self.connect(self.mcu.new_io(DigitalBidir), self.rgb1.blue)

      self.rgb2 = imp.Block(IndicatorSinkRgbLed())  # sd card RGB
      self.rgb2_red_net = self.connect(self.mcu.new_io(DigitalBidir), self.rgb2.red)
      self.rgb2_grn_net = self.connect(self.mcu.new_io(DigitalBidir), self.rgb2.green)
      self.rgb2_blue_net = self.connect(self.mcu.new_io(DigitalBidir), self.rgb2.blue)

      self.rgb3 = imp.Block(IndicatorSinkRgbLed())
      self.rgb3_red_net = self.connect(self.mcu.new_io(DigitalBidir), self.rgb3.red)
      self.rgb3_grn_net = self.connect(self.mcu.new_io(DigitalBidir), self.rgb3.green)
      self.rgb3_blue_net = self.connect(self.mcu.new_io(DigitalBidir), self.rgb3.blue)

      sw_pull_model = PullupResistor(4.7 * kOhm(tol=0.05))
      (self.sw1, self.sw1_pull), self.sw1_chain = self.chain(imp.Block(DigitalSwitch()),
                                                             imp.Block(sw_pull_model),
                                                             self.mcu.new_io(DigitalBidir))
      (self.sw2, self.sw2_pull), self.sw2_chain = self.chain(imp.Block(DigitalSwitch()),
                                                             imp.Block(sw_pull_model),
                                                             self.mcu.new_io(DigitalBidir))

    with self.implicit_connect(
        ImplicitConnect(self.pwr_3v3.gnd, [Common]),
    ) as imp:
      div_model = VoltageDivider(output_voltage=3 * Volt(tol=0.15), impedance=(100, 1000) * Ohm)
      (self.v12sense, ), self.v12sense_chain = self.chain(self.pwr_conn.pwr, imp.Block(div_model), self.mcu.new_io(AnalogSink))
      (self.v5sense, ), self.v5sense_chain = self.chain(self.pwr_5v.pwr_out, imp.Block(div_model), self.mcu.new_io(AnalogSink))
      (self.vscsense, ), self.vscsense_chain = self.chain(self.buffer.sc_out, imp.Block(div_model), self.mcu.new_io(AnalogSink))

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
      ],
      instance_values=[
        (['mcu', 'pin_assigns'], ';'.join([
          'can_chain_0.txd=51',
          'can_chain_0.rxd=53',
          'sd_spi_net.sck=17',
          'sd_spi_net.mosi=15',
          'sd_spi_net.miso=19',
          'sd_cs_net=11',
          'sd_cd_pull_chain_0=16',
          'xbee_uart_net.tx=58',
          'xbee_uart_net.rx=54',
          'aux_spi_net.sck=5',
          'aux_spi_net.mosi=6',
          'aux_spi_net.miso=7',
          'rtc_cs_net=64',
          'eink_busy_net=1',
          'eink_reset_net=2',
          'eink_dc_net=3',
          'eink_cs_net=4',
          'eink_busy_net=1',
          'ext_uart_net.tx=60',
          'ext_uart_net.rx=61',
          'ext_cts_net=62',
          'ext_rts_net=59',
          'rgb1_red_net=31',
          'rgb1_grn_net=32',
          'rgb1_blue_net=30',
          'rgb2_red_net=28',
          'rgb2_grn_net=29',
          'rgb2_blue_net=25',
          'rgb3_red_net=46',
          'rgb3_grn_net=39',
          'rgb3_blue_net=38',
          'sw1_chain_0=33',
          'sw2_chain_0=23',
          'v12sense_chain_1=10',
          'v5sense_chain_1=9',
          'vscsense_chain_1=8',
        ]))
      ]
    )


class DataloggerTestCase(unittest.TestCase):
  def test_design(self) -> None:
    compile_board_inplace(TestDatalogger)
