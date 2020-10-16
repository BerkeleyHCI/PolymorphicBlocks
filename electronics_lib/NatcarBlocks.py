from electronics_abstract_parts import *


class ServoConnector(Connector, CircuitBlock):
  @init_in_parent
  def __init__(self, voltage_limits: RangeLike = (4.5, 6.3)*Volt, current_draw: RangeLike = (0, 1)*Amp):
    # arbitrary initial voltage and current guesses
    # TODO a +5% tolerance was added to the voltage limit
    super().__init__()
    self.pwr = self.Port(ElectricalSink(
      voltage_limits=voltage_limits,
      current_draw=current_draw
    ))
    self.gnd = self.Port(Ground(), [Common])
    self.sig = self.Port(DigitalSink())  # TODO specs

  def contents(self):
    super().contents()
    self.footprint(
      'J', 'Connector_PinHeader_2.54mm:PinHeader_1x03_P2.54mm_Vertical',
      {
        '1': self.gnd,
        '2': self.pwr,
        '3': self.sig,
      },
      part='Header 3-pos',
      value='Servo'
    )


@abstract_block
class NatcarSubcircuit(Block):
  """Specialty subcircuit for the line-following robot car application"""
  pass


class FreescaleLineCameraConnector(NatcarSubcircuit, CircuitBlock):
  def __init__(self):
    super().__init__()
    self.vdd = self.Port(ElectricalSink(
      voltage_limits=(3, 5.5)*Volt  # based on TSL1401CL
      # TODO current specs
    ), [Power])
    self.gnd = self.Port(Ground(), [Common])

    self.aout = self.Port(AnalogSource(
      voltage_out=(0, self.vdd.link().voltage.upper()),
      impedance=0*Ohm(tol=0)  # TODO realistic impedance, datasheet does not specify output buffer P/N
    ))

    # digital IO models from TSL1401CL datasheet: https://www.mouser.com/datasheet/2/588/TSL1401CL-1214741.pdf
    dio_model = DigitalSink.from_supply(
      self.gnd, self.vdd,
      current_draw=(2.6, 4.5)*mAmp,  # from TSL1401CL only
      input_threshold_abs=(0.8, 2)*Volt
    )

    self.si = self.Port(dio_model)
    self.clk = self.Port(dio_model)

  def contents(self):
    super().contents()
    self.footprint(
      'J', 'Connector_PinHeader_2.54mm:PinHeader_1x05_P2.54mm_Vertical',
      {
        '1': self.aout,
        '2': self.si,
        '3': self.clk,
        '4': self.vdd,
        '5': self.gnd,
      },
      part='Header 5-pos',
      value='Camera',
      datasheet='https://community.nxp.com/docs/DOC-1058'
    )


class BeagleBoneBlueConnector(NatcarSubcircuit, Connector):
  def digital_model(self) -> DigitalBidir:
    return DigitalBidir(
      voltage_out=(0, 3.3)*Volt,
      voltage_limits=(-0.5, 3.3+0.3)*Volt,  # TODO dependent on toleranced source
      current_draw=(0, 0)*mAmp,
      current_limits=(-6, 6)*mAmp,
      input_thresholds=(0.8, 2)*Volt,
      output_thresholds=(0, 3.3)*Volt
    )

  def analog_model(self) -> AnalogSink:
    return AnalogSink(
      voltage_limits=(0, 1.8)*Volt,
      current_draw=(0, 0)*mAmp,
      impedance=(75.792, float('inf'))*kOhm  # at lowest impedance for maximum fs=200kHz, see Table 5-16
    )

class BeagleBoneBlueAdcConnector(BeagleBoneBlueConnector, CircuitBlock):
  def __init__(self):
    super().__init__()

    self.pwr = self.Port(ElectricalSource(
      voltage_out=(1.71, 1.88),  # VddA limits, p84, TODO tighter bounds
      # current_limits=(0, 0)*mAmp  # TODO current limits
    ), optional=True)
    self.gnd = self.Port(Ground(), [Common])

    ain_model = self.analog_model()
    self.ain0 = self.Port(ain_model, optional=True)
    self.ain1 = self.Port(ain_model, optional=True)
    self.ain2 = self.Port(ain_model, optional=True)
    self.ain3 = self.Port(ain_model, optional=True)

  def contents(self):
    super().contents()
    self.footprint(
      'J', 'Connector_JST:JST_SH_BM06B-SRSS-TB_1x06-1MP_P1.00mm_Vertical',
      {
        '1': self.gnd,
        '2': self.pwr,
        '3': self.ain0,
        '4': self.ain1,
        '5': self.ain2,
        '6': self.ain3,
      },
      mfr='JST', part='BM06B-SRSS-TB(LF)(SN)',
      value='BBBL ADC'
    )


