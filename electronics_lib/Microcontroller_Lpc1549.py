from typing import *
from itertools import chain

from electronics_abstract_parts import *


@abstract_block
class Lpc1549Base_Device(DiscreteChip, FootprintBlock):
  IRC_FREQUENCY = 12*MHertz(tol=0.01)

  # TODO remove these once there is a unified pin capability specification
  DIO0_PINS: List[int]
  DIO1_PINS: List[int]
  ADC0_PINS: List[int]
  ADC1_PINS: List[int]
  DAC_PINS: List[int]

  @init_in_parent
  def __init__(self) -> None:
    super().__init__()

    #
    # Common Ports
    #
    self.vdd = self.Port(VoltageSink(
      voltage_limits=(2.4, 3.6) * Volt,
      current_draw=(0, 19)*mAmp,  # rough guesstimate from Figure 11.1 for supply Idd (active mode)
    ), [Power])
    self.vss = self.Port(Ground(), [Common])

    #
    # Port Models
    #
    # TODO use all these models once there is a strategy for Analog/Digital capable IOs
    self.dio_5v_model = (DigitalBidir(
      voltage_limits=(0, 5) * Volt,
      current_draw=(0, 0) * Amp,
      voltage_out=(0 * Volt, self.vdd.link().voltage.upper()),
      current_limits=(-50, 45) * mAmp,  # TODO this uses short circuit current, which might not be useful, better to model as resistance?
      input_thresholds=(0.3 * self.vdd.link().voltage.lower(),
                        0.7 * self.vdd.link().voltage.upper()),
      output_thresholds=(0 * Volt, self.vdd.link().voltage.lower()),
      pullup_capable=True, pulldown_capable=True
    ), )  # TODO hax tuple wrapper to prevent unbound error
    dio_5v_model = self.dio_5v_model[0]

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
    self.swd_swdio = self.Port(DigitalBidir(dio_5v_model))
    self.swd_swclk = self.Port(DigitalSink(dio_5v_model))
    self.swd_swo = self.Port(DigitalSource(dio_5v_model))
    self.swd_reset = self.Port(DigitalSink(dio_5v_model))

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


