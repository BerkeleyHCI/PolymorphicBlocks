# As the first solar car board, the solar car specific libraries have been moved here.
# Most of these are parts and subcircuits specific to Tachyon-era electronics and
# are no longer used on newer cars.
# These are no longer maintained, only seeing incremental changes to keep examples building,
# as long as these examples continue being unit tests.
# These are not part of the main libraries to avoid these being indexed, since these
# are not likely to be generally useful and may reference parts and footprints
# that are not widely available.

import unittest

from edg import *


class CalSolCanBlock(Block):
  def __init__(self) -> None:
    super().__init__()

    self.pwr = self.Port(VoltageSink.empty(), [Power])
    self.gnd = self.Port(Ground.empty(), [Common])

    self.can_pwr = self.Port(VoltageSource.empty(), optional=True)
    self.can_gnd = self.Port(GroundSource.empty(), optional=True)

    self.controller = self.Port(CanTransceiverPort.empty(), [Input])
    self.can = self.Port(CanDiffPort.empty(), optional=True)

  def contents(self):
    super().contents()

    self.conn = self.Block(CalSolCanConnector())
    self.connect(self.can, self.conn.differential)

    self.can_fuse = self.Block(SeriesPowerPptcFuse(150 * mAmp(tol=0.1)))
    self.connect(self.conn.pwr, self.can_pwr, self.can_fuse.pwr_in)
    self.connect(self.conn.gnd, self.can_gnd)

    with self.implicit_connect(
        ImplicitConnect(self.can_fuse.pwr_out, [Power]),
        ImplicitConnect(self.can_gnd, [Common]),
    ) as imp:
      self.reg = imp.Block(Ap2204k(5*Volt(tol=0.05)))  # TODO: replace with generic LinearRegulator?

      self.esd = imp.Block(CanEsdDiode())
      self.connect(self.esd.can, self.can)

    with self.implicit_connect(  # Logic-side implicit
        ImplicitConnect(self.pwr, [Power]),
        ImplicitConnect(self.gnd, [Common]),
    ) as imp:
      self.transceiver = imp.Block(Iso1050dub())
      self.connect(self.transceiver.controller, self.controller)
      self.connect(self.transceiver.can, self.can)
      self.connect(self.transceiver.can_pwr, self.reg.pwr_out)
      self.connect(self.transceiver.can_gnd, self.can_gnd)


class CanFuse(PptcFuse, FootprintBlock):
  def __init__(self, trip_current: RangeLike = (100, 200)*mAmp):
    super().__init__(trip_current)

  def contents(self):
    super().contents()

    self.assign(self.actual_trip_current, 150*mAmp(tol=0))
    self.assign(self.actual_hold_current, 50*mAmp(tol=0))
    self.assign(self.actual_voltage_rating, (0, 15)*Volt)

    self.footprint(
      'F', 'Resistor_SMD:R_0603_1608Metric',
      {
        '1': self.a,
        '2': self.b,
      },
      part='0ZCM0005FF2G'
    )


class CalSolPowerConnector(Connector, FootprintBlock):
  def __init__(self) -> None:
    super().__init__()

    self.pwr = self.Port(VoltageSource(
      voltage_out=12 * Volt(tol=0.1),
      current_limits=(0, 3) * Amp  # TODO get actual limits from LVPDB?
    ))
    self.gnd = self.Port(GroundSource())

  def contents(self):
    super().contents()

    self.footprint(
      'J', 'calisco:Molex_DuraClik_vert_3pin',
      {
        '1': self.gnd,
        '2': self.pwr,
        '3': self.gnd,
      },
      mfr='Molex', part='5600200320'
    )


