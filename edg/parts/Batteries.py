from typing import Optional, Union, Any

from ..abstract_parts import *


class Cr2032(Battery, FootprintBlock):
  def __init__(self, voltage: RangeLike = (2.0, 3.0)*Volt, *args: Any,
               actual_voltage: RangeLike = (2.0, 3.0)*Volt, **kwargs: Any) -> None:
    super().__init__(voltage, *args, **kwargs)
    self.pwr.init_from(VoltageSource(
      voltage_out=self.gnd.link().voltage + actual_voltage,  # arbitrary from https://www.mouser.com/catalog/additional/Adafruit_3262.pdf
      current_limits=(0, 10)*mAmp,
    ))
    self.gnd.init_from(Ground())

  @override
  def contents(self) -> None:
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
  def __init__(self, voltage: RangeLike = (2.5, 4.2)*Volt, *args: Any,
               actual_voltage: RangeLike = (2.5, 4.2)*Volt, **kwargs: Any) -> None:
    super().__init__(voltage, *args, **kwargs)
    self.pwr.init_from(VoltageSource(
      voltage_out=self.gnd.link().voltage + actual_voltage,
      current_limits=(0, 2)*Amp,  # arbitrary assuming low capacity, 1 C discharge
    ))
    self.gnd.init_from(Ground())

  @override
  def contents(self) -> None:
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


class AaBattery(Battery, FootprintBlock):
  """AA battery holder supporting alkaline and rechargeable chemistries."""
  def __init__(self, voltage: RangeLike = (1.0, 1.6)*Volt, *args: Any,
               actual_voltage: RangeLike = (1.0, 1.6)*Volt, **kwargs: Any) -> None:
    super().__init__(voltage, *args, **kwargs)
    self.gnd.init_from(Ground())
    self.pwr.init_from(VoltageSource(
      voltage_out=self.gnd.link().voltage + actual_voltage,
      current_limits=(0, 1)*Amp,
    ))

  @override
  def contents(self) -> None:
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


class AaBatteryStack(Battery, GeneratorBlock):
    """AA Alkaline battery stack that generates batteries in series"""
    def __init__(self, count: IntLike = 1, *, cell_actual_voltage: RangeLike = (1.0, 1.6)*Volt):
        super().__init__(voltage=Range.all())  # no voltage spec passed in
        self.count = self.ArgParameter(count)
        self.cell_actual_voltage = self.ArgParameter(cell_actual_voltage)
        self.generator_param(self.count)

    @override
    def generate(self) -> None:
        super().generate()
        prev_cell: Optional[AaBattery] = None
        prev_capacity_min: Union[FloatExpr, float] = float('inf')
        prev_capacity_max: Union[FloatExpr, float] = float('inf')
        self.cell = ElementDict[AaBattery]()
        for i in range(self.get(self.count)):
          self.cell[i] = cell = self.Block(AaBattery(actual_voltage=self.cell_actual_voltage))
          if prev_cell is None:  # first cell, direct connect to gnd
            self.connect(self.gnd, cell.gnd)
          else:
            self.connect(prev_cell.pwr.as_ground(self.pwr.link().current_drawn), cell.gnd)
            prev_capacity_min = cell.actual_capacity.lower().min(prev_capacity_min)
            prev_capacity_max = cell.actual_capacity.upper().min(prev_capacity_max)
          prev_cell = cell

        assert prev_cell is not None, "must generate >=1 cell"
        self.connect(self.pwr, prev_cell.pwr)
        self.assign(self.actual_capacity, (prev_capacity_min, prev_capacity_max))
