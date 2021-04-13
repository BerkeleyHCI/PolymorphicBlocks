from electronics_abstract_parts import *
from electronics_lib import SmtInductor, SmtDiode
from electronics_model.VoltagePorts import VoltageSinkAdapterAnalogSource


class SolarCharger_LT3652(DiscreteChip, FootprintBlock):
  def __init__(self):
    super().__init__()

    self.gnd = self.Port(Ground(), [Common])

    self.vin = self.Port(
      VoltageSink(
        voltage_limits=(4.95, 32) * Volt,
        current_draw=(0, 3.5) * mAmp
      ), [Power])

    self.vin_reg = self.Port(
      AnalogSink(
        voltage_limits=(0, 40) * Volt,
        current_draw=(0, 100) * nAmp
      ), optional=True
    )

    pull_up_model = DigitalSink.from_supply(
      self.gnd, self.vin,
      voltage_limit_tolerance=(0, 0.5) * Volt,
      current_draw=(-10, 0) * nAmp,
      input_threshold_abs=(0.4, 1.2) * Volt
    )

    self.nshdn = self.Port(DigitalSink(pull_up_model), optional=True)
    self.nchrg = self.Port(DigitalSink(pull_up_model), optional=True)
    self.nfault = self.Port(DigitalSink(pull_up_model), optional=True)

    self.timer = self.Port(
      VoltageSink(
        voltage_limits=(0, 2.5) * Volt,
        current_draw=(0, 25) * uAmp
      ), optional=True
    )

    self.vfb = self.Port(
      AnalogSink(
        voltage_limits=(0, 5) * Volt,
        current_draw=(0, 3.5) * nAmp
      ), optional=True
    )

    self.ntc = self.Port(
      VoltageSource(
        voltage_out=(0, 2.5) * Volt,
        current_limits=(0, 52.5) * uAmp
      ), optional=True
    )

    self.bat = self.Port(
      VoltageSink(
        voltage_out=(0, 0.5) * Volt,
        current_limits=(0, 1) * uAmp
      ), optional=True
    )

    self.sense = self.Port(
      VoltageSink(
        voltage_limits=(0, 0.5) * Volt,
        current_draw=(0, 1) * uAmp
      ), optional=True
    )

    self.boost = self.Port(
      VoltageSink(
        voltage_limits=(0, 50) * Volt,
        current_draw=(0, 36) * Amp
      ), optional=True
    )

    self.sw = self.Port(
      VoltageSource(
        voltage_out=(0, 40) * Volt,
        current_limits=(0, 36) * Amp
      ), optional=True
    )

  def contents(self):
    super().contents()
    self.footprint(
      'U', 'LT3652',
      {
        '1': self.vin,
        '2': self.vin_reg,
        '3': self.nshdn,
        '4': self.nchrg,
        '5': self.nfault,
        '6': self.timer,
        '7': self.vfb,
        '8': self.ntc,
        '9': self.bat,
        '10': self.sense,
        '11': self.boost,
        '12': self.sw,
        '13': self.gnd,
      },
      mfr='Analog Devices Inc', part='LT3652EMSE',
      datasheet='https://www.analog.com/media/en/technical-documentation/data-sheets/3652fe.pdf'
    )


