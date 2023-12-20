from itertools import chain
from typing import Dict, List

from electronics_abstract_parts import *
from .JlcPart import JlcPart


class Pca9554_Device(PinMappable, InternalSubcircuit, FootprintBlock, JlcPart, GeneratorBlock):
  @init_in_parent
  def __init__(self, addr_lsb: IntLike, **kwags) -> None:
    super().__init__(**kwags)
    self.gnd = self.Port(Ground())
    self.vdd = self.Port(VoltageSink(
      voltage_limits=(2.3, 5.5)*Volt,
      current_draw=(0.25, 700)*uAmp  # TODO propagate current draw from loads
    ))

    i2c_model = DigitalBidir.from_supply(
      self.gnd, self.vdd,
      current_limits=(-3, 0)*mAmp,
      voltage_limit_tolerance=(-0.5, 0.5)*Volt,
      input_threshold_factor=(0.3, 0.7)
    )
    self.i2c = self.Port(I2cTarget(i2c_model))

    self.io = self.Port(Vector(DigitalBidir.empty()), optional=True)

    self.addr_lsb = self.ArgParameter(addr_lsb)
    self.generator_param(self.addr_lsb, self.pin_assigns, self.io.requested())

  def generate(self) -> None:
    dout_model = DigitalBidir.from_supply(  # same between TI and NXP versions
      self.gnd, self.vdd,
      current_limits=(-10, 10)*mAmp,  # sink min @ 2.3v (-24mA typ @ 4.5v), source @ 2.3v
      voltage_limit_abs=(-0.5, 5.5)*Volt,
      input_threshold_abs=(0.8, 2.0)*Volt
    )

    addr_lsb = self.get(self.addr_lsb)
    self.require((addr_lsb < 8) & (addr_lsb >= 0), f"addr_lsb={addr_lsb} must be within [0, 8)")

    pinmaps = PinMapUtil([  # *PW (TSSOP16) variant
      PinResource('4', {'IO0': dout_model}),
      PinResource('5', {'IO1': dout_model}),
      PinResource('6', {'IO2': dout_model}),
      PinResource('7', {'IO3': dout_model}),
      PinResource('9', {'IO4': dout_model}),
      PinResource('10', {'IO5': dout_model}),
      PinResource('11', {'IO6': dout_model}),
      PinResource('12', {'IO7': dout_model}),
    ])

    ic_pins: Dict[str, CircuitPort] = {
      '1': self.vdd if addr_lsb & 1 else self.gnd,  # A0
      '2': self.vdd if addr_lsb & 2 else self.gnd,  # A1
      '3': self.vdd if addr_lsb & 4 else self.gnd,  # A2
      '8': self.gnd,
      # '13': self.int,
      '14': self.i2c.scl,
      '15': self.i2c.sda,
      '16': self.vdd,
    }

    allocated = pinmaps.allocate([(DigitalBidir, self.get(self.io.requested()))], self.get(self.pin_assigns))
    io_pins: Dict[str, CircuitPort] = {
      allocation.pin: self.io.append_elt(dout_model, allocation.name)  # type: ignore
      for allocation in allocated}
    self.generator_set_allocation(allocated)

    self.footprint(
      'U', 'Package_SO:TSSOP-16_4.4x5mm_P0.65mm',
      dict(chain(ic_pins.items(), io_pins.items())),
      mfr='NXP', part='PCA9554APW,118',  # -A variant, in TSSOP16
      datasheet='https://www.nxp.com/docs/en/data-sheet/PCA9554_9554A.pdf'
    )
    self.assign(self.lcsc_part, 'C86803')


class Pca9554(Interface, PinMappable):
  """8 bit I2C IO expander"""
  @init_in_parent
  def __init__(self, addr_lsb: IntLike = 0) -> None:
    super().__init__()
    self.ic = self.Block(Pca9554_Device(addr_lsb=addr_lsb, pin_assigns=self.pin_assigns))
    self.pwr = self.Export(self.ic.vdd, [Power])
    self.gnd = self.Export(self.ic.gnd, [Common])
    self.i2c = self.Export(self.ic.i2c)
    self.io = self.Export(self.ic.io)

  def contents(self) -> None:
    super().contents()
    self.assign(self.actual_pin_assigns, self.ic.actual_pin_assigns)
    self.vdd_cap = self.Block(DecouplingCapacitor(0.1*uFarad(tol=0.2))).connected(self.gnd, self.pwr)
