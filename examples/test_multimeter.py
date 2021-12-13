import unittest
from typing import cast

from electronics_abstract_parts.ESeriesUtil import ESeriesRatioUtil
from electronics_abstract_parts.ResistiveDivider import DividerValues
from edg import *



class MultimeterTest(BoardTop):
  def contents(self) -> None:
    super().contents()

    self.bat = self.Block(AABattery())

    # Data-only USB port, for example to connect to a computer that can't source USB PD
    # so the PD port can be connected to a dedicated power brick.
    self.data_usb = self.Block(UsbCReceptacle())

    self.gnd_merge = self.Block(MergedVoltageSource())
    self.connect(self.bat.gnd, self.gnd_merge.sink1)
    self.connect(self.data_usb.gnd, self.gnd_merge.sink2)

    self.gnd = self.connect(self.gnd_merge.source)
    self.vbat = self.connect(self.bat.pwr)

    with self.implicit_connect(
        ImplicitConnect(self.gnd_merge.source, [Common]),
    ) as imp:
      (self.reg_5v, self.reg_3v3, self.led_3v3), _ = self.chain(
        self.bat.pwr,
        imp.Block(BoostConverter(output_voltage=5.0*Volt(tol=0.1))),
        imp.Block(LinearRegulator(output_voltage=3.3*Volt(tol=0.05))),
        imp.Block(VoltageIndicatorLed())
      )
      self.v3v3 = self.connect(self.reg_3v3.pwr_out)

      (self.ref_div, self.ref_buf), _ = self.chain(
        self.reg_3v3.pwr_out,
        imp.Block(VoltageDivider(output_voltage=1.62*Volt(tol=0.05), impedance=(10, 100)*kOhm)),
        imp.Block(OpampFollower())
      )
      self.connect(self.reg_3v3.pwr_out, self.ref_buf.pwr)
      self.vcenter = self.connect(self.ref_buf.output)

    with self.implicit_connect(
        ImplicitConnect(self.reg_3v3.pwr_out, [Power]),
        ImplicitConnect(self.reg_3v3.gnd, [Common]),
    ) as imp:
      self.prot_3v3 = imp.Block(ProtectionZenerDiode(voltage=(3.45, 3.75)*Volt))

      self.mcu = imp.Block(Holyiot_18010_Nrf52840())
      (self.swd, ), _ = self.chain(imp.Block(SwdCortexTargetWithTdiConnector()), self.mcu.swd)

      (self.usb_esd, ), _ = self.chain(self.data_usb.usb, imp.Block(UsbEsdDiode()), self.mcu.usb_0)

      self.rgb = imp.Block(IndicatorSinkRgbLed())
      self.rgb_r_net = self.connect(self.mcu.new_io(DigitalBidir), self.rgb.red)
      self.rgb_g_net = self.connect(self.mcu.new_io(DigitalBidir), self.rgb.green)
      self.rgb_b_net = self.connect(self.mcu.new_io(DigitalBidir), self.rgb.blue)

      (self.sw1, ), self.sw1_chain = self.chain(imp.Block(DigitalSwitch()), self.mcu.new_io(DigitalBidir))
      (self.sw2, ), self.sw2_chain = self.chain(imp.Block(DigitalSwitch()), self.mcu.new_io(DigitalBidir))
      (self.sw3, ), self.sw3_chain = self.chain(imp.Block(DigitalSwitch()), self.mcu.new_io(DigitalBidir))
      # TODO next revision: proper navigation switch

      shared_spi = self.mcu.new_io(SpiMaster)
      self.spi_net = self.connect(shared_spi)

      self.lcd = imp.Block(Qt096t_if09())
      self.connect(self.reg_3v3.pwr_out.as_digital_source(), self.lcd.led)
      self.lcd_reset_net = self.connect(self.mcu.new_io(DigitalBidir), self.lcd.reset)
      self.lcd_rs_net = self.connect(self.mcu.new_io(DigitalBidir), self.lcd.rs)
      self.connect(shared_spi, self.lcd.spi)  # MISO unused
      self.lcd_cs_net = self.connect(self.mcu.new_io(DigitalBidir), self.lcd.cs)


    self.inn = self.Block(BananaSafetyJack())
    # self.connect(self.outn.port.as_voltage_sink(), self.gnd_merge.source)
    self.inp = self.Block(BananaSafetyJack())
    # self.connect(self.outp.port.as_voltage_sink(), self.control.out)

    # Misc board
    self.duck = self.Block(DuckLogo())
    self.leadfree = self.Block(LeadFreeIndicator())
    self.id = self.Block(IdDots4())

    self.jlc_th1 = self.Block(JlcToolingHole())
    self.jlc_th2 = self.Block(JlcToolingHole())
    self.jlc_th3 = self.Block(JlcToolingHole())

  def refinements(self) -> Refinements:
    return super().refinements() + Refinements(
      instance_refinements=[
        (['reg_5v'], Tps61023),
        (['reg_3v3'], Xc6209),
      ],
      instance_values=[
        (['mcu', 'pin_assigns'], ';'.join([

        ])),
        # allow the regulator to go into tracking mode
        (['reg_5v', 'dutycycle_limit'], Range(0, float('inf'))),

      ],
      class_refinements=[
        (SwdCortexTargetWithTdiConnector, SwdCortexTargetTc2050),
        (Opamp, Tlv9061),  # higher precision opamps
        (BananaSafetyJack, Fcr7350),
        (Capacitor, JlcCapacitor),
        (Resistor, JlcResistor),
      ],
    )


class MultimeterTestCase(unittest.TestCase):
  def test_design(self) -> None:
    compile_board_inplace(MultimeterTest)
