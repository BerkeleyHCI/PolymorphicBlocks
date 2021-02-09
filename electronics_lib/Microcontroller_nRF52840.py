from typing import *
from itertools import chain

from electronics_abstract_parts import *


@abstract_block
class nRF52840_Device(DiscreteChip, CircuitBlock):
  DIO0_PINS = [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 18, 19, 21, 23, 25, 26, 27, 28, 29, 30, 31]
  DIO1_PINS = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15]
  ADC0_PINS = [2, 3, 4, 5, 28, 29, 30, 31]

  @init_in_parent
  def __init__(self) -> None:
    super().__init__()
    #
    # Common Ports
    # https://infocenter.nordicsemi.com/pdf/nRF52840_PS_v1.2.pdf
    # https://media.digikey.com/pdf/Data%20Sheets/Adafruit%20PDFs/4481_Web.pdf
    #
    self.vdd = self.Port(ElectricalSink(
      voltage_limits=(1.7, 3.6) * Volt,
      current_draw=(0, 5)*mAmp,
    ), [Power])
    self.vss = self.Port(Ground(), [Common])

    #
    # Port Models
    #
    # TODO use all these models once there is a strategy for Analog/Digital capable IOs
    self.dio_3v_model = (DigitalBidir(
      voltage_limits=(0, 3.3) * Volt,
      current_draw=(0, 0) * Amp,
      voltage_out=(0 * Volt, self.vdd.link().voltage.upper()),
      current_limits=(-50, 45) * mAmp,  # TODO this uses short circuit current, which might not be useful, better to model as resistance?
      input_thresholds=(0.3 * self.vdd.link().voltage.lower(),
                        0.7 * self.vdd.link().voltage.upper()),
      output_thresholds=(0 * Volt, self.vdd.link().voltage.lower()),
      pullup_capable=True, pulldown_capable=True
    ), )  # TODO hax tuple wrapper to prevent unbound error
    dio_3v_model = self.dio_3v_model[0]

    self.i2c_model = (DigitalBidir(  # TODO this isn't true bidir, this is an open-drain port
      voltage_limits=(0 * Volt, self.vdd.link().voltage.upper()),  # no value defined for I2C, use defaults
      current_draw=(0, 0) * Amp,
      voltage_out=(0 * Volt, self.vdd.link().voltage.upper()),
      current_limits=(-20, 0) * mAmp,  # I2C is sink-only
      input_thresholds=(0.3 * self.vdd.link().voltage.lower(),
                        0.7 * self.vdd.link().voltage.upper()),
      output_thresholds=(0 * Volt, self.vdd.link().voltage.lower())  # TODO can't source voltage
    ), )  # TODO hax tuple wrapper to prevent unbound error

    self.analog_model = (AnalogSink(
      voltage_limits=(0, self.vdd.link().voltage.upper()),
      current_draw=(0, 0) * Amp,
      impedance=(100, float('inf')) * kOhm
    ), )  # TODO hax tuple wrapper to prevent unbound error
    analog_model = self.analog_model[0]

    #
    # System Ports
    #
    self.swd_swdio = self.Port(DigitalBidir(dio_3v_model))
    self.swd_swclk = self.Port(DigitalSink(dio_3v_model))
    self.swd_swo = self.Port(DigitalSource(dio_3v_model))
    self.swd_reset = self.Port(DigitalSink(dio_3v_model))

    self.xtal = self.Port(CrystalDriver(frequency_limits=(1, 25)*MHertz, voltage_out=self.vdd.link().voltage), optional=True)  # Table 15, 32, 33
    # TODO Table 32, model crystal load capacitance and series resistance ratings
    self.xtal_rtc = self.Port(CrystalDriver(frequency_limits=(32, 33)*kHertz, voltage_out=self.vdd.link().voltage), optional=True)  # Assumed from "32kHz crystal" in 14.5

    #
    # User IOs
    #
    self.system_pins: Dict[str, CircuitPort]
    self.io_pins: Dict[str, Passive]

    self.pio0 = ElementDict[Passive]()
    self.pio1 = ElementDict[Passive]()

    self.usb_0 = self.Port(UsbDevicePort(), optional=True)
    self.i2c_0 = self.Port(I2cMaster(self.i2c_model[0]), optional=True)

    for i in chain(range(17), range(18, 20), [23], range(25, 32)):
      self.pio0[i] = self.Port(Passive(), optional=True)

    for i in chain(range(1, 16)):
      self.pio1[i] = self.Port(Passive(), optional=True)

    self.system_pins: Dict[str, CircuitPort] = {
      'VDD': self.vdd,
      'VSS': self.vss,

      'nRESET': self.swd_reset,
      'SWDIO': self.swd_swdio,
      'SWDCLK': self.swd_swclk,
      'TRACEDATA0': self.swd_swo,

      'D+': self.usb_0.dp,
      'D-': self.usb_0.dm,
    }

  def contents(self) -> None:
    super().contents()
    self.footprint(
      'U', 'Package_QFP:LQFP-64_10x10mm_P0.5mm',
      dict(chain(self.system_pins.items(), self.io_pins.items())),
      mfr='NXP', part='LPC1549JBD64',
      datasheet='https://www.nxp.com/docs/en/data-sheet/LPC15XX.pdf'
    )