class BeagleBoneBlueGpioConnector(BeagleBoneBlueConnector, CircuitBlock):
  def __init__(self):
    super().__init__()

    # Supplies 3.3V
    # Assume VddIO is 3.3v, IO specs from https://www.ti.com/lit/ds/symlink/am3358.pdf
    # DC electrical characteristics all other LVCMOS pins 3.3v

    self.pwr = self.Port(ElectricalSource(
      voltage_out=3.3 * Volt(tol=0),  # TODO tolerances
      # TODO current limits
    ), optional=True)
    self.gnd = self.Port(Ground(), [Common])  # TODO bidir GND

    dio_model = self.digital_model()
    self.gp0 = self.Port(dio_model, optional=True)
    self.gp1 = self.Port(dio_model, optional=True)
    self.gp2 = self.Port(dio_model, optional=True)
    self.gp3 = self.Port(dio_model, optional=True)

  def contents(self):
    super().contents()
    self.footprint(
      'J', 'Connector_JST:JST_SH_BM06B-SRSS-TB_1x06-1MP_P1.00mm_Vertical',
      {
        '1': self.gnd,
        '2': self.pwr,
        '3': self.gp0,
        '4': self.gp1,
        '5': self.gp2,
        '6': self.gp3,
      },
      mfr='JST', part='BM06B-SRSS-TB(LF)(SN)',
      value='BBBL GPIO'
    )


class BeagleBoneBlueGpsPwmConnector(BeagleBoneBlueConnector, CircuitBlock):
  def __init__(self):
    super().__init__()

    self.pwr = self.Port(ElectricalSource(
      voltage_out=5 * Volt(tol=0),  # TODO tolerances
      # TODO current limits
    ), optional=True)
    self.gnd = self.Port(Ground(), [Common])  # TODO bidir GND

    dio_model = self.digital_model()
    self.pwm0 = self.Port(dio_model, optional=True)
    self.pwm1 = self.Port(dio_model, optional=True)

  def contents(self):
    super().contents()
    self.footprint(
      'J', 'Connector_JST:JST_SH_BM06B-SRSS-TB_1x06-1MP_P1.00mm_Vertical',
      {
        # '1',  pin 1 is NC
        '2': self.gnd,
        '3': self.pwm0,
        '4': self.pwm1,
        '5': self.pwr,
        '6': self.gnd,
      },
      mfr='JST', part='BM06B-SRSS-TB(LF)(SN)',
      value='BBBL GPS'
    )


class BeagleBoneBlueDigitalPin(BeagleBoneBlueConnector, CircuitBlock):
  def __init__(self):
    super().__init__()
    self.io = self.Port(self.digital_model(), optional=True)

  def contents(self):
    super().contents()
    self.footprint(
      'J', 'Connector_PinHeader_2.54mm:PinHeader_1x01_P2.54mm_Vertical',
      {
        '1': self.io,
      },
      part='Header 1-pos',
      value='Servo PWM'
    )


class NatcarPowerTerminal(Connector, NatcarSubcircuit, CircuitBlock):
  def __init__(self):
    super().__init__()
    self.port = self.Port(Passive())

  def contents(self):
    super().contents()
    self.footprint(
      'J', 'calisco:ScrewTerminal_M3_RA_Keystone7761',
      {
        '1': self.port
      },
      mfr='Keystone', part='7761',
    )


class NatcarBatteryConnector(Connector, NatcarSubcircuit, Block):
  def __init__(self):
    super().__init__()

    self.pwr = self.Port(ElectricalSource(
      voltage_out=(3.0*3, 4.2*3)*Volt,
      current_limits=(0, 15)*Amp  # TODO better modeling
    ))
    self.gnd = self.Port(GroundSource())

  def contents(self):
    super().contents()
    self.pwr_conn = self.Block(NatcarPowerTerminal())
    self.connect(self.pwr_conn.port.as_electrical_source(), self.pwr)
    self.gnd_conn = self.Block(NatcarPowerTerminal())
    self.connect(self.gnd_conn.port.as_ground_source(), self.gnd)

