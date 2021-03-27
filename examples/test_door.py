import unittest

from edg import *


class DistanceSensor(CircuitBlock):
  '''
  HCSR04 distance sensor
  Datasheet: https://cdn.sparkfun.com/datasheets/Sensors/Proximity/HCSR04.pdf
  '''
  def __init__(self) -> None:
    super().__init__()

    self.vcc = self.Port(ElectricalSink(voltage_limits=(0,5) * Volt, current_draw=(0,15) * mAmp), [Power]) # 5v
    self.trigger = self.Port(DigitalSink(voltage_limits=(0, 5) * Volt, current_draw=(0, 15) * mAmp)) # input: digital, triggers distance measuring
    self.echo = self.Port(DigitalSource(voltage_out=(0, 5) * Volt, current_limits=(0, 15) * mAmp))# output: distance, outputs digital signal (distance ~ time high)
    self.gnd = self.Port(Ground(), [Common])


class DcMotor(CircuitBlock):
  '''
  DMN29BA motor
  Datasheet: http://www.e-jpc.com/pdf/dcmotors601-0241.pdf
  '''
  def __init__(self) -> None:
    super().__init__()
    motor_pin = DigitalSink(voltage_limits=(0, 12) * Volt, current_draw=(0, 0.42) * Amp)
    self.a = self.Port(motor_pin)
    self.b = self.Port(motor_pin)

    # @TODO how to make RangeExpr for resistance/
    low_ohm = 171
    high_ohm = 480
    self.resistance = self.Parameter(RangeExpr((low_ohm, high_ohm) * Ohm))

class MotorDriver(CircuitBlock):
  '''
  DRV8871 Motor Driver
  Tutorial: https://cdn-learn.adafruit.com/downloads/pdf/adafruit-drv8871-brushed-dc-motor-driver-breakout.pdf
  Datasheet: https://cdn-shop.adafruit.com/product-files/3190/drv8871.pdf
  '''
  def __init__(self) -> None:
    super().__init__()

    self.power = self.Port(ElectricalSink(voltage_limits=(6.5, 45) * Volt, current_draw=(0, 3.6) * Amp), [Power])
    self.ground = self.Port(Ground(), [Common])

    input_pins = DigitalSink(
      voltage_limits=(0, 5.5) * Volt,
      input_thresholds=(0.5, 1.5) * Volt # @TODO logic low < 0.5, logic high > 1.5
    )

    output_pins = DigitalSource(
      voltage_out=(0, 12) * Volt,
      current_limits=(0, 3.5) * Amp
    )

    self.in1 = self.Port(DigitalSink(input_pins))
    self.in2 = self.Port(DigitalSink(input_pins))
    self.out1 = self.Port(DigitalSource(output_pins))
    self.out2 = self.Port(DigitalSource(output_pins))

  def contents(self) -> None:
    super().contents()

    with self.implicit_connect(
        ImplicitConnect(self.power, [Power]),
        ImplicitConnect(self.ground, [Common]),
    ) as imp:
      self.vm_cap_0 = imp.Block(DecouplingCapacitor(
        capacitance=0.1*uFarad(tol=0.2),
      ))
      # TODO add aluminum electrolytic capacitor
      # self.vm_cap_1 = imp.Block(DecouplingCapacitor(
      #   capacitance=47*uFarad(tol=0.2),
      # ))

    self.ilm_res = self.Block(Resistor(  # TODO calculate current limit resistor
      resistance=30*kOhm(tol=0.2)
    ))

    assert False, "needs refactoring to split devices / app circuits / no net"

    # self.net(self.ilm_res.b, self.ground)

    # self.package = self.Footprint({
    #   'datasheet': 'https://www.ti.com/lit/ds/symlink/drv8871.pdf',
    #   'kicad': 'Package_SO:SOIC-8-1EP_3.9x4.9mm_P1.27mm_EP2.29x3mm_ThermalVias'
    # }, {
    #   '1': self.ground,
    #   '2': self.in2,
    #   '3': self.in1,
    #   '4': self.ilm_res.a,
    #   '5': self.power,
    #   '6': self.out1,
    #   '7': self.ground,
    #   '8': self.out2,
    #   '9': self.ground,
    # }, 'DRV8871', 'U')


# SSD1351: OLED driver chip
class Ssd1351(CircuitBlock):
  def __init__(self) -> None:
    super().__init__()

    # Vcc is 16 volts, needs power converter. Leave it to user to connect it to Vcc.
    # @TODO put constraints
    self.vcc = self.Port(ElectricalSink(voltage_limits=(0,20) * Volt, current_draw=(0,0.01) * mAmp), [Power])
    # @TODO data needs to be SPI bundle
