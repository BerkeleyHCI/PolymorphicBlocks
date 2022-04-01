from electronics_abstract_parts import *


class Cr2032(Battery, FootprintBlock):
  def __init__(self, voltage: RangeLike = Default((2.0, 3.0)*Volt), *args,
               actual_voltage: RangeLike = Default((2.0, 3.0)*Volt), **kwargs):
    super().__init__(voltage, *args, **kwargs)
    self.pwr.init_from(VoltageSource(
      voltage_out=actual_voltage,  # arbitrary from https://www.mouser.com/catalog/additional/Adafruit_3262.pdf
      current_limits=(0, 10)*mAmp,
    ))
    self.gnd.init_from(GroundSource())

  def contents(self):
    super().contents()

    self.assign(self.actual_capacity, (210, 210)*mAmp)  # TODO bounds of a few CR2032 cells; should be A*h

    self.footprint(
      'U', 'Battery:BatteryHolder_Keystone_106_1x20mm',
      {
        '1': self.pwr,
        '2': self.gnd,
      },
      mfr='Keystone', part='106'
    )


class Li18650(Battery, FootprintBlock):
  @init_in_parent
  def __init__(self, voltage: RangeLike = Default((2.5, 4.2)*Volt), *args,
               actual_voltage: RangeLike = Default((2.5, 4.2)*Volt), **kwargs):
    super().__init__(voltage, *args, **kwargs)
    self.pwr.init_from(VoltageSource(
      voltage_out=actual_voltage,  # arbitrary from https://www.mouser.com/catalog/additional/Adafruit_3262.pdf
      current_limits=(0, 2)*Amp,  # arbitrary assuming low capacity, 1 C discharge
    ))
    self.gnd.init_from(GroundSource())

  def contents(self):
    super().contents()

    self.assign(self.actual_capacity, (2, 3.6)*Amp)  # TODO should be A*h

    self.footprint(
      'U', 'Battery:BatteryHolder_Keystone_1042_1x18650',
      {
        '1': self.pwr,
        '2': self.gnd,
      },
      mfr='Keystone', part='1042'
    )

class AABattery(Battery, FootprintBlock):
  """AA Alkaline battery"""
  @init_in_parent
  def __init__(self, voltage: RangeLike = Default((1.3, 1.7)*Volt), *args,
               actual_voltage: RangeLike = Default((1.3, 1.7)*Volt), **kwargs):
    super().__init__(voltage, *args, **kwargs)
    self.pwr.init_from(VoltageSource(
      voltage_out=actual_voltage,  # arbitrary from https://www.mouser.com/catalog/additional/Adafruit_3262.pdf
      current_limits=(0, 1)*Amp,
    ))
    self.gnd.init_from(GroundSource())

  def contents(self):
    super().contents()

    self.assign(self.actual_capacity, (2, 3)*Amp)  # TODO should be A*h

    self.footprint(
      'U', 'Battery:BatteryHolder_Keystone_2460_1xAA',
      {
        '1': self.pwr,
        '2': self.gnd,
      },
      mfr='Keystone', part='2460'
    )
