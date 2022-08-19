from electronics_abstract_parts import *
from .JlcPart import JlcPart


class Pcf8574_Device(DiscreteChip, FootprintBlock, JlcPart):
  def __init__(self) -> None:
    super().__init__()
    self.gnd = self.Port(Ground())
    self.vdd = self.Port(VoltageSink(  # same between TI and NXP versions
      voltage_limits=(2.5, 6)*Volt,
      current_draw=(2.5, 100)*uAmp  # TODO propagate current draw from loads
    ))

    # TODO support configurable address?

    i2c_model = DigitalBidir.from_supply(  # same between TI and NXP versions
      self.gnd, self.vdd,
      current_limits=(-3, 0)*mAmp,
      voltage_limit_tolerance=(-0.5, 0.5)*Volt,
      input_threshold_factor=(0.3, 0.7)
    )
    self.i2c = self.Port(I2cSlave(i2c_model))

    dout_model = DigitalSource.from_supply(  # same between TI and NXP versions
      self.gnd, self.vdd,
      current_limits=(-25, 0.3)*mAmp  # highly limited sourcing current
    )
    self.p = self.Port(Vector(DigitalSource().empty()), optional=True)
    for i in range(8):
      self.p.append_elt(dout_model, str(i))

  def contents(self) -> None:
    self.footprint(
      'U', 'Package_SO:SOIC-16W_7.5x10.3mm_P1.27mm',
      {
        '1': self.gnd,  # A0
        '2': self.gnd,  # A1
        '3': self.gnd,  # A2
        '4': self.p['0'],
        '5': self.p['1'],
        '6': self.p['2'],
        '7': self.p['3'],
        '8': self.gnd,
        '9': self.p['4'],
        '10': self.p['5'],
        '11': self.p['6'],
        '12': self.p['7'],
        # '13': self.int,
        '14': self.i2c.scl,
        '15': self.i2c.sda,
        '16': self.vdd,
      },
      mfr='NXP', part='PCF8574AT',
      datasheet='https://www.nxp.com/docs/en/data-sheet/PCF8574_PCF8574A.pdf'
    )
    self.assign(self.lcsc_part, "C86832")


class Pcf8574(Block):
  """8 bit I2C IO expander with 'quasi-bidirectional IOs'"""
  def __init__(self) -> None:
    super().__init__()
    self.ic = self.Block(Pcf8574_Device())
    self.pwr = self.Export(self.ic.vdd, [Power])
    self.gnd = self.Export(self.ic.gnd, [Common])
    self.i2c = self.Export(self.ic.i2c)
    self.io = self.Export(self.ic.p)

  def contents(self) -> None:
    super().contents()
    self.vdd_cap = self.Block(DecouplingCapacitor(0.1*uFarad(tol=0.2))).connected(self.gnd, self.pwr)
