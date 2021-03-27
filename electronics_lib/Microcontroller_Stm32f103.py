from typing import *
from itertools import chain

from electronics_abstract_parts import *


class Stm32f103_48_Device(DiscreteChip, CircuitBlock):
  """
  STM32F103C8 (QFP-48) microcontroller, Cortex-M3
  https://www.st.com/resource/en/datasheet/stm32f103c8.pdf
  """
  def __init__(self) -> None:
    super().__init__()

    # TODO separate VddA and VssA, but both must operate at same potential
    self.vdd = self.Port(VoltageSink(
      voltage_limits=(3.0, 3.6)*Volt,
      current_draw=(0, 50.3)*mAmp  # Table 13
    ), [Power])  # TODO relaxed range down to 2.0 if ADC not used, or 2.4 if USB not used
    self.vss = self.Port(Ground(), [Common])

    self.nrst = self.Port(DigitalSink.from_supply(
      self.vss, self.vdd,
      voltage_limit_tolerance=(-0.3, 0.3)*Volt,  # Table 5.3.1, general operating conditions  TODO: FT IO, BOOT0 IO
      current_draw=(0, 0)*Amp,
      input_threshold_abs=(0.8, 2)*Volt
    ), optional=True)  # note, internal pull-up resistor, 30-50 kOhm by Table 35

    # self.boot0 = self.Port(DigitalSink(
    #   voltage_limits=(0, 5.5)*Volt, current_draw=(0, 0)*mAmp,
    #   input_thresholds=(0, 5.5)*Volt  # TODO not actually specified in datasheet!
    # ))

    standard_dio_model = DigitalBidir.from_supply(
      self.vss, self.vdd,
      voltage_limit_tolerance=(-0.3, 0.3)*Volt,  # Table 5.3.1, general operating conditions  TODO: FT IO
      current_draw=(0, 0)*Amp, current_limits=(-20, 20)*mAmp,  # TODO relaxed VOL, VOH, o/w +- 8 mAmps, except PC13-15 at +/- 3 mAmp
      input_threshold_factor=(0.45, 0.65),  # TODO stricter (but more complex) bounds available
      output_threshold_factor=(0, 1),
      pullup_capable=True, pulldown_capable=True)

    self.swd = self.Port(SwdTargetPort(standard_dio_model))  # TODO maybe make optional?

    self.osc32 = self.Port(CrystalDriver(frequency_limits=32.768*kHertz, voltage_out=self.vdd.link().voltage), optional=True)  # TODO other specs from Table 23
    self.osc = self.Port(CrystalDriver(frequency_limits=(4, 16)*MHertz, voltage_out=self.vdd.link().voltage), optional=True)  # Table 22

    self.pa = ElementDict[DigitalBidir]()
    for i in chain(range(13), [15]):
      self.pa[i] = self.Port(standard_dio_model, optional=True)

    self.pb = ElementDict[DigitalBidir]()
    for i in chain(range(3), range(4, 10), range(10, 16)):
      self.pb[i] = self.Port(standard_dio_model, optional=True)

    self.pc = ElementDict[DigitalBidir]()
    for i in chain(range(13, 14)):
      self.pc[i] = self.Port(standard_dio_model, optional=True)

    self.system_pins: Dict[str, CircuitPort] = {
      '1': self.vdd,  # actually Vbat
      '3': self.osc32.xtal_in,  # also PC14
      '4': self.osc32.xtal_out,  # also PC15
      '5': self.osc.xtal_in,  # also PD0
      '6': self.osc.xtal_out,  # also PD1
      '7': self.swd.reset,  # TODO actually NRST
      '8': self.vss,  # actually VssA
      '9': self.vdd,  # actually VddA

      '23': self.vss,
      '24': self.vdd,

      '34': self.swd.swdio,  # self.pa[13],
      '35': self.vss,
      '36': self.vdd,

      '37': self.swd.swclk,  # self.pa[14],
      '39': self.swd.swo,  # self.pb[3],  # also, JTDO
      '44': self.vss,  # self.boot0,  TODO re-enable boot0 option
      '47': self.vss,
      '48': self.vdd,
    }
    self.io_pins = {
      '2': self.pc[13],
      '10': self.pa[0],  # also, ADC12_IN0
      '11': self.pa[1],  # also, ADC12_IN1
      '12': self.pa[2],  # also, ADC12_IN2

      '13': self.pa[3],  # also, ADC12_IN3
      '14': self.pa[4],  # also, ADC12_IN4
      '15': self.pa[5],  # also, ADC12_IN5
      '16': self.pa[6],  # also, ADC12_IN6
      '17': self.pa[7],  # also, ADC12_IN7
      '18': self.pb[0],  # also, ADC12_IN8
      '19': self.pb[1],  # also, ADC12_IN9
      '20': self.pb[2],  # also, BOOT1
      '21': self.pb[10],
      '22': self.pb[11],

      '25': self.pb[12],
      '26': self.pb[13],
      '27': self.pb[14],
      '28': self.pb[15],
      '29': self.pa[8],
      '30': self.pa[9],
      '31': self.pa[10],
      '32': self.pa[11],
      '33': self.pa[12],

      '38': self.pa[15],  # also, JTDI
      '40': self.pb[4],  # also, JNTRST
      '41': self.pb[5],
      '42': self.pb[6],
      '43': self.pb[7],
      '45': self.pb[8],
      '46': self.pb[9],
    }

  def contents(self):
    super().contents()
    self.footprint(
      'U', 'Package_QFP:LQFP-48_7x7mm_P0.5mm',
      dict(chain(self.system_pins.items(), self.io_pins.items())),
      mfr='STMicroelectronics', part='STM32F103xxT6',
      datasheet='https://www.st.com/resource/en/datasheet/stm32f103c8.pdf'
    )


