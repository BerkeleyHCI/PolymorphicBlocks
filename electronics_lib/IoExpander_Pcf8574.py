from itertools import chain
from typing import Dict, List

from electronics_abstract_parts import *
from .JlcPart import JlcPart


class Pcf8574_Device(PinMappable, InternalSubcircuit, FootprintBlock, JlcPart, GeneratorBlock):
  @init_in_parent
  def __init__(self, addr_lsb: IntLike, **kwags) -> None:
    super().__init__(**kwags)
    self.gnd = self.Port(Ground())
    self.vdd = self.Port(VoltageSink(  # same between TI and NXP versions
      voltage_limits=(2.5, 6)*Volt,
      current_draw=(2.5, 100)*uAmp  # TODO propagate current draw from loads
    ))

    i2c_model = DigitalBidir.from_supply(  # same between TI and NXP versions
      self.gnd, self.vdd,
      current_limits=(-3, 0)*mAmp,
      voltage_limit_tolerance=(-0.5, 0.5)*Volt,
      input_threshold_factor=(0.3, 0.7)
    )
    self.i2c = self.Port(I2cSlave(i2c_model))

    self.io = self.Port(Vector(DigitalBidir().empty()), optional=True)

    self.addr_lsb = self.ArgParameter(addr_lsb)
    self.generator_param(self.addr_lsb, self.pin_assigns, self.io.requested())

  def generate(self) -> None:
    dout_model = DigitalBidir.from_supply(  # same between TI and NXP versions
      self.gnd, self.vdd,
      current_limits=(-25, 0.3)*mAmp,  # highly limited sourcing current
      voltage_limit_tolerance=(-0.5, 0.5)*Volt,
      input_threshold_factor=(0.3, 0.7)
    )

    addr_lsb = self.get(self.addr_lsb)
    self.require((addr_lsb < 8) & (addr_lsb >= 0), f"addr_lsb={addr_lsb} must be within [0, 8)")

    pinmaps = PinMapUtil([
      PinResource('4', {'P0': dout_model}),
      PinResource('5', {'P1': dout_model}),
      PinResource('6', {'P2': dout_model}),
      PinResource('7', {'P3': dout_model}),
      PinResource('9', {'P4': dout_model}),
      PinResource('10', {'P5': dout_model}),
      PinResource('11', {'P6': dout_model}),
      PinResource('12', {'P7': dout_model}),
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
      'U', 'Package_SO:SOIC-16W_7.5x10.3mm_P1.27mm',
      dict(chain(ic_pins.items(), io_pins.items())),
      mfr='NXP', part='PCF8574AT',
      datasheet='https://www.nxp.com/docs/en/data-sheet/PCF8574_PCF8574A.pdf'
    )
    self.assign(self.lcsc_part, "C86832")


class Pcf8574(Interface, PinMappable):
  """8 bit I2C IO expander with 'quasi-bidirectional IOs'"""
  @init_in_parent
  def __init__(self, addr_lsb: IntLike = Default(0)) -> None:
    super().__init__()
    self.ic = self.Block(Pcf8574_Device(addr_lsb=addr_lsb, pin_assigns=self.pin_assigns))
    self.pwr = self.Export(self.ic.vdd, [Power])
    self.gnd = self.Export(self.ic.gnd, [Common])
    self.i2c = self.Export(self.ic.i2c)
    self.io = self.Export(self.ic.io)

  def contents(self) -> None:
    super().contents()
    self.assign(self.actual_pin_assigns, self.ic.actual_pin_assigns)
    self.vdd_cap = self.Block(DecouplingCapacitor(0.1*uFarad(tol=0.2))).connected(self.gnd, self.pwr)
