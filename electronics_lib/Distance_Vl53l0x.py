from electronics_abstract_parts import *
from .JlcPart import JlcPart


class Vl53l0x_DeviceBase():
  """Shared common definitions for VL53L0x devices"""
  @staticmethod
  def _vdd_model() -> VoltageSink:
    return VoltageSink(
      voltage_limits=(2.6, 3.5) * Volt,
      current_draw=(3, 40000) * uAmp  # up to 40mA including VCSEL when ranging
    )

  @staticmethod
  def _gpio_model(vss: Port[VoltageLink], vdd: Port[VoltageLink]) -> DigitalBidir:
    # TODO: the datasheet references values to IOVDD, but the value of IOVDD is never stated.
    # This model assumes that IOVDD = Vdd
    return DigitalBidir.from_supply(
      vss, vdd,
      voltage_limit_abs=(-0.5, 3.6),  # not referenced to Vdd!
      input_threshold_factor=(0.3, 0.7),
    )

  @staticmethod
  def _i2c_io_model(vss: Port[VoltageLink], vdd: Port[VoltageLink]) -> DigitalBidir:
    return DigitalBidir.from_supply(
      vss, vdd,
      voltage_limit_abs=(-0.5, 3.6),  # not referenced to Vdd!
      input_threshold_abs=(0.6, 1.12),
    )


class Vl53l0x_Device(Vl53l0x_DeviceBase, InternalSubcircuit, JlcPart, FootprintBlock):
  def __init__(self) -> None:
    super().__init__()

    self.vdd = self.Port(self._vdd_model(), [Power])
    self.vss = self.Port(Ground(), [Common])

    gpio_model = self._gpio_model(self.vss, self.vdd)
    self.xshut = self.Port(DigitalSink.from_bidir(gpio_model))
    self.gpio1 = self.Port(DigitalSingleSource.low_from_supply(self.vss), optional=True)

    # TODO: support addresses, the default is 0x29 though it's software remappable
    self.i2c = self.Port(I2cTarget(self._i2c_io_model(self.vss, self.vdd)), [Output])

  def contents(self):
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


@abstract_block_default(lambda: Vl53l0x)
class Vl53l0xBase(Resettable, DistanceSensor, Block):
  """Abstract base class for VL53L0x devices"""
  def __init__(self) -> None:
    super().__init__()

    self.gnd = self.Port(Ground.empty(), [Common])
    self.pwr = self.Port(VoltageSink.empty(), [Power])

    self.i2c = self.Port(I2cTarget.empty())
    self.int = self.Port(DigitalSingleSource.empty(), optional=True,
                         doc="Interrupt output for new data available")


class Vl53l0xConnector(Vl53l0x_DeviceBase, Vl53l0xBase, GeneratorBlock):
  """Connector to an external VL53L0X breakout board.
  Uses the pinout from the Adafruit product: https://www.adafruit.com/product/3317
  This has an onboard 2.8v regulator, but thankfully the IO tolerance is not referenced to Vdd"""
  def contents(self):
    super().contents()
    self.generator_param(self.reset.is_connected(), self.int.is_connected())

  def generate(self):
    super().generate()
    self.conn = self.Block(PassiveConnector(length=6))
    self.connect(self.pwr, self.conn.pins.request('1').adapt_to(self._vdd_model()))
    self.connect(self.gnd, self.conn.pins.request('2').adapt_to(Ground()))

    gpio_model = self._gpio_model(self.gnd, self.pwr)


    i2c_io_model = self._i2c_io_model(self.gnd, self.pwr)
    self.connect(self.i2c.scl, self.conn.pins.request('3').adapt_to(i2c_io_model))
    self.connect(self.i2c.sda, self.conn.pins.request('4').adapt_to(i2c_io_model))
    self.i2c.init_from(I2cTarget(DigitalBidir.empty(), []))

    gpio_model = self._gpio_model(self.gnd, self.pwr)
    if self.get(self.reset.is_connected()):
      self.connect(self.reset, self.conn.pins.request('6').adapt_to(gpio_model))
    else:
      self.connect(self.pwr.as_digital_source(), self.conn.pins.request('6').adapt_to(gpio_model))

    if self.get(self.int.is_connected()):
      self.connect(self.int, self.conn.pins.request('5').adapt_to(
        DigitalSingleSource.low_from_supply(self.gnd)
      ))


class Vl53l0x(Vl53l0xBase, GeneratorBlock):
  """Time-of-flight laser ranging sensor, up to 2m"""
  def contents(self):
    super().contents()
    self.ic = self.Block(Vl53l0x_Device())
    self.connect(self.pwr, self.ic.vdd)
    self.connect(self.gnd, self.ic.vss)

    self.connect(self.i2c, self.ic.i2c)
    self.generator_param(self.reset.is_connected(), self.int.is_connected())

    # Datasheet Figure 3, two decoupling capacitors
    self.vdd_cap = ElementDict[DecouplingCapacitor]()
    self.vdd_cap[0] = self.Block(DecouplingCapacitor(0.1 * uFarad(tol=0.2))).connected(self.gnd, self.pwr)
    self.vdd_cap[1] = self.Block(DecouplingCapacitor(4.7 * uFarad(tol=0.2))).connected(self.gnd, self.pwr)

  def generate(self):
    super().generate()
    if self.get(self.reset.is_connected()):
      self.connect(self.reset, self.ic.xshut)
    else:
      self.connect(self.pwr.as_digital_source(), self.ic.xshut)

    if self.get(self.int.is_connected()):
      self.connect(self.int, self.ic.gpio1)

class Vl53l0xArray(DistanceSensor, GeneratorBlock):
  """Array of Vl53l0x with common I2C but individually exposed XSHUT pins and optionally GPIO1 (interrupt)."""
  @init_in_parent
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

  def generate(self):
    super().generate()
    self.elt = ElementDict[Vl53l0xBase]()
    for elt_i in range(self.get(self.count)):
      elt = self.elt[str(elt_i)] = self.Block(Vl53l0xBase())
      self.connect(self.pwr, elt.pwr)
      self.connect(self.gnd, elt.gnd)
      self.connect(self.i2c, elt.i2c)
      if self.get(self.first_reset_fixed) and elt_i == 0:
        self.connect(elt.pwr.as_digital_source(), elt.reset)
      else:
        self.connect(self.reset.append_elt(DigitalSink.empty(), str(elt_i)), elt.reset)