class CalSolCanConnector(Connector, FootprintBlock):
  def __init__(self) -> None:
    super().__init__()

    self.pwr = self.Port(VoltageSource(
      voltage_out=(7, 14) * Volt,  # TODO get limits from CAN power brick?
      current_limits=(0, 0.15) * Amp  # TODO get actual limits from ???
    ))
    self.gnd = self.Port(GroundSource())
    self.differential = self.Port(CanDiffPort(), [Output])

  def contents(self):
    super().contents()

    self.footprint(
      'J', 'calisco:Molex_DuraClik_vert_5pin',
      {
        # 1 is SHLD
        '2': self.pwr,
        '3': self.gnd,
        '4': self.differential.canh,
        '5': self.differential.canl,
      },
      mfr='Molex', part='5600200520'
    )


class CalSolCanConnectorRa(Connector, FootprintBlock):
  def __init__(self) -> None:
    super().__init__()

    self.pwr = self.Port(VoltageSource(
      voltage_out=(7, 14) * Volt,  # TODO get limits from CAN power brick?
      current_limits=(0, 0.15) * Amp  # TODO get actual limits from ???
    ))
    self.gnd = self.Port(GroundSource())
    self.differential = self.Port(CanDiffPort(), [Output])

  def contents(self):
    super().contents()

    self.footprint(
      'J', 'calisco:Molex_DuraClik_502352_1x05_P2.00mm_Horizontal',
      {
        # 1 is SHLD
        '2': self.pwr,
        '3': self.gnd,
        '4': self.differential.canh,
        '5': self.differential.canl,
      },
      mfr='Molex', part='5023520500'
    )


class M12CanConnector(Connector, FootprintBlock):
  def __init__(self) -> None:
    super().__init__()

    self.pwr = self.Port(VoltageSource(
      voltage_out=(7, 14) * Volt,  # TODO get limits from CAN power brick?
      current_limits=(0, 0.15) * Amp  # TODO get actual limits from ???
    ))
    self.gnd = self.Port(GroundSource())
    self.differential = self.Port(CanDiffPort(), [Output])

  def contents(self):
    super().contents()

    self.footprint(
      'J', 'calisco:PhoenixContact_M12-5_Pin_SACC-DSIV-MS-5CON-L90',
      {
        # 1 is SHLD
        '2': self.pwr,
        '3': self.gnd,
        '4': self.differential.canh,
        '5': self.differential.canl,
      },
      mfr='Phoenix Contact', part='SACC-DSIV-MS-5CON-L90'
    )


class LightsConnector(Connector, FootprintBlock):
  @init_in_parent
  def __init__(self, current_draw: RangeLike = RangeExpr()) -> None:
    super().__init__()

    self.pwr = self.Port(VoltageSink(), [Power])  # unused, doesn't draw anything
    self.gnd = self.Port(Ground(), [Common])
    self.out = ElementDict[DigitalSink]()
    for i in range(2):
      self.out[i] = self.Port(DigitalSink(current_draw=current_draw))

  def contents(self):
    super().contents()

    self.footprint(
      'J', 'calisco:Molex_DuraClik_vert_4pin',
      {
        '1': self.pwr,
        '2': self.out[0],
        '3': self.out[1],
        '4': self.gnd,
      },
      mfr='Molex', part='5600200420'
    )


class LightsDriver(Block):
  @init_in_parent
  def __init__(self, current_draw: RangeLike = RangeExpr()) -> None:
    super().__init__()

    self.current_draw = current_draw

    self.pwr = self.Port(VoltageSink.empty(), [Power])
    self.gnd = self.Port(Ground.empty(), [Common])

    self.control = ElementDict[DigitalSink]()

    for i in range(2):
      self.control[i] = self.Port(DigitalSink.empty())

  def contents(self) -> None:
    super().contents()

    with self.implicit_connect(
        ImplicitConnect(self.pwr, [Power]),
        ImplicitConnect(self.gnd, [Common]),
    ) as imp:
      self.conn = imp.Block(LightsConnector(current_draw=self.current_draw))
      self.drv = ElementDict[Block]()

      for i in range(2):
        driver = self.drv[i] = imp.Block(HighSideSwitch(frequency=(0.1, 10) * kHertz))
        self.connect(self.control[i], driver.control)
        self.connect(driver.output, self.conn.out[i])


