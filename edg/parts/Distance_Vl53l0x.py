from typing_extensions import override

from ..abstract_parts import *
from .JlcPart import JlcPart


class Vl53l0x_Device(InternalSubcircuit, JlcPart, FootprintBlock):
  def __init__(self) -> None:
    super().__init__()

    self.vdd = self.Port(VoltageSink(
      voltage_limits=(2.6, 3.5) * Volt,
      current_draw=(3, 40000) * uAmp  # up to 40mA including VCSEL when ranging
    ), [Power])
    self.vss = self.Port(Ground(), [Common])

    # TODO: the datasheet references values to IOVDD, but the value of IOVDD is never stated.
    gpio_model = DigitalBidir.from_supply(  # This model assumes that IOVDD = Vdd
      self.vss, self.vdd,
      voltage_limit_abs=(-0.5, 3.6),  # not referenced to Vdd!
      input_threshold_factor=(0.3, 0.7),
    )
    self.xshut = self.Port(DigitalSink.from_bidir(gpio_model))
    self.gpio1 = self.Port(DigitalSource.low_from_supply(self.vss), optional=True)

    # TODO: support addresses, the default is 0x29 though it's software remappable
    self.i2c = self.Port(I2cTarget(DigitalBidir.from_supply(
      self.vss, self.vdd,
      voltage_limit_abs=(-0.5, 3.6),  # not referenced to Vdd!
      input_threshold_abs=(0.6, 1.12),
    )), [Output])

  @override
  def contents(self) -> None:
    super().contents()
    self.footprint(
      'U', 'OptoDevice:ST_VL53L0X',
      {
        '1': self.vdd,  # AVddVcsel
        '2': self.vss,  # AVssVcsel
        '3': self.vss,  # GND
        '4': self.vss,  # GND2
        '5': self.xshut,
        '6': self.vss,  # GND3
        '7': self.gpio1,
        # '8': ,  # DNC, must be left floating
        '9': self.i2c.sda,
        '10': self.i2c.scl,
        '11': self.vdd,  # AVdd
        '12': self.vss,  # GND4
      },
      mfr='STMicroelectronics', part='VL53L0X',
      datasheet='https://www.st.com/content/ccc/resource/technical/document/datasheet/group3/b2/1e/33/77/c6/92/47/6b/DM00279086/files/DM00279086.pdf/jcr:content/translations/en.DM00279086.pdf'
    )
    self.assign(self.lcsc_part, "C91199")
    self.assign(self.actual_basic_part, False)


class Vl53l0x(DistanceSensor, Resettable, GeneratorBlock):
  """Time-of-flight laser ranging sensor, up to 2m"""
  def __init__(self) -> None:
    super().__init__()
    self.ic = self.Block(Vl53l0x_Device())
    self.gnd = self.Export(self.ic.vss, [Common])
    self.pwr = self.Export(self.ic.vdd, [Power])

    self.i2c = self.Export(self.ic.i2c)

    self.int = self.Port(DigitalSource.empty(), optional=True,
                         doc="Interrupt output for new data available")
    self.generator_param(self.reset.is_connected(), self.int.is_connected())

  @override
  def generate(self) -> None:
    super().generate()
    if self.get(self.reset.is_connected()):
      self.connect(self.reset, self.ic.xshut)
    else:
      self.connect(self.pwr.as_digital_source(), self.ic.xshut)

    if self.get(self.int.is_connected()):
      self.connect(self.int, self.ic.gpio1)

    # Datasheet Figure 3, two decoupling capacitors
    self.vdd_cap = ElementDict[DecouplingCapacitor]()
    self.vdd_cap[0] = self.Block(DecouplingCapacitor(0.1 * uFarad(tol=0.2))).connected(self.gnd, self.pwr)
    self.vdd_cap[1] = self.Block(DecouplingCapacitor(4.7 * uFarad(tol=0.2))).connected(self.gnd, self.pwr)


class Vl53l0xConnector(Vl53l0x, WrapperFootprintBlock):
  """Connector to an external VL53L0X breakout board.
  Uses the pinout from the Adafruit product: https://www.adafruit.com/product/3317
  This has an onboard 2.8v regulator, but thankfully the IO tolerance is not referenced to Vdd

  TODO: not completely correct that this should extend the application circuit"""
  @override
  def generate(self) -> None:
    super().generate()
    self.footprint(
      'J', 'Connector_PinSocket_2.54mm:PinSocket_1x06_P2.54mm_Vertical',
      {
        '1': self.pwr,
        '2': self.gnd,
        '3': self.i2c.scl,
        '4': self.i2c.sda,
        '5': self.ic.gpio1,
        '6': self.ic.xshut
      },
    )


class Vl53l0xArray(DistanceSensor, GeneratorBlock):
  """Array of Vl53l0x with common I2C but individually exposed XSHUT pins and optionally GPIO1 (interrupt)."""
  def __init__(self, count: IntLike, *, first_reset_fixed: BoolLike = False):
    super().__init__()
    self.pwr = self.Port(VoltageSink.empty(), [Power])
    self.gnd = self.Port(Ground.empty(), [Common])
    self.i2c = self.Port(I2cTarget.empty())
    self.reset = self.Port(Vector(DigitalSink.empty()))
    # TODO better support for optional vectors so the inner doesn't connect if the outer doesn't connect
    # self.int = self.Port(Vector(DigitalSingleSource.empty()), optional=True)

    self.count = self.ArgParameter(count)
    self.first_reset_fixed = self.ArgParameter(first_reset_fixed)
    self.generator_param(self.count, self.first_reset_fixed)

  @override
  def generate(self) -> None:
    super().generate()
    self.elt = ElementDict[Vl53l0x]()
    for elt_i in range(self.get(self.count)):
      elt = self.elt[str(elt_i)] = self.Block(Vl53l0x())
      self.connect(self.pwr, elt.pwr)
      self.connect(self.gnd, elt.gnd)
      self.connect(self.i2c, elt.i2c)
      if self.get(self.first_reset_fixed) and elt_i == 0:
        self.connect(elt.pwr.as_digital_source(), elt.reset)
      else:
        self.connect(self.reset.append_elt(DigitalSink.empty(), str(elt_i)), elt.reset)