class NatcarBrushedMotorConnector(Connector, NatcarSubcircuit, Block):
  def __init__(self):
    super().__init__()
    self.a = self.Port(DigitalSink(
      current_draw=(-10, 10)*Amp
    ))  # TODO better modeling
    self.b = self.Port(Ground())  # TODO allow full-bridge instead of fixed ground - problem is drawing current from gnd

  def contents(self):
    super().contents()
    self.a_conn = self.Block(NatcarPowerTerminal())
    self.connect(self.a, self.a_conn.port.as_digital_sink())
    self.b_conn = self.Block(NatcarPowerTerminal())
    self.connect(self.b, self.b_conn.port.as_ground())


class Ucc21222_Device(DiscreteChip, CircuitBlock):
  def __init__(self):
    super().__init__()
    self.vcci = self.Port(ElectricalSink(
      voltage_limits=(3, 5.5)*Volt,  # recommended operating conditions
      current_draw=(1.5, 2.5)*mAmp  # datasheet table 6.9 typ quiescent -> typ operating
    ))
    self.gnd = self.Port(Ground())

    din_model = DigitalSink.from_supply(self.gnd, self.vcci,
                                        voltage_limit_tolerance=(-0.5, 0.5),
                                        current_draw=(0, 0)*mAmp,
                                        input_threshold_abs=(0.8, 2)*Volt)  # worst case thresholds from datasheet table 6.9

    self.ina = self.Port(din_model)
    self.inb = self.Port(din_model)

    self.dis = self.Port(din_model)  # disable pin
    self.dt = self.Port(Passive())  # programmable deadtime, connect a RC network to set deadtime

    # TODO make these not passive, while accounting for bootstrapped connection
    # iso_pwr_model = ElectricalSink(
    #   voltage_limits=(9.2, 18)*Volt,
    #   current_draw=(1.0, 2.5)*mAmp  # datasheet table 6.9 typ quiescent -> typ operating
    # )
    # self.vdda = self.Port(iso_pwr_model)
    # self.vddb = self.Port(iso_pwr_model)
    #
    # iso_gnd_model = Ground()
    # self.vssa = self.Port(iso_gnd_model)  # TODO can be floating
    # self.vssb = self.Port(iso_gnd_model)  # TODO can be floating
    #
    # self.outa = self.Port(DigitalSource.from_supply(self.vssa, self.vdda,
    #                                                 current_limits=(-6, 4)*Amp))  # is a peak rating
    # self.outb = self.Port(DigitalSource.from_supply(self.vssb, self.vddb,
    #                                                 current_limits=(-6, 4)*Amp))  # is a peak rating

    self.vssa = self.Port(Passive())
    self.vssb = self.Port(Passive())
    self.vdda = self.Port(Passive())
    self.vddb = self.Port(Passive())
    self.outa = self.Port(Passive())
    self.outb = self.Port(Passive())


  def contents(self):
    super().contents()
    self.footprint(
      'U', 'Package_SO:SOIC-16_3.9x9.9mm_P1.27mm',
      {
        '1': self.ina,
        '2': self.inb,
        '3': self.vcci,
        '4': self.gnd,
        '5': self.dis,
        '6': self.dt,
        # 7 is NC
        '8': self.vcci,
        '9': self.gnd,
        '10': self.outb,
        '11': self.vddb,
        # 12, 13 are NC
        '14': self.vssa,
        '15': self.outa,
        '16': self.vdda
      },
      mfr='Texas Instruments', part='UCC21222',
      datasheet='https://www.ti.com/lit/ds/symlink/ucc21222-q1.pdf'
    )


