import unittest

from typing_extensions import override

from edg import *


class Obd2Connector(FootprintBlock):
  """OBD2 dongle-side (not car-side) connector"""
  def __init__(self) -> None:
    super().__init__()
    self.gnd = self.Port(Ground())
    self.pwr = self.Port(VoltageSource(voltage_out=(10, 25)*Volt))

    self.can = self.Port(CanDiffPort())

  @override
  def contents(self) -> None:
    super().contents()
    self.footprint(
      'U', 'project:J1962',
      {
        '6': self.can.canh,
        '14': self.can.canl,
        '5': self.gnd,  # note, 4 is chassis gnd
        '16': self.pwr,  # battery voltage
      },
    )


class CanAdapter(JlcBoardTop):
  @override
  def contents(self) -> None:
    super().contents()

    self.obd = self.Block(Obd2Connector())
    self.gnd = self.connect(self.obd.gnd)

    with self.implicit_connect(
        ImplicitConnect(self.gnd, [Common]),
    ) as imp:
      (self.ferrite, self.reg_3v3, self.prot_3v3), _ = self.chain(
        self.obd.pwr,
        self.Block(SeriesPowerFerriteBead()),
        imp.Block(VoltageRegulator(output_voltage=3.3*Volt(tol=0.05))),
        imp.Block(ProtectionZenerDiode(voltage=(3.45, 3.9)*Volt))
      )
      self.vobd = self.connect(self.ferrite.pwr_out)
      self.v3v3 = self.connect(self.reg_3v3.pwr_out)

    with self.implicit_connect(
        ImplicitConnect(self.v3v3, [Power]),
        ImplicitConnect(self.gnd, [Common]),
    ) as imp:
      self.mcu = imp.Block(IoController())
      self.mcu.with_mixin(IoControllerWifi())

      self.can = imp.Block(CanTransceiver())
      self.connect(self.can.can, self.obd.can)
      self.connect(self.can.controller, self.mcu.with_mixin(IoControllerCan()).can.request('can'))

      # debugging LEDs
      (self.ledr, ), _ = self.chain(imp.Block(IndicatorSinkLed(Led.Red)), self.mcu.gpio.request('ledr'))
      (self.ledg, ), _ = self.chain(imp.Block(IndicatorLed(Led.Green)), self.mcu.gpio.request('ledg'))
      (self.ledw, ), _ = self.chain(imp.Block(IndicatorLed(Led.White)), self.mcu.gpio.request('ledw'))

      (self.vobd_sense, ), _ = self.chain(
        self.vobd,
        imp.Block(VoltageSenseDivider(full_scale_voltage=2.2*Volt(tol=0.1), impedance=(1, 10)*kOhm)),
        self.mcu.adc.request('vobd_sense')
      )

  @override
  def refinements(self) -> Refinements:
    return super().refinements() + Refinements(
      instance_refinements=[
        (['mcu'], Esp32c3_Wroom02),
        (['reg_3v3'], Tps54202h),
      ],
      instance_values=[
        (['refdes_prefix'], 'O'),  # unique refdes for panelization
        (['mcu', 'pin_assigns'], [
          'ledr=_GPIO9_STRAP',  # force using the strapping / boot mode pin
          'ledg=13',
          'ledw=14',
          'can.txd=6',
          'can.rxd=5',
          'vobd_sense=3',  # 4 as sent to fabrication before ADC2 removed from model, blue-wire to 3

        ]),
        (['mcu', 'programming'], 'uart-auto'),
        (['reg_3v3', 'power_path', 'inductor', 'manual_frequency_rating'], Range(0, 9e6)),
        (['reg_3v3', 'power_path', 'in_cap', 'cap', 'voltage_rating_derating'], 1.0),
        (['reg_3v3', 'power_path', 'inductor', 'footprint_spec'], "Inductor_SMD:L_1210_3225Metric")
      ],
      class_refinements=[
        (EspProgrammingHeader, EspProgrammingTc2030),
        (TagConnect, TagConnectNonLegged),
        (CanTransceiver, Sn65hvd230),
        (TestPoint, CompactKeystone5015),
      ],
      class_values=[
        (CompactKeystone5015, ['lcsc_part'], 'C5199798'),
      ]
    )


class CanAdapterTestCase(unittest.TestCase):
  def test_design(self) -> None:
    compile_board_inplace(CanAdapter)