class Stm32f103_48(Microcontroller, AssignablePinBlock, GeneratorBlock):
  """
  STM32F103C8 (QFP-48) microcontroller, Cortex-M3
  https://www.st.com/resource/en/datasheet/stm32f103c8.pdf
  """
  def __init__(self) -> None:
    super().__init__()
    self.ic = self.Block(Stm32f103_48_Device())

    self.pwr = self.Port(VoltageSink(), [Power])
    self.gnd = self.Port(Ground(), [Common])
    self.swd = self.Export(self.ic.swd)
    # self.rst = self.Export(self.ic.nrst)  # TODO separate from SWD

    self.xtal = self.Export(self.ic.osc, optional=True)  # TODO standardize naming across all MCUs
    self.xtal_rtc = self.Export(self.ic.osc32, optional=True)  # TODO standardize naming across all MCUs

    self.digital = ElementDict[DigitalBidir]()
    for i in range(len(self.ic.io_pins)):
      self.digital[i] = self.Port(DigitalBidir(), optional=True)
      self._add_assignable_io(self.digital[i])

    self.adc = ElementDict[AnalogSink]()
    for i in range(10):
      self.adc[i] = self.Port(AnalogSink(), optional=True)
      self._add_assignable_io(self.adc[i])

    self.uart_0 = self.Port(UartPort(), optional=True)
    self._add_assignable_io(self.uart_0)

    self.spi_0 = self.Port(SpiMaster(), optional=True)
    self._add_assignable_io(self.spi_0)

    self.can_0 = self.Port(CanControllerPort(), optional=True)
    self._add_assignable_io(self.can_0)

    self.usb_0 = self.Port(UsbDevicePort(), optional=True)
    # self._add_assignable_io(self.usb_0)  # TODO incompatible with builtin USB circuit

    self.generator(self.pin_assign, self.pin_assigns,
                   req_ports=chain(self.digital.values(),
                                   self.adc.values(),
                                   [self.uart_0, self.spi_0, self.can_0, self.usb_0]),
                   targets=chain([self.pwr, self.gnd],
                                 [self.ic],  # connected block
                                 self.digital.values(),
                                 self.adc.values(),
                                 [self.uart_0, self.spi_0, self.can_0, self.usb_0]))  # TODO pass in connected blocks



  def pin_assign(self, pin_assigns_str: str) -> None:
    # These are here because we can't split the power with the USB.
    # TODO support for split nets between generatorrs
    self.connect(self.pwr, self.ic.vdd)
    self.connect(self.gnd, self.ic.vss)

    io_draw_expr = (0, 0)*mAmp
    for _, io in self.digital.items():
      io_draw_expr = io_draw_expr + io.is_connected().then_else(
        io.link().current_drawn.intersect((0, float('inf'))*Amp),  # only count sourced current
        (0, 0)*Amp)
    self.io_draw = self.Block(VoltageLoad(
      voltage_limit=(-float('inf'), float('inf')),
      current_draw=io_draw_expr
    ))
    self.connect(self.pwr, self.io_draw.pwr)

    #
    # Reference Circuit Block
    #
    # TODO associate capacitors with a particular Vdd, Vss pin
    self.pwr_cap = ElementDict[DecouplingCapacitor]()
    with self.implicit_connect(
        ImplicitConnect(self.pwr, [Power]),
        ImplicitConnect(self.gnd, [Common])
    ) as imp:
      # one 0.1uF cap each for Vdd1-5 and one bulk 4.7uF cap
      self.pwr_cap[0] = imp.Block(DecouplingCapacitor(4.7 * uFarad(tol=0.2)))
      for i in range(1, 4):
        self.pwr_cap[i] = imp.Block(DecouplingCapacitor(0.1 * uFarad(tol=0.2)))

      # one 10nF and 1uF cap for VddA
      # TODO generate the same cap if a different Vref is used
      self.vdda_cap_0 = imp.Block(DecouplingCapacitor(10 * nFarad(tol=0.2)))
      self.vdda_cap_1 = imp.Block(DecouplingCapacitor(1 * uFarad(tol=0.2)))

    #
    # Pin assignment block
    #
    assigned_pins = PinAssignmentUtil(
      # TODO assign fixed-pin digital peripherals here
      # TODO
      AnyPinAssign([port for port in self._all_assignable_ios if isinstance(port, AnalogSink)],
                   [10, 11, 12, 13, 14, 15, 16, 17, 18, 19]),
      AnyPinAssign([port for port in self._all_assignable_ios if isinstance(port, DigitalBidir)],
                   [int(pinnum) for pinnum in self.ic.io_pins.keys()]),  # TODO ducktype in pin-assign infrastructure
      PeripheralPinAssign([port for port in self._all_assignable_ios if isinstance(port, SpiMaster)],
                          [[39, 15], [17, 41], [16, 40]],  # SPI1 - sck, mosi, miso
                          [26, 28, 27]),  # SPI2
      PeripheralPinAssign([port for port in self._all_assignable_ios if isinstance(port, UartPort)],
                          [[30, 42], [31, 43]],  # USART1 - tx, rx
                          [12, 13],  # USART2
                          [21, 22]),  # USART3
      PeripheralPinAssign([port for port in self._all_assignable_ios if isinstance(port, CanControllerPort)],
                          [[33, 46], [32, 45]]),  # CAN - txd, rxd
      PeripheralPinAssign([port for port in self._all_assignable_ios if isinstance(port, UsbDevicePort)],
                          [33, 32]),  # USB - dp, dm
    ).assign(
      [port for port in self._all_assignable_ios if self.get(port.is_connected())],
      self._get_suggested_pin_maps(pin_assigns_str))

    for pin_num, self_port in assigned_pins.items():
      self.connect(self_port, self.ic.io_pins[str(pin_num)])

    if self.get(self.usb_0.is_connected()):
      self.usb_pull = self.Block(PullupResistor(resistance=1.5*kOhm(tol=0.01)))  # required by datasheet Table 44  # TODO proper tolerancing?
      self.connect(self.usb_pull.pwr, self.pwr)

      self.connect(self.usb_0.dm, self.ic.pa[11])
      self.connect(self.usb_0.dp, self.usb_pull.io, self.ic.pa[12])
