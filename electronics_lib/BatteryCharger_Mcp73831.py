from electronics_abstract_parts import *
from .JlcPart import JlcPart


class Mcp73831_Device(InternalSubcircuit, JlcPart, FootprintBlock):
  @init_in_parent
  def __init__(self, charging_current: RangeLike) -> None:
    super().__init__()

    self.charging_current = self.ArgParameter(charging_current)

    self.vss = self.Port(Ground())
    self.vdd = self.Port(VoltageSink(
      voltage_limits=(3.75, 6)*Volt,  # Section 1, DC characteristics
      current_draw=(0.0001, 1.5)*mAmp + self.charging_current
    ))

    self.stat = self.Port(DigitalSource.from_supply(
      self.vss, self.vdd,
      current_limits=(-25, 35)*mAmp
    ))
    self.vbat = self.Port(VoltageSource(
      voltage_out=(4.168, 4.232)*Volt,  # -2 variant
      current_limits=charging_current.hull(0*Amp(tol=0))
    ))
    self.prog = self.Port(Passive())

  def contents(self) -> None:
    super().contents()
    self.footprint(
      'U', 'Package_TO_SOT_SMD:SOT-23-5',
      {
        '1': self.stat,
        '2': self.vss,
        '3': self.vbat,
        '4': self.vdd,
        '5': self.prog,
      },
      mfr='Microchip Technology', part='MCP73831T-2ACI/OT',
      datasheet='https://ww1.microchip.com/downloads/en/DeviceDoc/MCP73831-Family-Data-Sheet-DS20001984H.pdf'
    )
    self.assign(self.lcsc_part, 'C424093')
    self.assign(self.actual_basic_part, False)


class Mcp73831(PowerConditioner, Block):
  """Single-cell Li-ion / Li-poly charger, seemingly popular on Adafruit and Sparkfun boards."""
  @init_in_parent
  def __init__(self, charging_current: RangeLike) -> None:
    super().__init__()

    self.ic = self.Block(Mcp73831_Device(charging_current=RangeExpr()))

    self.pwr_bat = self.Export(self.ic.vbat, [Output])
    self.pwr = self.Export(self.ic.vdd, [Power])
    self.gnd = self.Export(self.ic.vss, [Common])
    self.stat = self.Export(self.ic.stat)  # hi-Z when not charging, low when charging, high when done

    self.charging_current = self.ArgParameter(charging_current)

  def contents(self) -> None:
    super().contents()

    self.prog_res = self.Block(Resistor(1000 / self.charging_current))
    self.connect(self.prog_res.a, self.ic.prog)
    self.connect(self.prog_res.b.adapt_to(Ground()), self.gnd)
    self.assign(self.ic.charging_current, 1000 / self.prog_res.actual_resistance)
    self.require(self.prog_res.actual_resistance.within((2, 67)*kOhm), "prog must be within charge impedance range")

    self.vdd_cap = self.Block(  # not formally specified on the datasheet, but this is used in the reference board
      DecouplingCapacitor(4.7*uFarad(tol=0.10))
    ).connected(self.gnd, self.pwr)

    self.vbat_cap = self.Block(  # can be ceramic, tantalum, aluminum electrolytic
      DecouplingCapacitor(4.7*uFarad(tol=0.10))
    ).connected(self.gnd, self.pwr_bat)