@abstract_block
class nRF52840(Microcontroller, AssignablePinBlock):  # TODO refactor with _Device
  """
  LPC1549JBD48 (QFP-48) microcontroller, Cortex-M3
  https://www.nxp.com/docs/en/data-sheet/LPC15XX.pdf
  """
  DEVICE: Type[nRF52840_Device] = nRF52840_Device

  @init_in_parent
  def __init__(self) -> None:
    super().__init__()
    self.ic = self.Block(self.DEVICE())

    self.pwr = self.Export(self.ic.vdd)
    self.gnd = self.Export(self.ic.vss)
    self.swd = self.Port(SwdTargetPort())  # TODO
    #
    # IO models
    # TODO models should be in the _Device block, but need to figure how to handle Analog/Digital capable pins first
    #
    dio_3v_model = DigitalBidir(
      voltage_limits=(0, 3.3) * Volt,
      current_draw=(0, 0) * Amp,
      voltage_out=(0 * Volt, self.pwr.link().voltage.upper()),
      current_limits=(-50, 45) * mAmp,  # TODO this uses short circuit current, which might not be useful, better to model as resistance?
      input_thresholds=(0.3 * self.pwr.link().voltage.lower(),
                        0.7 * self.pwr.link().voltage.upper()),
      output_thresholds=(0 * Volt, self.pwr.link().voltage.lower())
    )

    i2c_model = DigitalBidir(  # TODO this isn't true bidir, this is an open-drain port
      voltage_limits=(0 * Volt, self.pwr.link().voltage.upper()),  # no value defined for I2C, use defaults
      current_draw=(0, 0) * Amp,
      voltage_out=(0 * Volt, self.pwr.link().voltage.upper()),
      current_limits=(-20, 0) * mAmp,  # I2C is sink-only
      input_thresholds=(0.3 * self.pwr.link().voltage.lower(),
                        0.7 * self.pwr.link().voltage.upper()),
      output_thresholds=(0 * Volt, self.pwr.link().voltage.lower())  # TODO can't source voltage
    )

    # TODO these should be array types?
    # TODO model current flows from digital ports
    self.digital = ElementDict[DigitalBidir]()
    for i in range(20):
      self.digital[i] = self.Port(dio_3v_model, optional=True)
      self._add_assignable_io(self.digital[i])

    self.i2c_0 = self.Port(I2cMaster(i2c_model), optional=True)
    self.connect(self.i2c_0, self.ic.i2c_0)
    # self._add_assignable_io(self.i2c_0)  # TODO conflicts with pin assign

    self.usb_0 = self.Port(UsbDevicePort(), optional=True)
    self.connect(self.usb_0, self.ic.usb_0)
    # self._add_assignable_io(self.usb_0)  # TODO conflicts with pin assign

    io_draw_expr = (0, 0)*mAmp
    for _, io in self.digital.items():
      io_draw_expr = io_draw_expr + io.is_connected().then_else(
        io.link().current_drawn.intersect((0, float('inf'))*Amp),  # only count sourced current
        (0, 0)*Amp)
    self._io_draw = self.Parameter(RangeExpr(io_draw_expr))
    self.io_draw = self.Block(ElectricalLoad(
      voltage_limit=(-float('inf'), float('inf')),
      current_draw=self._io_draw
    ))
    self.connect(self.pwr, self.io_draw.pwr)
    self.constrain(self.pwr.current_draw.within(self._io_draw + (0, 19)*mAmp))  # TODO fast prop so we can bound it before generation

  def generate(self) -> None:
    #
    # Reference Circuit Block
    #
    # TODO associate capacitors with a particular Vdd, Vss pin
    self.pwr_cap = ElementDict[DecouplingCapacitor]()
    with self.implicit_connect(
      ImplicitConnect(self.pwr, [Power]),
      ImplicitConnect(self.gnd, [Common])
    ) as imp:
      # one set of 0.1, 0.01uF caps for each Vdd, Vss pin, per reference schematic
      for i in range(3):
        self.pwr_cap[i*2] = imp.Block(DecouplingCapacitor(0.1 * uFarad(tol=0.2)))
        self.pwr_cap[i*2+1] = imp.Block(DecouplingCapacitor(0.01 * uFarad(tol=0.2)))
      self.vbat_cap = imp.Block(DecouplingCapacitor(0.1 * uFarad(tol=0.2)))

    self.pwra_cap = ElementDict[DecouplingCapacitor]()
    self.vref_cap = ElementDict[DecouplingCapacitor]()
    with self.implicit_connect(
        ImplicitConnect(self.pwr, [Power]),
        ImplicitConnect(self.gnd, [Common])
    ) as imp:
      # one set of 0.1, 10uF caps for each VddA, VssA pin, per reference schematic
      self.pwra_cap[0] = imp.Block(DecouplingCapacitor(0.1 * uFarad(tol=0.2)))
      self.pwra_cap[1] = imp.Block(DecouplingCapacitor(10 * uFarad(tol=0.2)))

      self.vref_cap[0] = imp.Block(DecouplingCapacitor(0.1 * uFarad(tol=0.2)))
      self.vref_cap[1] = imp.Block(DecouplingCapacitor(0.1 * uFarad(tol=0.2)))
      self.vref_cap[2] = imp.Block(DecouplingCapacitor(10 * uFarad(tol=0.2)))

    with self.implicit_connect(
        ImplicitConnect(self.pwr, [Power]),
        ImplicitConnect(self.gnd, [Common])
    ) as imp:
      self.swdio_pull = imp.Block(PullupResistor((10, 100) * kOhm(tol=0.05)))
      self.connect(self.swdio_pull.io, self.swd.swdio, self.ic.swd_swdio)
      self.swclk_pull = imp.Block(PulldownResistor((10, 100) * kOhm(tol=0.05)))
      self.connect(self.swclk_pull.io, self.swd.swclk, self.ic.swd_swclk)
      self.reset_pull = imp.Block(PullupResistor(10 * kOhm(tol=0.05)))
      self.connect(self.reset_pull.io, self.swd.reset, self.ic.swd_reset)
      self.connect(self.swd.swo, self.ic.swd_swo)

    # TODO capacitive divider in CLKIN mode; in XO mode see external load capacitors table, see LPC15XX 14.3

    #
    # Pin Assignment Block
    #
    assigned_pins = PinAssignmentUtil(
      AnyPinAssign([port for port in self._all_assignable_ios if isinstance(port, AnalogSink)],
                   self.ic.ADC0_PINS + self.ic.ADC1_PINS),
      AnyPinAssign([port for port in self._all_assignable_ios if isinstance(port, AnalogSource)],
                   self.ic.DAC_PINS),
      AnyPinAssign([port for port in self._all_assignable_ios if not isinstance(port, (AnalogSink, AnalogSource))],
                   self.ic.DIO0_PINS + self.ic.DIO1_PINS),
    ).assign(
      [port for port in self._all_assignable_ios if self.get(port.is_connected())],
      self._get_suggested_pin_maps())

    for pin_num, self_port in assigned_pins.items():
      if isinstance(self_port, (DigitalSource, DigitalSink, DigitalBidir)):
        self.connect(self_port, self.ic.io_pins[str(pin_num)].as_digital_bidir())
      elif isinstance(self_port, AnalogSink):
        self.connect(self_port, self.ic.io_pins[str(pin_num)].as_analog_sink())
      elif isinstance(self_port, AnalogSource):
        self.connect(self_port, self.ic.io_pins[str(pin_num)].as_analog_source())
      else:
        raise ValueError(f"unknown pin type {self_port}")
