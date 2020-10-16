from electronics_abstract_parts import *


class Cr2032(Battery, CircuitBlock):
  def contents(self):
    super().contents()

    # TODO can this be assigned self.pwr == ElectricalSource(...) directly?
    self.constrain(self.pwr.voltage_out == (2.0, 3.0)*Volt)
    self.constrain(self.pwr.current_limits == (0, 10)*mAmp)  # arbitrary from https://www.mouser.com/catalog/additional/Adafruit_3262.pdf
    self.constrain(self.capacity.within((210, 210)*mAmp))  # TODO bounds of a few CR2032 cells; should be A*h

    self.footprint(
      'U', 'Battery:BatteryHolder_Keystone_106_1x20mm',
      {
        '1': self.pwr,
        '2': self.gnd,
      },
      mfr='Keystone', part='106'
    )


class Li18650(Battery, CircuitBlock):
  def contents(self):
    super().contents()

    # TODO can this be assigned self.pwr == ElectricalSource(...) directly?
    self.constrain(self.pwr.voltage_out == (2.5, 4.2)*Volt)
    self.constrain(self.pwr.current_limits == (0, 2)*mAmp)  # arbitrary assuming low capacity, 1 C discharge
    self.constrain(self.capacity.within((2, 3.6)*Amp))  # TODO should be A*h

    self.footprint(
      'U', 'Battery:BatteryHolder_Keystone_1042_1x18650',
      {
        '1': self.pwr,
        '2': self.gnd,
      },
      mfr='Keystone', part='1042'
    )
