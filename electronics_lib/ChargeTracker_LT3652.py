from electronics_abstract_parts import *


class ChargeTracker_LT3652(DiscreteChip, CircuitBlock):
  def __init__(self):
    super().__init__()

    # only required pins are Vcc, GND, DOUT, DIN
    # also need RTS, DTR for serial firmware updates
    # DNC pins that are not in use
    self.vin = self.Port(ElectricalSink(
      voltage_limits=(4.95, 32) * Volt,
      current_draw=(0, 3.5) * mAmp  # 2.5uA sleep, 29mA receive, 290 mA max transmit
    ), [Power])
    self.gnd = self.Port(Ground(), [Common])

    digital_model = DigitalBidir.from_supply(
      self.gnd, self.vin,
      voltage_limit_tolerance=(-0.3, 0.3)*Volt,  # TODO speculative default
      current_draw=(0, 0),  # TODO actually an unspecified default
      current_limits=(-2, 2) * mAmp,
      input_threshold_factor=(0.3, 0.7),
      output_threshold_factor=(0.05, 0.95)
    )

    adc_model = AnalogSink(
      voltage_limits=(2.65, 2.75) * Volt,
      current_draw=(35, 100) * nAmp,
      impedance=100*kOhm  # TODO no specs
    )

    pull_up_model = DigitalSink.from_supply(
      self.vin, self.gnd,
      voltage_limit_tolerance=(-0.3, 0.3)*Volt,  # TODO: FIX
      current_draw=(0, 0)*Amp,
      input_threshold_abs=(0.8, 2)*Volt
    )  # TODO: FIX

    self.data = self.Port(UartPort(digital_model), [Input])

    self.rssi = self.Port(DigitalSource(digital_model), optional=True)
    self.associate = self.Port(DigitalSource(digital_model), optional=True)

    self.vin_reg = self.Port(AnalogSink(adc_model), optional=True)
    # self.nshdn = self.Port(DigitalSink(pull_up_model), optional=True)

  def contents(self):
    super().contents()
    self.footprint(
      'U', 'Sparkfun_RF:XBEE',
      {
        '1': self.vin,
        '2': self.vin_reg,
        # '3': self.nshdn,
        # '4': self.nchrg,
        # '5': self.nfault,
        # '6': self.timer,
        # '7': self.vfb,
        # '8': self.ntc,
        # '9': self.bat,
        # '10': self.sense,
        # '11': self.boost,
        # '12': self.sw,
        '13': self.gnd,
      },
      # mfr='Digi International', part='XBP9B-*',
      # datasheet='https://www.digi.com/resources/documentation/digidocs/pdfs/90002173.pdf'
    )