class SolarCharger_LT3652_Module(FootprintBlock):
  @init_in_parent
  def __init__(self,
               max_charge_current: FloatLike = FloatExpr(),
               inductor_ripple_current: FloatLike = FloatExpr(),
               output_battery_float_voltage: FloatLike = FloatExpr(),
               vin_max: FloatLike = FloatExpr(),) -> None:
    super().__init__()
    self.gnd = self.Port(Ground())

    self.vin = self.Port(
      VoltageSink(
        voltage_limits=(4.95, 32) * Volt,
        current_draw=(0, 3.5) * mAmp
      ), [Power]
    )

    self.vout = self.Port(
      VoltageSource(
        voltage_out=(0, 0.5) * Volt,
        current_limits=(0, 1) * uAmp
      )
    )


    self.max_charge_current = max_charge_current
    self.rsense = 0.1/max_charge_current
    self.ind_val = ((10 * self.rsense)/(inductor_ripple_current/max_charge_current)) * output_battery_float_voltage * (1 - (output_battery_float_voltage/vin_max)) * 10e-6

  def contents(self) -> None:
    super().contents()
    self.solar_charger = self.Block(SolarCharger_LT3652())

    self.timer_cap = self.Block(Capacitor(capacitance=0 * uFarad))
    self.vin_cap = self.Block(Capacitor(capacitance=10 * uFarad))
    self.sw_boost_cap = self.Block(Capacitor(capacitance=1 * uFarad))
    self.bat_boost_diode = self.Block(Diode())
    self.gnd_sw_diode = self.Block(Diode())
    self.sense_res = self.Block(CurrentSenseResistor(resistance=self.rsense))
    self.bat_cap = self.Block(Capacitor(capacitance=10 * uFarad))
    self.ind = self.Block(Inductor(inductance=self.ind_val))
    self.vin_diode = self.Block(Diode())
    self.vin_vd = self.Block(VoltageDivider(output_voltage=2.7 * Volt, impedance=250 * kOhm(tol=0.10)))
    self.bat_vd = self.Block(VoltageDivider(output_voltage=3.3 * Volt, impedance=250 * kOhm(tol=0.10)))

    self.footprint(
      'U', 'SolarCharger_LT3652_Module',
      {
        '1': self.gnd,
        '2': self.vin,
        '3': self.vout,
      }
    )
    # i/o connections
    self.connect(self.solar_charger.gnd, self.gnd)
    self.connect(self.vin, self.vin_diode.anode.as_voltage_sink())
    self.connect(self.solar_charger.vin, self.vin_diode.cathode.as_voltage_sink())
    self.connect(self.solar_charger.bat, self.vout)

    # timer
    self.connect(self.solar_charger.timer, self.timer_cap.pos.as_voltage_sink())
    self.connect(self.gnd, self.timer_cap.neg.as_ground())

    # vin cap
    self.connect(self.vin, self.vin_cap.pos.as_voltage_sink())
    self.connect(self.gnd, self.vin_cap.neg.as_ground())

    # vin voltage divider
    self.connect(self.gnd, self.vin_vd.gnd)
    self.connect(self.vin, self.vin_vd.input)
    self.connect(self.solar_charger.vin_reg, self.vin_vd.output)

    # sw boost cap
    self.connect(self.solar_charger.boost, self.sw_boost_cap.neg.as_voltage_sink())
    self.connect(self.solar_charger.sw, self.sw_boost_cap.pos.as_voltage_sink())

    # bat boost diode
    self.connect(self.solar_charger.boost, self.bat_boost_diode.cathode.as_voltage_sink())
    self.connect(self.solar_charger.bat, self.bat_boost_diode.anode.as_voltage_sink())

    # gnd sw diode
    self.connect(self.solar_charger.sw, self.gnd_sw_diode.cathode.as_voltage_sink())
    self.connect(self.gnd, self.gnd_sw_diode.anode.as_ground())

    # bat voltage divider
    self.connect(self.gnd, self.bat_vd.gnd)
    self.connect(self.solar_charger.bat, self.bat_vd.input)
    self.connect(self.solar_charger.vfb, self.bat_vd.output)

    # bat cap
    self.connect(self.vout, self.bat_cap.pos.as_voltage_sink())
    self.connect(self.gnd, self.bat_cap.neg.as_ground())

    # ind
    self.connect(self.gnd_sw_diode.cathode, self.ind.a)
    self.connect(self.solar_charger.sense, self.ind.b.as_voltage_sink())

    # vin nshdn
    # self.connect(self.solar_charger.vin, self.solar_charger.nshdn)

    # current sense resistor
    self.connect(self.solar_charger.sense, self.sense_res.pwr_out)
    self.connect(self.solar_charger.bat, self.sense_res.pwr_in)