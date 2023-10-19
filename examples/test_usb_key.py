import unittest

from edg import *


class StTscSenseChannel(Block):
  """Sense channel for STM micros' TSC peripheral."""
  def __init__(self):
    super().__init__()
    self.io = self.Port(DigitalBidir.empty(), [Input])

  def contents(self):
    super().contents()
    self.res = self.Block(Resistor(resistance=10*kOhm(tol=0.05)))  # recommended by ST
    self.connect(self.io, self.res.a.adapt_to(DigitalBidir()))  # ideal
    self.load = self.Block(DummyPassive())  # avoid ERC
    self.connect(self.res.b, self.load.io)


class StTscReference(Block):
  """Reference capacitor for STM micros' TSC peripheral."""
  def __init__(self):
    super().__init__()
    self.gnd = self.Port(Ground.empty(), [Common])
    self.io = self.Port(DigitalBidir.empty(), [Input])

  def contents(self):
    super().contents()
    self.cap = self.Block(Capacitor(10*nFarad(tol=0.2), voltage=self.io.link().voltage))
    self.connect(self.cap.pos.adapt_to(DigitalBidir()), self.io)
    self.connect(self.cap.neg.adapt_to(Ground()), self.gnd)


class UsbKey(JlcBoardTop):
  """USB dongle with the PCB as the USB-A contact surface and a microcontroller on the opposite side.
  Similar circuitry and same pinning as the Solokeys Somu: https://github.com/solokeys/solo-hw/tree/master/solo
  """
  def contents(self) -> None:
    super().contents()

    self.usb = self.Block(UsbAPlugPads())

    self.gnd = self.connect(self.usb.gnd)

    # POWER
    with self.implicit_connect(
            ImplicitConnect(self.gnd, [Common]),
    ) as imp:
      (self.reg_3v3, ), _ = self.chain(
        self.usb.pwr,
        imp.Block(LinearRegulator(output_voltage=3.3*Volt(tol=0.05))),
      )
      self.v3v3 = self.connect(self.reg_3v3.pwr_out)

    # 3V3 DOMAIN
    with self.implicit_connect(
            ImplicitConnect(self.v3v3, [Power]),
            ImplicitConnect(self.gnd, [Common]),
    ) as imp:
      self.mcu = imp.Block(IoController())

      self.connect(self.mcu.usb.request('usb'), self.usb.usb)

      (self.rgb, ), _ = self.chain(imp.Block(IndicatorSinkRgbLed()), self.mcu.gpio.request_vector('rgb'))

      (self.ts1, ), _ = self.chain(self.mcu.gpio.request('touch1'), imp.Block(StTscSenseChannel()))
      (self.ts2, ), _ = self.chain(self.mcu.gpio.request('touch2'), imp.Block(StTscSenseChannel()))
      (self.tss, ), _ = self.chain(self.mcu.gpio.request('ref'), imp.Block(StTscReference()))

      self.connect(self.mcu.gpio.request('b1_gnd'), self.mcu.gpio.request('c15_gnd'), self.usb.gnd.as_digital_source())

  def multipack(self) -> None:
    self.packed_mcu_vdda_cap = self.PackedBlock(CombinedCapacitor())
    self.pack(self.packed_mcu_vdda_cap.elements.request('0'), ['mcu', 'vdda_cap0', 'cap'])
    self.pack(self.packed_mcu_vdda_cap.elements.request('1'), ['mcu', 'vdda_cap1', 'cap'])
    self.pack(self.packed_mcu_vdda_cap.elements.request('2'), ['mcu', 'vdd_cap[0]', 'cap'])

    self.packed_mcu_vdd1_cap = self.PackedBlock(CombinedCapacitor(extend_upper=True))
    self.pack(self.packed_mcu_vdd1_cap.elements.request('0'), ['reg_3v3', 'out_cap', 'cap'])
    self.pack(self.packed_mcu_vdd1_cap.elements.request('1'), ['mcu', 'vdd_cap_bulk', 'cap'])
    self.pack(self.packed_mcu_vdd1_cap.elements.request('2'), ['mcu', 'vdd_cap[1]', 'cap'])

  def refinements(self) -> Refinements:
    return super().refinements() + Refinements(
      instance_refinements=[
        (['mcu'], Stm32l432k),
        (['reg_3v3'], Lp5907),
      ],
      class_refinements=[
        (RgbLedCommonAnode, Smt0404RgbLed),
        (SwdCortexTargetHeader, SwdCortexTargetTagConnect),
        (TagConnect, TagConnectNonLegged),
      ],
      instance_values=[
        (['mcu', 'pin_assigns'], [
          'touch1=PB4',
          'touch2=PB5',
          'ref=PB6',

          'rgb_red=PA1',
          'rgb_green=PA2',
          'rgb_blue=PA3',

          # these are hard-tied in the reference and used to help routing here
          'b1_gnd=PB1',
          'c15_gnd=PC15',
        ]),
        (['mcu', 'swd_connect_reset'], False),
        (['packed_mcu_vdd1_cap', 'cap', 'capacitance_minimum_size'], False),
      ],
      class_values=[
        (Diode, ['footprint_spec'], 'Diode_SMD:D_SOD-323'),
        (SmdStandardPackage, ["smd_min_package"], '0402'),
        (Lp5907, ['ic', 'footprint_spec'], 'Package_DFN_QFN:UDFN-4-1EP_1x1mm_P0.65mm_EP0.48x0.48mm'),
      ]
    )


class UsbKeyTestCase(unittest.TestCase):
  def test_design(self) -> None:
    compile_board_inplace(UsbKey)
