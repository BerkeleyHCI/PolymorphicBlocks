import unittest

from edg import *


class EspProgrammerTc2030Inline(Connector, Block):
  """UART connector, follows the TXD, RXD, GND, +5 pinning of cheap CP2102 dongles."""
  @init_in_parent
  def __init__(self, *, pwr_current_draw: RangeLike = (0, 0)*mAmp):
    super().__init__()
    self.conn = self.Block(PinHeader254DualShroudedInline(6))

    self.uart = self.Port(UartPort.empty(), [InOut])
    # note that RX and TX here are from the connected device, so they're flipped from the CP2102's view
    self.connect(self.uart.rx, self.conn.pins.request('4').adapt_to(DigitalSink()))
    self.connect(self.uart.tx, self.conn.pins.request('3').adapt_to(DigitalSource()))
    self.gnd = self.Export(self.conn.pins.request('5').adapt_to(Ground()),
                           [Common])
    self.pwr = self.Export(self.conn.pins.request('1').adapt_to(VoltageSink(
      current_draw=pwr_current_draw
    )), [Power])

    self.en = self.Export(self.conn.pins.request('6').adapt_to(DigitalSink()))  # RTS
    self.boot = self.Export(self.conn.pins.request('2').adapt_to(DigitalSink()))  # CTS


class EspProgrammer(JlcBoardTop):
  """USB UART converter board set up for ESP programming including auto-program circuit."""
  def contents(self) -> None:
    super().contents()
    self.usb_uart = self.Block(UsbCReceptacle())

    self.vusb = self.connect(self.usb_uart.pwr)
    self.gnd = self.connect(self.usb_uart.gnd)

    # 5v DOMAIN
    with self.implicit_connect(
        ImplicitConnect(self.vusb, [Power]),
        ImplicitConnect(self.gnd, [Common]),
    ) as imp:
      self.vusb_protect = imp.Block(ProtectionZenerDiode(voltage=(5.25, 6)*Volt))

      self.usbconv = imp.Block(Cp2102())
      (self.usb_esd, ), self.usb_chain = self.chain(
        self.usb_uart.usb, imp.Block(UsbEsdDiode()), self.usbconv.usb)

      # for target power only
      self.reg_3v3 = imp.Block(LinearRegulator(output_voltage=3.3*Volt(tol=0.05)))
      self.v3v3 = self.connect(self.reg_3v3.pwr_out)

    # 3v3 DOMAIN
    with self.implicit_connect(
        ImplicitConnect(self.v3v3, [Power]),
        ImplicitConnect(self.gnd, [Common]),
    ) as imp:
      self.out = imp.Block(EspProgrammerTc2030Inline())
      self.connect(self.usbconv.uart, self.out.uart)
      self.auto = imp.Block(EspAutoProgram())
      self.connect(self.usbconv.dtr, self.auto.dtr)
      self.connect(self.usbconv.rts, self.auto.rts)
      self.connect(self.auto.en, self.out.en)
      self.connect(self.auto.boot, self.out.boot)

      (self.led, ), _ = self.chain(self.usbconv.suspend, imp.Block(IndicatorSinkLed(Led.White)))
      (self.led_en, ), _ = self.chain(self.usbconv.rts, imp.Block(IndicatorSinkLed(Led.Red)))

  def refinements(self) -> Refinements:
    return super().refinements() + Refinements(
      instance_refinements=[
        (['reg_3v3'], Ap2204k),
      ],
      instance_values=[
        (['refdes_prefix'], 'U'),  # unique refdes for panelization
        (['vusb_protect', 'diode', 'footprint_spec'], 'Diode_SMD:D_SOD-323'),
        # 2.2uF generates a 1206, but 4.7uF allows a 0805
        (['reg_3v3', 'out_cap', 'cap', 'capacitance'], Range.from_tolerance(4.7e-6, 0.2)),
      ],
      class_refinements=[
      ],
      class_values=[
        (SmdStandardPackage, ["smd_min_package"], "0402"),
        (TableBjt, ["footprint_spec"], "Package_TO_SOT_SMD:SOT-323_SC-70")
      ],
    )


class EspProgrammerTestCase(unittest.TestCase):
  def test_design(self) -> None:
    compile_board_inplace(EspProgrammer)
