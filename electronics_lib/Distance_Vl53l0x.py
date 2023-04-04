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
    self.gpio1 = self.Port(gpio_model, optional=True)

    self.i2c = self.Port(I2cSlave(self._i2c_io_model(self.vss, self.vdd)), [Output])

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


@abstract_block_default(lambda: Vl53l0xApplication)
class Vl53l0x(DistanceSensor, Block):
  """Abstract base class for VL53L0x application circuits"""
  def __init__(self) -> None:
    super().__init__()

    self.pwr = self.Port(VoltageSink().empty(), [Power])
    self.gnd = self.Port(Ground().empty(), [Common])

    self.i2c = self.Port(I2cSlave.empty())
    self.xshut = self.Port(DigitalSink.empty())  # MUST be driven
    self.gpio1 = self.Port(DigitalBidir.empty(), optional=True)


class Vl53l0xConnector(Vl53l0x_DeviceBase, Vl53l0x):
  """Connector to an external VL53L0X breakout board.
  Uses the pinout from the Adafruit product: https://www.adafruit.com/product/3317
  This has an onboard 2.8v regulator, but thankfully the IO tolerance is not referenced to Vdd"""
  def __init__(self) -> None:
    super().__init__()
    self.conn = self.Block(PassiveConnector(length=6))
    self.connect(self.pwr, self.conn.pins.request('1').adapt_to(self._vdd_model()))
    self.connect(self.gnd, self.conn.pins.request('2').adapt_to(Ground()))

    gpio_model = self._gpio_model(self.gnd, self.pwr)
    self.connect(self.xshut, self.conn.pins.request('6').adapt_to(gpio_model))
    self.connect(self.gpio1, self.conn.pins.request('5').adapt_to(gpio_model))

    i2c_io_model = self._i2c_io_model(self.gnd, self.pwr)
    self.connect(self.i2c.scl, self.conn.pins.request('3').adapt_to(i2c_io_model))
    self.connect(self.i2c.sda, self.conn.pins.request('4').adapt_to(i2c_io_model))
    self.i2c.init_from(I2cSlave(DigitalBidir.empty(), []))


class Vl53l0xApplication(Vl53l0x):
  """Board-mount laser ToF sensor"""
  def contents(self):
    super().contents()
    self.ic = self.Block(Vl53l0x_Device())
    self.connect(self.pwr, self.ic.vdd)
    self.connect(self.gnd, self.ic.vss)

    self.connect(self.i2c, self.ic.i2c)
    self.connect(self.xshut, self.ic.xshut)  # MUST be driven
    self.connect(self.gpio1, self.ic.gpio1)

    # Datasheet Figure 3, two decoupling capacitors
    self.vdd_cap = ElementDict[DecouplingCapacitor]()
    self.vdd_cap[0] = self.Block(DecouplingCapacitor(0.1 * uFarad(tol=0.2))).connected(self.gnd, self.pwr)
    self.vdd_cap[1] = self.Block(DecouplingCapacitor(4.7 * uFarad(tol=0.2))).connected(self.gnd, self.pwr)


class Vl53l0xArray(DistanceSensor, GeneratorBlock):
  """Array of Vl53l0x with common I2C but individually exposed XSHUT pins and optionally GPIO1 (interrupt)."""
  @init_in_parent
  def __init__(self, count: IntLike, *, first_xshut_fixed: BoolLike = False):
    super().__init__()
    self.pwr = self.Port(VoltageSink.empty(), [Power])
    self.gnd = self.Port(Ground.empty(), [Common])
    self.i2c = self.Port(I2cSlave.empty())
    self.xshut = self.Port(Vector(DigitalSink.empty()))
    self.gpio1 = self.Port(Vector(DigitalBidir.empty()), optional=True)
    self.generator(self.generate, count, first_xshut_fixed)

  def generate(self, count: int, first_xshut_fixed: bool):
    self.elt = ElementDict[Vl53l0x]()
    for elt_i in range(count):
      elt = self.elt[str(elt_i)] = self.Block(Vl53l0x())
      self.connect(self.pwr, elt.pwr)
      self.connect(self.gnd, elt.gnd)
      self.connect(self.i2c, elt.i2c)
      if first_xshut_fixed and elt_i == 0:
        self.connect(elt.pwr.as_digital_source(), elt.xshut)
      else:
        self.connect(self.xshut.append_elt(DigitalSink.empty(), str(elt_i)), elt.xshut)

      self.connect(self.gpio1.append_elt(DigitalBidir.empty(), str(elt_i)), elt.gpio1)