class Lpc1549_48_Device(Lpc1549Base_Device):
  DIO0_PINS = [
    1, 2, 3, 4, 6, 7, 8, 12,  # pin 5 ISP_0 not assigned, 9 reserved for SWD
    13, 15, 18, 21, 22, 23,  # pin 24 ISP_1 not assigned, TODO not assigning 19 - not 5v tolerant
    28,  # pin 29, 33, 34 reserved for SWD
    43, 44, 45, 46, 47, 48  # not assigning 37, 38 - not 5v tolerant and IIC reserved
  ]
  DIO1_PINS: List[int] = []
  ADC0_PINS = [
    1, 2, 3, 4, 6, 7, 8  # pin 5 ISP_0 not assigned, 9 reserved for SWD
  ]
  ADC1_PINS = [
    12, 15, 18, 21, 22, 23, # pin 24 ISP_1 not assigned
  ]
  DAC_PINS = [
    19
  ]

  @init_in_parent
  def __init__(self):
    super().__init__()

    for i in chain(range(4), range(5, 8), range(9, 16), [17, 18], range(24, 30)):
      self.pio0[i] = self.Port(Passive(), optional=True)

    self.system_pins: Dict[str, CircuitPort] = {
      '16': self.vdd,  # VddA
      '17': self.vss,  # VssA
      '10': self.vdd,  # VrefP_ADC
      '14': self.vdd,  # VrefP_DAC
      '11': self.vss,  # VrefN
      '30': self.vdd,  # TODO support optional Vbat
      '20': self.vss,
      '27': self.vdd,
      '39': self.vdd,
      '40': self.vss,
      '41': self.vss,
      '42': self.vdd,

      '26': self.xtal.xtal_in,  # TODO Table 3, note 11, float/gnd (gnd preferred) if not used
      '25': self.xtal.xtal_out,  # TODO Table 3, note 11, float if not used
      '31': self.xtal_rtc.xtal_in,  # 14.5 can be grounded if RTC not used
      '32': self.xtal_rtc.xtal_out,

      '34': self.swd_reset,
      '33': self.swd_swdio,  # also TMS
      '29': self.swd_swclk,  # also TCK
      '9': self.swd_swo,  # also TDO
      # 12: JTAG TDI

      '35': self.usb_0.dp,
      '36': self.usb_0.dm,

      '37': self.i2c_0.scl,  # I2C_SCL, not 5v tolerant
      '38': self.i2c_0.sda,  # I2C_SDA, not 5v tolerant
    }

    self.io_pins = {
      '1': self.pio0[0],
      '2': self.pio0[1],
      '3': self.pio0[2],
      '4': self.pio0[3],
      # '5': self.pio0[4],  # not connected, reserved for ISP_0, note datasheet indicates reset state is pull-up
      '6': self.pio0[5],
      '7': self.pio0[6],
      '8': self.pio0[7],
      # '9': self.pio0[8],  # reserved for SWD
      '12': self.pio0[9],

      '13': self.pio0[18],
      '15': self.pio0[10],
      '18': self.pio0[11],
      '19': self.pio0[12],  # DAC_OUT, not 5v tolerant
      '21': self.pio0[13],
      '22': self.pio0[14],
      '23': self.pio0[15],
      # '24': self.pio0[16],  # not connected, reserved for ISP_1, note datasheet indicates reset state is pull-up

      '28': self.pio0[17],
      # '29': self.pio0[19],  # reserved for SWCLK
      # '33': self.pio0[20],  # reserved for SWDIO
      # '34': self.pio0[21],  # reserved for /RESET

      '43': self.pio0[24],
      '44': self.pio0[25],
      '45': self.pio0[26],
      '46': self.pio0[27],
      '47': self.pio0[28],
      '48': self.pio0[29],
    }

  def contents(self) -> None:
    super().contents()
    self.footprint(
      'U', 'Package_QFP:LQFP-48_7x7mm_P0.5mm',
      dict(chain(self.system_pins.items(), self.io_pins.items())),
      mfr='NXP', part='LPC1549JBD48',
      datasheet='https://www.nxp.com/docs/en/data-sheet/LPC15XX.pdf'
    )


