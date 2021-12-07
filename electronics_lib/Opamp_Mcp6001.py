from electronics_abstract_parts import *


class Mcp6001_Device(DiscreteChip, FootprintBlock):
  def __init__(self):
    super().__init__()
    self.vcc = self.Port(VoltageSink(
      voltage_limits=(1.8, 6.0)*Volt, current_draw=(50, 170)*uAmp
    ), [Power])
    self.vss = self.Port(Ground(), [Common])

    analog_in_model = AnalogSink(
      voltage_limits=(-0.3, self.vcc.link().voltage.lower() + 0.3),
      impedance=1e13*Ohm(tol=0),  # no tolerance bounds given on datasheet
      current_draw=(0, 0)*pAmp  # TODO: should bias current be modeled here?
    )
    self.vinp = self.Port(analog_in_model)
    self.vinn = self.Port(analog_in_model)
    self.vout = self.Port(AnalogSource(
      (0.25, self.vcc.link().voltage.lower() - 0.25),
      current_limits=(-6, 6)*mAmp,  # for Vdd=1.8, 23mA for Vdd=5.5
      impedance=300*Ohm(tol=0)  # no tolerance bounds given on datasheet
    ))

  def contents(self):
    super().contents()
    self.footprint(
      'U', 'Package_TO_SOT_SMD:SOT-23-5',
      {
        '1': self.vout,
        '2': self.vss,
        '3': self.vinp,
        '4': self.vinn,
        '5': self.vcc,
      },
      mfr='Microchip Technology', part='MCP6001T-I/OT',
      datasheet='https://ww1.microchip.com/downloads/en/DeviceDoc/21733j.pdf'
    )


class Mcp6001(Opamp):
  """MCP6001 op-amp in SOT-23-5
  """
  def contents(self):
    super().contents()

    self.ic = self.Block(Mcp6001_Device())
    self.connect(self.inn, self.ic.vinn)
    self.connect(self.inp, self.ic.vinp)
    self.connect(self.out, self.ic.vout)
    self.connect(self.pwr, self.ic.vcc)
    self.connect(self.gnd, self.ic.vss)

    with self.implicit_connect(
        ImplicitConnect(self.pwr, [Power]),
        ImplicitConnect(self.gnd, [Common])
    ) as imp:
      self.vdd_cap0 = imp.Block(DecouplingCapacitor(
        capacitance=0.1*uFarad(tol=0.2),
      ))