#     self.data = self.Port(SpiSlave()) # @TODO figure out syntax @todo uncomment the spi
    self.vddio = self.Port(ElectricalSink(voltage_limits=(0,4) * Volt, current_draw=(0,0.01) * mAmp), [Power])
    self.vci = self.Port(ElectricalSink(voltage_limits=(0,4) * Volt), [Power])
    self.gnd = self.Port(Ground(), [Common])

    # @TODO external circuitry like decoupling capacitors

# --


class TestMotionControlledDoor(CircuitBlock):
  def contents(self) -> None:
    super().contents()

#     # @TODO do I need this buck converter as an interface to the output of the power source
#     self.pwr_source = self.Block(PowerSource())
#     self.pwr_converter = self.Block(LM3671MF_3v3())

    self.pwr = self.Block(Pj_102a(voltage_out=12*Volt(tol=0.1), current_limits=(0, 5) * Amp))
    self.mcu = self.Block(Nucleo_F303k8()) # @todo set constraints on current etc or no (like power converter)
    assert False, "FIXME"
    # self.net(self.pwr.gnd, self.mcu.gnd)  # TODO fix ground merging hack

    self.boost_converter = self.Block(Ap3012(output_voltage=12*Volt(tol=0.1)))
    self.connect(self.boost_converter.pwr_in, self.mcu.pwr_5v)
    self.connect(self.boost_converter.gnd, self.mcu.gnd)

    self.constrain(self.boost_converter.pwr_out.link().current_drawn == (0, 200) * mAmp, unchecked=True)  # TODO remove fake const prop



#     self.connect(self.pwr_source.pwr, self.pwr_converter.pwr_in)
#     self.connect(self.pwr_source.gnd, self.pwr_converter.gnd)
#
#     # constraints for generator block inside power converter
#     self.constrain(self.pwr_converter.pwr_in.link().voltage == (4.5, 5.5), unchecked=True)  # TODO fake fake const prop
#     self.constrain(self.pwr_converter.pwr_out.link().voltage == self.pwr_converter.pwr_out.voltage_out, unchecked=True)  # TODO fake fake const prop
#     self.constrain(self.pwr_converter.pwr_out.link().current_drawn == (0, 1) * Amp, unchecked=True)  # TODO fake fake const prop


    with self.implicit_connect(
        ImplicitConnect(self.pwr.pwr, [Power]), # mmmmm
        ImplicitConnect(self.mcu.gnd, [Common])
    ) as imp:
      self.motor_driver = imp.Block(MotorDriver())
      self.motor = imp.Block(DcMotor())

    # # implicit connections for power/ground
    with self.implicit_connect(
        ImplicitConnect(self.mcu.pwr_5v, [Power]), # mmmmm
        # ImplicitConnect(self.mcu.pwr_3v3, [Power]),  # TODO removal of voltage-tagged power rail tags
        ImplicitConnect(self.mcu.gnd, [Common])

    ) as imp:
      # explicit connections for pins
#       self.microcontroller = imp.Block(Lpc1549())
      self.oled = imp.Block(Ssd1351())
      self.connect(self.boost_converter.pwr_out, self.oled.vcc) # todo connect pwr_out to spi, but spi stuff is commented out for now

      self.distance_sensor = imp.Block(DistanceSensor())

      # wire up main circuit
#       self.connect(self.mcu.spi_0, self.oled.data) # micro spi -> oled spi
      self.connect(self.distance_sensor.echo, self.mcu.new_io(DigitalBidir)) # distance sensor -> micro
      self.connect(self.mcu.new_io(DigitalBidir), self.distance_sensor.trigger)
      self.connect(self.mcu.new_io(DigitalBidir), self.motor_driver.in1) # micro -> motor driver
      self.connect(self.mcu.new_io(DigitalBidir), self.motor_driver.in2) # ground other input pin for motor driver ERROR! ground is electrical. either use .net or just connect to micro
      self.connect(self.motor_driver.out1, self.motor.a) # motor driver to motor
      self.connect(self.motor_driver.out2, self.motor.b) # motor driver to motor

      # trying to break edg
      # 1. connect (required) pins to themselves
      # self.connect(self.motor_driver.out2, self.motor_driver.out2)
      # self.connect(self.motor.b, self.motor.b)
      # 2. connect power to ground (both are sources, can't connect source to source)





class MotionControlledDoorTestCase(unittest.TestCase):
  @unittest.skip("needs major refactoring to update to new electronics model")
  def test_design(self) -> None:
    compile_board_inplace(TestMotionControlledDoor)
