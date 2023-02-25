import unittest

from edg import *
from .test_high_switch import CalSolPowerConnector, CalSolCanBlock, CanFuse


class TestDatalogger(BoardTop):
  def contents(self) -> None:
    super().contents()

    self.pwr_conn = self.Block(CalSolPowerConnector())
    self.usb_conn = self.Block(UsbCReceptacle())

    self.usb_forced_current = self.Block(ForcedVoltageCurrentDraw(forced_current_draw=(0, 0.5) * Amp))
    self.connect(self.usb_conn.pwr, self.usb_forced_current.pwr_in)

    self.bat = self.Block(Cr2032())

    self.gnd_merge = self.Block(MergedVoltageSource()).connected_from(
      self.usb_conn.gnd, self.pwr_conn.gnd, self.bat.gnd)
    self.gnd = self.connect(self.gnd_merge.pwr_out)

    with self.implicit_connect(
        ImplicitConnect(self.gnd, [Common]),
    ) as imp:
      (self.pwr_5v,), _ = self.chain(
        self.pwr_conn.pwr,
        imp.Block(BuckConverter(output_voltage=(4.85, 5.4)*Volt))
      )
      self.pwr_5v_merge = self.Block(MergedVoltageSource()).connected_from(
        self.usb_forced_current.pwr_out, self.pwr_5v.pwr_out)

      (self.buffer, self.pwr_3v3), _ = self.chain(
        self.pwr_5v_merge.pwr_out,
        imp.Block(BufferedSupply(charging_current=(0.4, 0.5)*Amp, sense_resistance=0.47*Ohm(tol=0.01),
                                 voltage_drop=(0, 0.4)*Volt)),
        imp.Block(LinearRegulator(output_voltage=3.3*Volt(tol=0.05)))
      )

    self.outline = self.Block(Outline_Pn1332())
    self.duck = self.Block(DuckLogo())

    self.vin = self.connect(self.pwr_conn.pwr)
    self.v5 = self.connect(self.pwr_5v_merge.pwr_out)
    self.v5_buffered = self.connect(self.buffer.pwr_out)
    self.v3v3 = self.connect(self.pwr_3v3.pwr_out)  # TODO better auto net names

    with self.implicit_connect(
      ImplicitConnect(self.v3v3, [Power]),
      ImplicitConnect(self.gnd, [Common]),
    ) as imp:
      self.mcu = imp.Block(IoController())

      self.connect(self.mcu.usb.request(), self.usb_conn.usb)

      (self.can, ), _ = self.chain(self.mcu.can.request('can'), imp.Block(CalSolCanBlock()))

      # TODO need proper support for exported unconnected ports
      self.can_gnd_load = self.Block(VoltageLoad())
      self.connect(self.can.can_gnd, self.can_gnd_load.pwr)
      self.can_pwr_load = self.Block(VoltageLoad())
      self.connect(self.can.can_pwr, self.can_pwr_load.pwr)

      # mcu_i2c = self.mcu.i2c.request()  # no devices, ignored for now
      # self.i2c_pullup = imp.Block(I2cPullup())
      # self.connect(self.i2c_pullup.i2c, mcu_i2c)

      self.sd = imp.Block(SdSocket())
      self.connect(self.mcu.spi.request('sd_spi'), self.sd.spi)
      self.connect(self.mcu.gpio.request('sd_cs'), self.sd.cs)
      (self.cd_pull, ), _ = self.chain(
        self.mcu.gpio.request('sd_cd_pull'),
        imp.Block(PullupResistor(4.7 * kOhm(tol=0.05))),
        self.sd.cd)

      self.xbee = imp.Block(Xbee_S3b())
      self.connect(self.mcu.uart.request('xbee_uart'), self.xbee.data)
      (self.xbee_assoc, ), _ = self.chain(
        self.xbee.associate,
        imp.Block(IndicatorLed(current_draw=(0.5, 2)*mAmp)))  # XBee DIO current is -2 -> 2 mA

      aux_spi = self.mcu.spi.request('aux_spi')
      self.rtc = imp.Block(Pcf2129())
      self.connect(aux_spi, self.rtc.spi)
      self.connect(self.mcu.gpio.request('rtc_cs'), self.rtc.cs)
      self.connect(self.bat.pwr, self.rtc.pwr_bat)

      self.eink = imp.Block(E2154fs091())
      self.connect(aux_spi, self.eink.spi)
      self.connect(self.mcu.gpio.request('eink_busy'), self.eink.busy)
      self.connect(self.mcu.gpio.request('eink_reset'), self.eink.reset)
      self.connect(self.mcu.gpio.request('eink_dc'), self.eink.dc)
      self.connect(self.mcu.gpio.request('eink_cs'), self.eink.cs)

      self.ext = imp.Block(BlueSmirf())
      self.connect(self.mcu.uart.request('ext_uart'), self.ext.data)
      self.connect(self.mcu.gpio.request('ext_cts'), self.ext.cts)
      self.connect(self.mcu.gpio.request('ext_rts'), self.ext.rts)

      self.rgb1 = imp.Block(IndicatorSinkRgbLed())  # system RGB 1
      self.connect(self.mcu.gpio.request_vector('rgb1'), self.rgb1.signals)

      self.rgb2 = imp.Block(IndicatorSinkRgbLed())  # sd card RGB
      self.connect(self.mcu.gpio.request_vector('rgb2'), self.rgb2.signals)

      self.rgb3 = imp.Block(IndicatorSinkRgbLed())
      self.connect(self.mcu.gpio.request_vector('rgb3'), self.rgb3.signals)

      sw_pull_model = PullupResistor(4.7 * kOhm(tol=0.05))
      (self.sw1, self.sw1_pull), _ = self.chain(imp.Block(DigitalSwitch()),
                                                imp.Block(sw_pull_model),
                                                self.mcu.gpio.request('sw1'))
      (self.sw2, self.sw2_pull), _ = self.chain(imp.Block(DigitalSwitch()),
                                                imp.Block(sw_pull_model),
                                                self.mcu.gpio.request('sw2'))

    with self.implicit_connect(
        ImplicitConnect(self.gnd, [Common]),
    ) as imp:
      # TODO update to use VoltageSenseDivider
      div_model = VoltageDivider(output_voltage=3 * Volt(tol=0.15), impedance=(100, 1000) * Ohm)
      (self.v12sense, ), _ = self.chain(self.vin, imp.Block(div_model), self.mcu.adc.request('v12sense'))
      (self.v5sense, ), _ = self.chain(self.v5, imp.Block(div_model), self.mcu.adc.request('v5sense'))
      (self.vscsense, ), _ = self.chain(self.buffer.sc_out, imp.Block(div_model), self.mcu.adc.request('vscsense'))

    self.hole = ElementDict[MountingHole]()
    for i in range(3):
      self.hole[i] = self.Block(MountingHole_M4())

    self.leadfree = self.Block(LeadFreeIndicator())
    self.id = self.Block(IdDots4())

  def refinements(self) -> Refinements:
    return super().refinements() + Refinements(
      instance_refinements=[
        (['mcu'], Lpc1549_64),
        (['pwr_5v'], Tps561201),
        (['pwr_3v3'], Ldl1117),
        (['buffer', 'amp'], Mcp6001),
      ],
      instance_values=[
        (['mcu', 'pin_assigns'], [
          'can.txd=51',
          'can.rxd=53',
          'sd_spi.sck=17',
          'sd_spi.mosi=15',
          'sd_spi.miso=19',
          'sd_cs=11',
          'sd_cd_pull=16',
          'xbee_uart.tx=58',
          'xbee_uart.rx=50',  # used to be 54, which is ISP_0
          'aux_spi.sck=5',
          'aux_spi.mosi=6',
          'aux_spi.miso=7',
          'rtc_cs=64',
          'eink_busy=1',
          'eink_reset=2',
          'eink_dc=3',
          'eink_cs=4',
          'eink_busy=1',
          'ext_uart.tx=60',
          'ext_uart.rx=61',
          'ext_cts=62',
          'ext_rts=59',
          'rgb1_red=31',
          'rgb1_green=32',
          'rgb1_blue=30',
          'rgb2_red=28',
          'rgb2_green=29',
          'rgb2_blue=25',
          'rgb3_red=46',
          'rgb3_green=39',
          'rgb3_blue=34',  # used to be 38, which is ISP_1
          'sw1=33',
          'sw2=23',
          'v12sense=10',
          'v5sense=9',
          'vscsense=8',
        ]),
        (['mcu', 'swd_swo_pin'], 'PIO0_8'),

        (['pwr_5v', 'power_path', 'inductor_current_ripple'], Range(0.01, 0.6)),  # trade higher Imax for lower L
        # the hold current wasn't modeled at the time of manufacture and turns out to be out of limits
        (['can', 'can_fuse', 'fuse', 'actual_hold_current'], Range(0.1, 0.1)),
        # JLC does not have frequency specs, must be checked TODO
        (['pwr_5v', 'power_path', 'inductor', 'ignore_frequency'], True),
        (['eink', 'boost_ind', 'ignore_frequency'], True),
        # JLC does not have gate voltage tolerance specs, and the inferred one is low
        (['eink', 'boost_sw', 'gate_voltage'], Range(3, 10)),

        # keep netlist footprints as libraries change
        (['buffer', 'fet', 'footprint_spec'], 'Package_TO_SOT_SMD:SOT-223-3_TabPin2'),
      ],
      class_refinements=[
        (PptcFuse, CanFuse)
      ],
    )


class DataloggerTestCase(unittest.TestCase):
  def test_design(self) -> None:
    compile_board_inplace(TestDatalogger)
