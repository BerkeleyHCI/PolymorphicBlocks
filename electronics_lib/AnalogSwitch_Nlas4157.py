from electronics_abstract_parts import *


class Nlas4157_Device(FootprintBlock):
  def __init__(self):
    super().__init__()

    self.pwr = self.Port(VoltageSink(
      voltage_limits=(1.65, 5.5)*Volt,
      current_draw=(0.5, 1.0)*uAmp,  # Icc, at 5.5v, typ to max
    ))
    self.gnd = self.Port(Ground())

    self.control = self.Port(DigitalSink(
      voltage_limits=(-0.5, 6)*Volt,
      current_draw=(-1, 1)*uAmp,  # input leakage current
      input_thresholds=(0.6, 2.4)*Volt,  # strictest of Vdd=2.7, 4.5 V
    ))


    # TBD analog parameters:
    # max analog voltage -0.5 to Vcc+0.5
    # max analog current limit 300mA continuous
    # switch on-resistance 0.3-4.3 ohm (typ and max, for all Vcc)

    self.com = self.Port(Passive())
    self.no = self.Port(Passive())
    self.nc = self.Port(Passive())

  def contents(self):
    super().contents()

    self.footprint(
      'U', 'Package_TO_SOT:SOT-363_SC-70-6',
      {
        '1': self.no,
        '2': self.gnd,
        '3': self.nc,
        '4': self.com,
        '5': self.pwr,
        '6': self.control,
      },
      mfr='ON Semiconductor', part='NLAS4157',
      datasheet='https://www.onsemi.com/pdf/datasheet/nlas4157-d.pdf'
    )


class Nlas4157(AnalogSwitch):
  def __init__(self):
    super().__init__()
