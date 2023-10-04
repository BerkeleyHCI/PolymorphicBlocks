import unittest

from edg import *


class JacdacKeyswitch(JacdacDeviceTop, JlcBoardTop):
  """A Jacdac socketed mechanical keyswitch with RGB, for the gamer-maker in all of us.
  """
  def contents(self) -> None:
    super().contents()

    self.edge2 = self.create_edge()

    # TODO should connect to the nets, once .connected can take a Connection
    self.tp_jd_pwr = self.Block(VoltageTestPoint()).connected(self.edge2.jd_pwr_sink)
    self.tp_gnd = self.Block(VoltageTestPoint()).connected(self.edge2.gnd_sink)

    # POWER
    with self.implicit_connect(
            ImplicitConnect(self.gnd, [Common]),
    ) as imp:
      (self.reg_3v3, self.tp_3v3), _ = self.chain(
        self.jd_pwr,
        imp.Block(LinearRegulator(output_voltage=3.3*Volt(tol=0.05))),
        self.Block(VoltageTestPoint()),
      )
      self.v3v3 = self.connect(self.reg_3v3.pwr_out)

    # 3V3 DOMAIN
    with self.implicit_connect(
            ImplicitConnect(self.v3v3, [Power]),
            ImplicitConnect(self.gnd, [Common]),
    ) as imp:
      self.mcu = imp.Block(IoController())

      (self.sw, ), _ = self.chain(imp.Block(DigitalSwitch()), self.mcu.gpio.request('sw'))
      (self.rgb, ), _ = self.chain(imp.Block(IndicatorSinkRgbLed()), self.mcu.gpio.request_vector('rgb'))

      (self.jd_if, ), _ = self.chain(self.mcu.gpio.request('jd_data'),
                                     imp.Block(JacdacDataInterface()),
                                     self.jd_data)

      self.connect(self.mcu.gpio.request('jd_status'), self.jd_status)


  def refinements(self) -> Refinements:
    return super().refinements() + Refinements(
      instance_refinements=[
        (['mcu'], Stm32g031_G),
        (['reg_3v3'], Xc6209),  # up to 10V input, more robust in case of transients
      ],
      class_refinements=[
        (TvsDiode, Rclamp0521p),
        (Switch, KailhSocket),
        (SwdCortexTargetHeader, SwdCortexTargetTagConnect),
        (TagConnect, TagConnectNonLegged),
      ],
      instance_values=[
        (['mcu', 'pin_assigns'], [
          # pinning based on https://github.com/microsoft/jacdac-ddk/blob/main/electronics/altium/module-designs/JacdacDevRgbEc30%20117-1.0/PDF/JacdacDevRgbEc30%20117-1.0%20schematic.PDF
          'jd_data=PB6',  # PB3/4/5/6 on reference design
          'jd_status=PC14',

          'rgb_blue=15',
          'rgb_red=16',
          'rgb_green=17',

          'sw=19',
        ]),
        (['edge', 'status_led', 'color'], 'yellow'),  # NONSTANDARD, but uses a JLC basic part
        (['edge2', 'status_led', 'color'], 'yellow'),
      ],
      class_values=[
        (Diode, ['footprint_spec'], 'Diode_SMD:D_SOD-323'),
      ]
    )


class JacdacKeyswitchTestCase(unittest.TestCase):
  def test_design(self) -> None:
    compile_board_inplace(JacdacKeyswitch)