class Lpc1549_64_Device(Lpc1549Base_Device):
  DIO0_PINS = [  # pin 38 ISP_1, 54 ISP_0 not assigned, pin 12 reserved for SWD,
    1, 2, 3, 5, 6, 7, 8, 9, 10, 11, 16,
    17, 19, 23, 29, 30, 31, 32,  # TODO pin 24 DAC not 5v tolerant
    39,
    58, 60, 61, 62, 63, 64
  ]
  DIO1_PINS = [
    4, 15,
    25, 28,
    33, 34, 38, 46,
    51, 53, 54, 59,
  ]
  ADC0_PINS = [
    1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11,
  ]
  ADC1_PINS = [
    15, 16, 19, 23, 25, 28, 29, 30, 31, 32, 33, 34
  ]
  DAC_PINS = [
    24
  ]

  @init_in_parent
  def __init__(self):
    super().__init__()

    for i in chain(range(8), range(9, 19), range(24, 32)):
      self.pio0[i] = self.Port(Passive(), optional=True)

    for i in chain(range(12)):
      self.pio1[i] = self.Port(Passive(), optional=True)

    self.system_pins: Dict[str, CircuitPort] = {
      '20': self.vdd,  # VddA
      '21': self.vss,  # VssA
      '13': self.vdd,  # VrefP_ADC
      '18': self.vdd,  # VrefP_DAC
      '14': self.vss,  # VrefN
      '41': self.vdd,  # TODO support optional Vbat
      '22': self.vdd,
      '26': self.vss,
      '27': self.vss,
      '37': self.vdd,
      '52': self.vdd,
      '55': self.vss,
      '56': self.vss,
      '57': self.vdd,

      '36': self.xtal.xtal_in,  # TODO Table 3, note 11, float/gnd (gnd preferred) if not used
      '35': self.xtal.xtal_out,  # TODO Table 3, note 11, float if not used
      '42': self.xtal_rtc.xtal_in,  # 14.5 can be grounded if RTC not used
      '43': self.xtal_rtc.xtal_out,

      '45': self.swd_reset,
      '44': self.swd_swdio,  # also TMS
      '40': self.swd_swclk,  # also TCK
      '12': self.swd_swo,  # also TDO

      '47': self.usb_0.dp,
      '48': self.usb_0.dm,

      '49': self.i2c_0.scl,  # TODO: should these be handled by PinAssignUtil?
      '50': self.i2c_0.sda,
      # '16': JTAG TDI
    }

    self.io_pins = {
      '1': self.pio0[30],
      '2': self.pio0[0],
      '3': self.pio0[31],
      '4': self.pio1[0],
      '5': self.pio0[1],
      '6': self.pio0[2],
      '7': self.pio0[3],
      '8': self.pio0[4],
      '9': self.pio0[5],
      '10': self.pio0[6],
      '11': self.pio0[7],
      # '12': self.pio0[8],  # reserved for SWDIO
      '15': self.pio1[1],
      '16': self.pio0[9],

      '17': self.pio0[18],
      '19': self.pio0[10],
      '23': self.pio0[11],
      '24': self.pio0[12],  # DAC, not 5v tolerant
      '25': self.pio1[2],
      '28': self.pio1[3],
      '29': self.pio0[13],
      '30': self.pio0[14],
      '31': self.pio0[15],
      '32': self.pio0[16],

      '33': self.pio1[4],
      '34': self.pio1[5],
      '38': self.pio1[11],
      '39': self.pio0[17],
      # '40': self.pio0[19],  # reserved for SWCLK
      # '44': self.pio0[20],  # reserved for SWDIO
      # '45': self.pio0[21],  # reserved for /RESET
      '46': self.pio1[6],

      # '49': self.pio0[22],  # I2C_SCL, not 5v tolerant
      # '50': self.pio0[23],  # I2C_SDA, not 5v tolerant
      '51': self.pio1[7],
      '53': self.pio1[8],
      '54': self.pio1[9],
      '58': self.pio0[24],
      '59': self.pio1[10],
      '60': self.pio0[25],
      '61': self.pio0[26],
      '62': self.pio0[27],
      '63': self.pio0[28],
      '64': self.pio0[29],
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
class Lpc1549Base(Microcontroller, AssignablePinBlock):  # TODO refactor with _Device
  """
  LPC1549JBD48 (QFP-48) microcontroller, Cortex-M3
  https://www.nxp.com/docs/en/data-sheet/LPC15XX.pdf
  """
  DEVICE: Type[Lpc1549Base_Device] = Lpc1549Base_Device

  @init_in_parent
  def __init__(self, frequency: RangeExpr = Lpc1549Base_Device.IRC_FREQUENCY) -> None:
    super().__init__()
    self.ic = self.Block(self.DEVICE())

    self.pwr = self.Export(self.ic.vdd, [Power])
    self.gnd = self.Export(self.ic.vss, [Common])
    self.swd = self.Port(SwdTargetPort())  # TODO

    self.xtal = self.Export(self.ic.xtal, optional=True)
    self.xtal_rtc = self.Export(self.ic.xtal_rtc, optional=True)

    self.frequency = self.Parameter(RangeExpr(frequency))  # TODO move into _Device, but const prop needs to ignore inner contents

    # TODO these should be array types?
    # TODO model current flows from digital ports
    self.digital = ElementDict[DigitalBidir]()
    for i in range(20):
      self.digital[i] = self.Port(DigitalBidir(), optional=True)
      self._add_assignable_io(self.digital[i])

    self.adc = ElementDict[AnalogSink]()
    for i in range(10):
      self.adc[i] = self.Port(AnalogSink(), optional=True)
      self._add_assignable_io(self.adc[i])

    self.dac = ElementDict[AnalogSource]()
    for i in range(1):
      self.dac[i] = self.Port(AnalogSource(), optional=True)
      self._add_assignable_io(self.dac[i])

    self.uart = ElementDict[UartPort]()
    for i in range(3):
      self.uart[i] = self.Port(UartPort(), optional=True)
      self._add_assignable_io(self.uart[i])

    self.spi = ElementDict[SpiMaster]()
    for i in range(2):
      self.spi[i] = self.Port(SpiMaster(), optional=True)
      self._add_assignable_io(self.spi[i])

    self.can_0 = self.Port(CanControllerPort(), optional=True)
    self._add_assignable_io(self.can_0)

    self.i2c_0 = self.Port(I2cMaster(), optional=True)
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
    self.io_draw = self.Block(VoltageLoad(
      voltage_limit=(-float('inf'), float('inf')),
      current_draw=self._io_draw
    ))
    self.connect(self.pwr, self.io_draw.pwr)
    self.require(self.pwr.current_draw.within(self._io_draw + (0, 19)*mAmp))

    self.generator(self.pin_assign, self.pin_assigns,
                   req_ports=chain(self.digital.values(),
                                   self.adc.values(), self.dac.values(),
                                   self.uart.values(), self.spi.values(),
                                   [self.can_0, self.i2c_0, self.usb_0]),
                   targets=chain([self.ic],  # connected block
                                 [self.swd.swo, self.swd.swdio, self.swd.swclk, self.swd.reset],
                                 self.digital.values(),
                                 self.adc.values(), self.dac.values(),
                                 self.uart.values(), self.spi.values(),
                                 [self.can_0, self.i2c_0, self.usb_0]))  # TODO pass in connected blocks

    #
    # Reference Circuit Block
    #
    self.require(self.ic.IRC_FREQUENCY.within(self.frequency) | self.xtal.is_connected(),
                 "requested frequency out of internal RC range")  # TODO configure clock dividers?

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


  def pin_assign(self, pin_assigns_str: str) -> None:
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
      self._get_suggested_pin_maps(pin_assigns_str))

    #
    # IO models
    #
    # TODO models should be in the _Device block, but need to figure how to handle Analog/Digital capable pins first
    # TODO dedup w/ models in the _Device block
    for pin_num, self_port in assigned_pins.assigned_pins.items():
      if isinstance(self_port, (DigitalSource, DigitalSink, DigitalBidir)):
        self.connect(self_port, self.ic.io_pins[str(pin_num)].as_digital_bidir(
          voltage_limits=(0, 5) * Volt,
          current_draw=(0, 0) * Amp,
          voltage_out=(0 * Volt, self.pwr.link().voltage.upper()),
          current_limits=(-50, 45) * mAmp,  # TODO this uses short circuit current, which might not be useful, better to model as resistance?
          input_thresholds=(0.3 * self.pwr.link().voltage.lower(),
                            0.7 * self.pwr.link().voltage.upper()),
          output_thresholds=(0 * Volt, self.pwr.link().voltage.lower()),
          pullup_capable=True, pulldown_capable=True
        ))
      elif isinstance(self_port, AnalogSink):
        self.connect(self_port, self.ic.io_pins[str(pin_num)].as_analog_sink(
          voltage_limits=(0, self.pwr.link().voltage.upper()),
          current_draw=(0, 0) * Amp,
          impedance=(100, float('inf')) * kOhm
        ))
      elif isinstance(self_port, AnalogSource):
        self.connect(self_port, self.ic.io_pins[str(pin_num)].as_analog_source(
          voltage_out=(0, self.pwr.link().voltage.upper() - 0.3),
          current_limits=(0, 0) * Amp,  # TODO not given by spec
          impedance=(300, 300) * Ohm  # Table 25, "typical" rating
        ))
      else:
        raise ValueError(f"unknown pin type {self_port}")

    for self_port in assigned_pins.not_connected:
      assert isinstance(self_port, NotConnectablePort), f"non-NotConnectablePort {self_port.name()} marked NC"
      self_port.not_connected()


class Lpc1549_48(Lpc1549Base):
  DEVICE = Lpc1549_48_Device


class Lpc1549_64(Lpc1549Base):
  DEVICE = Lpc1549_64_Device