class Ucc21222_HalfbridgeDriver(IntegratedCircuit, GeneratorBlock):  # TODO better categorization
  @init_in_parent
  def __init__(self, drive_current: RangeExpr=(3, 4)*Amp, deadtime: RangeExpr=(190, 240)*nSecond,  # TODO asymmetric drive currents
               bootstrap_voltage: RangeExpr=(0, 0.4)*Volt):
    super().__init__()

    self.drive_current = self.Parameter(RangeExpr(drive_current))
    self.deadtime = self.Parameter(RangeExpr(deadtime))
    self.bootstrap_voltage = self.Parameter(RangeExpr(bootstrap_voltage))

    # TODO these should be exported, but unclear how to resolve them with generator skeleton / impl
    # self.pwr = self.Export(self.ic.vcci, [Power])
    # self.gnd = self.Export(self.ic.gnd, [Common])
    #
    # self.ina = self.Export(self.ic.ina)  # high side driver
    # self.inb = self.Export(self.ic.inb)  # low side driver
    # self.dis = self.Export(self.ic.dis)

    self.pwr = self.Port(ElectricalSink(), [Power])
    self.gnd = self.Port(Ground(), [Common])

    self.ina = self.Port(DigitalSink())  # high side driver
    self.inb = self.Port(DigitalSink())  # low side driver
    self.dis = self.Port(DigitalSink())

    self.pwr_hv = self.Port(ElectricalSink())  # required to spec out the bootstrap diode
    self.drv_common = self.Port(ElectricalSink())  # TODO parameter directionality flow?, TODO should be Digital?
    # self.pwr_drv = self.Export(self.ic.vddb)  # optionally isolated
    # self.gnd_drv = self.Export(self.ic.vssb)

    self.pwr_drv = self.Port(ElectricalSink())
    self.gnd_drv = self.Port(Ground())

    self.outa = self.Port(DigitalSource(
      current_limits=(drive_current.lower() * -1, drive_current.lower())
    ))
    self.outb = self.Port(DigitalSource(
      current_limits=(drive_current.lower() * -1, drive_current.lower())
    ))

  def generate(self) -> None:
    super().generate()

    self.ic = self.Block(Ucc21222_Device())
    self.connect(self.pwr, self.ic.vcci)
    self.connect(self.gnd, self.ic.gnd)
    self.connect(self.ina, self.ic.ina)
    self.connect(self.inb, self.ic.inb)
    self.connect(self.dis, self.ic.dis)
    # self.connect(self.pwr_drv, self.ic.vddb.as_electrical_sink())  # assigned below to avoid making two adapters
    # self.connect(self.gnd_drv, self.ic.vssb.as_electrical_sink())  # assigned below to avoid making two adapters

    # self.pwr_drv = self.Export(self.ic.vddb)  # optionally isolated
    # self.gnd_drv = self.Export(self.ic.vssb)

    # TODO datasheet section 9.2.2.2: optional Rin/Cin filter, for ringing from layout

    dt_res_range = (self.get(self.deadtime.lower()) * 1e9 * 1e3 / 10, self.get(self.deadtime.upper()) * 1e9 * 1e3 / 10)
    self.dt_res = self.Block(Resistor(resistance=dt_res_range*Ohm))
    self.dt_cap = self.Block(Capacitor(capacitance=2.2*nFarad(tol=0.2), voltage=(0, 5.5)*Volt))  # guess from Vcci ratings
    self.connect(self.dt_cap.pos, self.dt_res.a, self.ic.dt)
    self.connect(self.dt_cap.neg.as_ground(), self.dt_res.b.as_ground(), self.gnd)

    self.vcci_cap = self.Block(DecouplingCapacitor(capacitance=0.1*uFarad(tol=0.2)))  # datasheet 9.2.2.8.1 TODO: voltage rating
    self.connect(self.vcci_cap.pwr, self.ic.vcci)
    self.connect(self.vcci_cap.gnd, self.ic.gnd)

    vddx_cap_model = DecouplingCapacitor(capacitance=1*uFarad(tol=0.2))  # datasheet 9.2.2.8.2 to allow derating, TODO voltage rating
    self.vddb_cap = self.Block(vddx_cap_model)
    self.connect(self.pwr_drv, self.vddb_cap.pwr, self.ic.vddb.as_electrical_sink())
    self.connect(self.gnd_drv, self.vddb_cap.gnd, self.ic.vssb.as_ground())

    drive_voltage_min, drive_voltage_max = self.get(self.pwr_drv.link().voltage)
    hv_voltage_min, hv_voltage_max = self.get(self.pwr_hv.link().voltage)
    bootstrap_drop_min, bootstrap_drop_max = self.get(self.bootstrap_voltage)
    self.boot_dio = self.Block(Diode(
      reverse_voltage=(0, hv_voltage_max - drive_voltage_min)*Volt,
      current=(0, 1)*Amp,  # TODO kind of an arbitrary spec
      voltage_drop=self.bootstrap_voltage,
      reverse_recovery_time=(0, 500) * nSecond  # guess from Digikey's classification for "fast recovery"
    ))
    drive_current_min, drive_current_max = self.get(self.drive_current)
    bootstrap_res_max = (drive_voltage_max - bootstrap_drop_min) / drive_current_min
    bootstrap_res_min = (drive_voltage_min - bootstrap_drop_max) / drive_current_max
    self.boot_res = self.Block(Resistor(resistance=(bootstrap_res_min, bootstrap_res_max)*Ohm))
    self.connect(self.pwr_drv, self.boot_res.a.as_electrical_sink())
    self.connect(self.boot_res.b, self.boot_dio.anode)
    self.vdda_cap = self.Block(vddx_cap_model)
    self.connect(self.boot_dio.cathode.as_electrical_source(), self.vdda_cap.pwr, self.ic.vdda.as_electrical_sink())
    self.constrain(self.vdda_cap.pwr.link().voltage == self.pwr_drv.link().voltage, unchecked=True)  # TODO account for diode drop  TODO model w/ bootstrap adapter
    self.connect(self.drv_common, self.vdda_cap.gnd, self.ic.vssa.as_electrical_sink(current_draw=(0, 0)*Amp))  # TODO actually model power draw

    # calculate required resistances based on datasheet section 9.2.2.5
    # TODO account for FET gate resistance too?
    DRIVER_HIGH_RESISTANCE = 1/(1/1.47 + 1/5)
    DRIVER_LOW_RESISTANCE = 0.55
    drive_a_res_max = (drive_voltage_max - bootstrap_drop_min) / drive_current_min
    drive_a_res_min = (drive_voltage_min - bootstrap_drop_max) / drive_current_max
    drive_b_res_max = (drive_voltage_max) / drive_current_min
    drive_b_res_min = (drive_voltage_min) / drive_current_max

    drive_a_high_res_range = (drive_a_res_min - DRIVER_HIGH_RESISTANCE, drive_a_res_max - DRIVER_HIGH_RESISTANCE)
    drive_a_low_res_range = (drive_a_res_min - DRIVER_LOW_RESISTANCE, drive_a_res_max - DRIVER_LOW_RESISTANCE)
    drive_b_high_res_range = (drive_b_res_min - DRIVER_HIGH_RESISTANCE, drive_b_res_max - DRIVER_HIGH_RESISTANCE)
    drive_b_low_res_range = (drive_b_res_min - DRIVER_LOW_RESISTANCE, drive_b_res_max - DRIVER_LOW_RESISTANCE)

    drive_res_min = max(drive_a_high_res_range[0], drive_a_low_res_range[0],
                        drive_b_high_res_range[0], drive_b_low_res_range[0])
    drive_res_max = min(drive_a_high_res_range[1], drive_a_low_res_range[1],
                        drive_b_high_res_range[1], drive_b_low_res_range[1])
    assert drive_res_min <= drive_res_max, \
      f"can't reconcile gate resistors to meet gate current target {(drive_current_min, drive_current_max)}: " \
      f"a high range {drive_a_high_res_range}, a low range {drive_a_low_res_range}" \
      f"b high range {drive_b_high_res_range}, b low range {drive_b_low_res_range}"

    self.a_gate_res = self.Block(Resistor(
      resistance=(drive_res_min, drive_res_max)*Ohm
    ))
    self.connect(self.ic.outa.as_digital_source(), self.a_gate_res.a.as_digital_sink())
    self.connect(self.a_gate_res.b.as_digital_source(), self.outa)

    self.b_gate_res = self.Block(Resistor(
      resistance=(drive_res_min, drive_res_max)*Ohm
    ))
    self.connect(self.ic.outb.as_digital_source(), self.b_gate_res.a.as_digital_sink())
    self.connect(self.b_gate_res.b.as_digital_source(), self.outb)
    # TODO propagate actual currents to digital outs