class HighSwitch(BoardTop):
  def contents(self) -> None:
    super().contents()

    self.pwr_conn = self.Block(CalSolPowerConnector())

    self.vin = self.connect(self.pwr_conn.pwr)
    self.gnd = self.connect(self.pwr_conn.gnd)

    with self.implicit_connect(
        ImplicitConnect(self.gnd, [Common]),
    ) as imp:
      (self.pwr, ), _ = self.chain(
        self.vin,
        imp.Block(Tps561201(output_voltage=3.3*Volt(tol=0.05))))

    self.v3v3 = self.connect(self.pwr.pwr_out)

    self.outline = self.Block(Outline_Pn1332())
    self.duck = self.Block(DuckLogo())

    with self.implicit_connect(
      ImplicitConnect(self.v3v3, [Power]),
      ImplicitConnect(self.gnd, [Common]),
    ) as imp:
      self.mcu = imp.Block(IoController())

      (self.can, ), self.can_chain = self.chain(self.mcu.can.request('can'), imp.Block(CalSolCanBlock()))

      # TODO need proper support for exported unconnected ports
      self.can_gnd_load = self.Block(DummyVoltageSink())
      self.connect(self.can.can_gnd, self.can_gnd_load.pwr)
      self.can_pwr_load = self.Block(DummyVoltageSink())
      self.connect(self.can.can_pwr, self.can_pwr_load.pwr)

      (self.vsense, ), _ = self.chain(  # TODO update to use VoltageSenseDivider
        self.vin,
        imp.Block(VoltageDivider(output_voltage=3 * Volt(tol=0.15), impedance=(100, 1000) * Ohm)),
        self.mcu.adc.request('vsense'))

      self.rgb1 = imp.Block(IndicatorSinkRgbLed())  # CAN RGB
      self.connect(self.mcu.gpio.request_vector('rgb1'), self.rgb1.signals)

      self.rgb2 = imp.Block(IndicatorSinkRgbLed())  # system RGB 2
      self.connect(self.mcu.gpio.request_vector('rgb2'), self.rgb2.signals)

    self.limit_light_current = self.Block(ForcedVoltageCurrentDraw((0, 2.5) * Amp))
    self.connect(self.vin, self.limit_light_current.pwr_in)
    with self.implicit_connect(
        ImplicitConnect(self.limit_light_current.pwr_out, [Power]),
        ImplicitConnect(self.gnd, [Common]),
    ) as imp:
      self.light = ElementDict[LightsDriver]()
      for i in range(4):
        light = self.light[i] = imp.Block(LightsDriver((0, 0.5) * Amp))
        self.connect(self.mcu.gpio.request(f'light_{i}0'), light.control[0])
        self.connect(self.mcu.gpio.request(f'light_{i}1'), light.control[1])

      for i in range(4, 6):
        light = self.light[i] = imp.Block(LightsDriver((0, 3) * Amp))
        self.connect(self.mcu.gpio.request(f'light_{i}0'), light.control[0])
        self.connect(self.mcu.gpio.request(f'light_{i}1'), light.control[1])

    self.hole = ElementDict[MountingHole]()
    for i in range(4):
      self.hole[i] = self.Block(MountingHole_M4())

  def refinements(self) -> Refinements:
    return super().refinements() + Refinements(
      instance_refinements=[
        (['mcu'], Lpc1549_48),
      ],
      instance_values=[
        (['mcu', 'pin_assigns'], [
          'can.txd=43',
          'can.rxd=44',
          'vsense=21',
          'rgb1_red=28',
          'rgb1_green=23',
          'rgb1_blue=22',
          'rgb2_red=18',
          'rgb2_green=15',
          'rgb2_blue=13',
          'light_00=12',
          'light_01=8',
          'light_10=7',
          'light_11=6',
          'light_20=4',
          'light_21=3',
          'light_30=2',
          'light_31=1',
          'light_40=48',
          'light_41=47',
          'light_50=46',
          'light_51=45',
        ]),
        (['mcu', 'swd_swo_pin'], 'PIO0_8'),
        # the hold current wasn't modeled at the time of manufacture and turns out to be out of limits
        (['can', 'can_fuse', 'fuse', 'actual_hold_current'], Range(0.1, 0.1)),
        # JLC does not have frequency specs, must be checked TODO
        (['pwr', 'power_path', 'inductor', 'ignore_frequency'], True),
        # JLC does not have gate charge spec, so ignore the power calc TODO
        (['light[0]', 'drv[0]', 'drv', 'frequency'], Range(0, 0)),
        (['light[0]', 'drv[1]', 'drv', 'frequency'], Range(0, 0)),
        (['light[1]', 'drv[0]', 'drv', 'frequency'], Range(0, 0)),
        (['light[1]', 'drv[1]', 'drv', 'frequency'], Range(0, 0)),
        (['light[2]', 'drv[0]', 'drv', 'frequency'], Range(0, 0)),
        (['light[2]', 'drv[1]', 'drv', 'frequency'], Range(0, 0)),
        (['light[3]', 'drv[0]', 'drv', 'frequency'], Range(0, 0)),
        (['light[3]', 'drv[1]', 'drv', 'frequency'], Range(0, 0)),
        (['light[4]', 'drv[0]', 'drv', 'frequency'], Range(0, 0)),
        (['light[4]', 'drv[1]', 'drv', 'frequency'], Range(0, 0)),
        (['light[5]', 'drv[0]', 'drv', 'frequency'], Range(0, 0)),
        (['light[5]', 'drv[1]', 'drv', 'frequency'], Range(0, 0)),

        # keep netlist footprints as libraries change
        (['light[0]', 'drv[0]', 'drv', 'footprint_spec'], 'Package_TO_SOT_SMD:TO-252-2'),
        (['light[0]', 'drv[1]', 'drv', 'footprint_spec'], ParamValue(['light[0]', 'drv[0]', 'drv', 'footprint_spec'])),
        (['light[1]', 'drv[0]', 'drv', 'footprint_spec'], ParamValue(['light[0]', 'drv[0]', 'drv', 'footprint_spec'])),
        (['light[1]', 'drv[1]', 'drv', 'footprint_spec'], ParamValue(['light[0]', 'drv[0]', 'drv', 'footprint_spec'])),
        (['light[2]', 'drv[0]', 'drv', 'footprint_spec'], ParamValue(['light[0]', 'drv[0]', 'drv', 'footprint_spec'])),
        (['light[2]', 'drv[1]', 'drv', 'footprint_spec'], ParamValue(['light[0]', 'drv[0]', 'drv', 'footprint_spec'])),
        (['light[3]', 'drv[0]', 'drv', 'footprint_spec'], ParamValue(['light[0]', 'drv[0]', 'drv', 'footprint_spec'])),
        (['light[3]', 'drv[1]', 'drv', 'footprint_spec'], ParamValue(['light[0]', 'drv[0]', 'drv', 'footprint_spec'])),
        (['light[4]', 'drv[0]', 'drv', 'footprint_spec'], ParamValue(['light[0]', 'drv[0]', 'drv', 'footprint_spec'])),
        (['light[4]', 'drv[1]', 'drv', 'footprint_spec'], ParamValue(['light[0]', 'drv[0]', 'drv', 'footprint_spec'])),
        (['light[5]', 'drv[0]', 'drv', 'footprint_spec'], ParamValue(['light[0]', 'drv[0]', 'drv', 'footprint_spec'])),
        (['light[5]', 'drv[1]', 'drv', 'footprint_spec'], ParamValue(['light[0]', 'drv[0]', 'drv', 'footprint_spec'])),
      ],
      class_refinements=[
        (PptcFuse, CanFuse)
      ],
    )


class HighSwitchTestCase(unittest.TestCase):
  def test_design(self) -> None:
    compile_board_inplace(HighSwitch)
