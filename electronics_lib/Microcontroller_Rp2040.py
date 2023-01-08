from itertools import chain
from typing import *

from electronics_abstract_parts import *
from electronics_lib import OscillatorCrystal
from .JlcPart import JlcPart


class Rp2040_Device(PinMappable, IoController, DiscreteChip, GeneratorBlock, JlcPart, FootprintBlock):
  def __init__(self, **kwargs) -> None:
    super().__init__(**kwargs)

    # note: IOVDD is self.pwr
    self.dvdd = self.Port(VoltageSink(  # Digital Core
      voltage_limits=(0.99, 1.21)*Volt,  # Table 627
      current_draw=(0.18, 40)*mAmp,  # Table 628 typ Dormant to Figure 171 approx max DVdd
    ))
    self.vreg_vout = self.Port(VoltageSource(  # actually adjustable, section 2.10.3
      voltage_out=1.1*Volt(tol=0.03),  # default is 1.1v nominal with 3% variation (Table 192)
      current_limits=(0, 100)*mAmp  # Table 1, max current
    ))
    self.vreg_vin = self.Port(VoltageSink(
      voltage_limits=(1.62, 3.63)*Volt,  # Table 627
      current_draw=self.vreg_vout.is_connected().then_else(self.vreg_vout.link().current_drawn, 0*Amp(tol=0)),
    ))
    self.usb_vdd = self.Port(VoltageSink(
      voltage_limits=(3.135, 3.63)*Volt,  # Table 627, can be lower if USB not used (section 2.9.4)
      current_draw=(0.2, 2.0)*mAmp,  # Table 628 typ BOOTSEL Idle to max BOOTSEL Active
    ))
    self.adc_avdd = self.Port(VoltageSink(
      voltage_limits=(1.62, 3.63)*Volt,  # Table 627, performance compromised <2.97V
      # current draw not specified in datasheet
    ))

    # Additional ports (on top of IoController)
    self.qspi = self.Port(SpiMaster.empty())  # TODO actually QSPI
    self.qspi_cs = self.Port(DigitalBidir.empty())

    self.xosc = self.Port(CrystalDriver(frequency_limits=(1, 15)*MHertz,  # datasheet 2.15.2.2
                                        voltage_out=self.pwr.link().voltage),
                          optional=True)

    self.swd = self.Port(SwdTargetPort().empty())

    self.generator(self.generate, self.pin_assigns,
                   self.gpio.requested(), self.adc.requested(), self.dac.requested(),
                   self.spi.requested(), self.i2c.requested(), self.uart.requested(),
                   self.usb.requested(), self.can.requested(), self.swd.is_connected())

  def contents(self) -> None:
    super().contents()

    self.pwr.init_from(VoltageSink(
      voltage_limits=(1.62, 3.63)*Volt,  # Table 627
      current_draw=(1.2, 4.3)*mAmp  # Table 628, TODO propagate current consumption from IO ports
    ))
    self.gnd.init_from(Ground())

    # Port models
    dio_ft_model = DigitalBidir.from_supply(  # Table 623
      self.gnd, self.pwr,
      voltage_limit_tolerance=(-0.3, 0.3) * Volt,
      current_limits=(-12, 12)*mAmp,  # by IOH / IOL modes
      input_threshold_abs=(0.8, 2.0)*Volt,  # for IOVdd=3.3, TODO other IOVdd ranges
      pullup_capable=True, pulldown_capable=True
    )
    dio_std_model = dio_ft_model  # exactly the same characteristics
    dio_usb_model = dio_ft_model  # similar enough, main difference seems to be PUR/PDR resistance

    self.qspi.init_from(SpiMaster(dio_std_model))
    self.qspi_cs.init_from(dio_std_model)

    adc_model = AnalogSink(  # Table 625
      voltage_limits=(self.gnd.link().voltage.lower(), self.pwr.link().voltage.upper()),
      impedance=(100, float('inf')) * kOhm
    )

    uart_model = UartPort(DigitalBidir.empty())
    spi_model = SpiMaster(DigitalBidir.empty())
    i2c_model = I2cMaster(DigitalBidir.empty())

    # Pin/peripheral resource definitions (table 3)
    self.system_pins: Dict[str, CircuitPort] = {
      # '51': QSPI_SD3
      '52': self.qspi.sck,
      '53': self.qspi.mosi,  # IO0
      # '54': QSPI_SD2
      '55': self.qspi.miso,  # IO1
      '56': self.qspi_cs,  # IO1

      '20': self.xosc.xtal_in,
      '21': self.xosc.xtal_out,

      '24': self.swd.swclk,
      '25': self.swd.swdio,

      '19': self.gnd,  # TESTEN, connect to gnd

      '1': self.pwr,  # IOVdd
      '10': self.pwr,
      '22': self.pwr,
      '33': self.pwr,
      '42': self.pwr,
      '49': self.pwr,

      '23': self.dvdd,
      '50': self.dvdd,

      '44': self.vreg_vin,
      '45': self.vreg_vout,
      '48': self.usb_vdd,
      '43': self.adc_avdd,
      '57': self.gnd,  # pad
    }

    self.pinmaps = PinMapUtil([  # Table 5, partial table for 48-pin only
      PinResource('2', {'GPIO0': dio_ft_model}),
      PinResource('3', {'GPIO1': dio_ft_model}),
      PinResource('4', {'GPIO2': dio_ft_model}),
      PinResource('5', {'GPIO3': dio_ft_model}),
      PinResource('6', {'GPIO4': dio_ft_model}),
      PinResource('7', {'GPIO5': dio_ft_model}),
      PinResource('8', {'GPIO6': dio_ft_model}),
      PinResource('9', {'GPIO7': dio_ft_model}),
      PinResource('11', {'GPIO8': dio_ft_model}),
      PinResource('12', {'GPIO9': dio_ft_model}),
      PinResource('13', {'GPIO10': dio_ft_model}),
      PinResource('14', {'GPIO11': dio_ft_model}),
      PinResource('15', {'GPIO12': dio_ft_model}),
      PinResource('16', {'GPIO13': dio_ft_model}),
      PinResource('17', {'GPIO14': dio_ft_model}),
      PinResource('18', {'GPIO15': dio_ft_model}),
      PinResource('27', {'GPIO16': dio_ft_model}),
      PinResource('28', {'GPIO17': dio_ft_model}),
      PinResource('29', {'GPIO18': dio_ft_model}),
      PinResource('30', {'GPIO19': dio_ft_model}),
      PinResource('31', {'GPIO20': dio_ft_model}),
      PinResource('32', {'GPIO21': dio_ft_model}),

      PinResource('34', {'GPIO22': dio_ft_model}),
      PinResource('35', {'GPIO23': dio_ft_model}),
      PinResource('36', {'GPIO24': dio_ft_model}),
      PinResource('37', {'GPIO25': dio_ft_model}),

      PinResource('38', {'GPIO26': dio_std_model, 'ADC0': adc_model}),
      PinResource('39', {'GPIO27': dio_std_model, 'ADC1': adc_model}),
      PinResource('40', {'GPIO28': dio_std_model, 'ADC2': adc_model}),
      PinResource('41', {'GPIO29': dio_std_model, 'ADC3': adc_model}),

      # fixed-pin peripherals
      PeripheralFixedPin('USB', UsbDevicePort(dio_usb_model), {
        'dm': '46', 'dp': '47'
      }),

      # reassignable peripherals
      PeripheralFixedResource('UART0', uart_model, {
        'tx': ['GPIO0', 'GPIO12', 'GPIO16', 'GPIO28'],
        'rx': ['GPIO1', 'GPIO13', 'GPIO17', 'GPIO29']
      }),
      PeripheralFixedResource('UART1', uart_model, {
        'tx': ['GPIO4', 'GPIO8', 'GPIO20', 'GPIO24'],
        'rx': ['GPIO5', 'GPIO9', 'GPIO21', 'GPIO25']
      }),

      PeripheralFixedResource('SPI0', spi_model, {  # assumes master mode
        'miso': ['GPIO0', 'GPIO4', 'GPIO16', 'GPIO20'],  # RX
        'sck': ['GPIO2', 'GPIO6', 'GPIO18', 'GPIO22'],
        'mosi': ['GPIO3', 'GPIO7', 'GPIO19', 'GPIO23']  # TX
      }),
      PeripheralFixedResource('SPI1', spi_model, {  # assumes master mode
        'miso': ['GPIO8', 'GPIO12', 'GPIO24', 'GPIO28'],  # RX
        'sck': ['GPIO10', 'GPIO14', 'GPIO26'],
        'mosi': ['GPIO11', 'GPIO15', 'GPIO27']  # TX
      }),
      PeripheralFixedResource('I2C0', i2c_model, {
        'sda': ['GPIO0', 'GPIO4', 'GPIO8', 'GPIO12', 'GPIO16', 'GPIO20', 'GPIO24', 'GPIO28'],
        'scl': ['GPIO1', 'GPIO5', 'GPIO9', 'GPIO13', 'GPIO17', 'GPIO21', 'GPIO25', 'GPIO20']
      }),
      PeripheralFixedResource('I2C1', i2c_model, {
        'sda': ['GPIO2', 'GPIO6', 'GPIO10', 'GPIO14', 'GPIO18', 'GPIO22', 'GPIO24', 'GPIO26'],
        'scl': ['GPIO3', 'GPIO7', 'GPIO11', 'GPIO15', 'GPIO19', 'GPIO23', 'GPIO25', 'GPIO27']
      }),

      PeripheralFixedPin('SWD', SwdTargetPort(dio_std_model), {
        'swdio': '25', 'swclk': '24', 'reset': '26',  # reset is 'run'
      }),
    ])

  def generate(self, assignments: List[str],
               gpio_requests: List[str], adc_requests: List[str], dac_requests: List[str],
               spi_requests: List[str], i2c_requests: List[str], uart_requests: List[str],
               usb_requests: List[str], can_requests: List[str], swd_connected: bool) -> None:
    allocated = self.pinmaps.allocate([
      (SwdTargetPort, ['swd'] if swd_connected else []),
      (UsbDevicePort, usb_requests), (SpiMaster, spi_requests), (I2cMaster, i2c_requests),
      (UartPort, uart_requests), (CanControllerPort, can_requests),
      (AnalogSink, adc_requests), (AnalogSource, dac_requests), (DigitalBidir, gpio_requests),
    ], assignments)
    self.generator_set_allocation(allocated)

    io_pins = self._instantiate_from(self._get_io_ports() + [self.swd], allocated)

    self.footprint(
      'U', 'Package_DFN_QFN:QFN-56-1EP_7x7mm_P0.4mm_EP3.2x3.2mm',
      dict(chain(self.system_pins.items(), io_pins.items())),
      mfr='Raspberry Pi', part='RP2040',
      datasheet='https://datasheets.raspberrypi.com/rp2040/rp2040-datasheet.pdf'
    )
    self.assign(self.lcsc_part, 'C2040')
    self.assign(self.actual_basic_part, False)


class Rp2040Usb(Block):
  """Supporting passives for USB for RP2040"""
  def __init__(self) -> None:
    super().__init__()
    self.usb_rp = self.Port(UsbHostPort.empty(), [Input])
    self.usb = self.Port(UsbDevicePort.empty(), [Output])

  def contents(self) -> None:
    super().contents()

    self.dp_res = self.Block(Resistor(27*Ohm(tol=0.05)))
    self.dm_res = self.Block(Resistor(27*Ohm(tol=0.05)))

    self.connect(self.usb_rp.dm, self.dm_res.a.adapt_to(DigitalBidir()))  # internal ports are ideal
    self.connect(self.usb.dm, self.dm_res.b.adapt_to(
      UsbBitBang.digital_external_from_link(self.usb_rp.dm)))

    self.connect(self.usb_rp.dp, self.dp_res.a.adapt_to(DigitalBidir()))
    self.connect(self.usb.dp, self.dp_res.b.adapt_to(
      UsbBitBang.digital_external_from_link(self.usb_rp.dp)))


class Rp2040(PinMappable, Microcontroller, IoControllerWithSwdTargetConnector, IoController, GeneratorBlock):
  def __init__(self, **kwargs):
    super().__init__(**kwargs)
    self.generator(self.generate, self.usb.requested(),
                   self.pin_assigns, self.gpio.requested(), self.swd_swo_pin, self.swd_tdi_pin)

  def contents(self):
    super().contents()

    with self.implicit_connect(
        ImplicitConnect(self.pwr, [Power]),
        ImplicitConnect(self.gnd, [Common])
    ) as imp:
      # https://datasheets.raspberrypi.com/rp2040/hardware-design-with-rp2040.pdf
      self.ic = imp.Block(Rp2040_Device(pin_assigns=ArrayStringExpr()))
      # USB requires additional circuitry, and SWO/TDI must be mixed into GPIOs
      self._export_ios_from(self.ic, excludes=[self.usb, self.gpio])
      self.assign(self.actual_pin_assigns, self.ic.actual_pin_assigns)

      self.connect(self.swd.swd, self.ic.swd)

      self.iovdd_cap = ElementDict[DecouplingCapacitor]()
      for i in range(6):  # one per IOVdd, combining USBVdd and IOVdd pin 49 per the example
        self.iovdd_cap[i] = imp.Block(DecouplingCapacitor(0.1 * uFarad(tol=0.2)))
      self.avdd_cap = imp.Block(DecouplingCapacitor(0.1 * uFarad(tol=0.2)))

      self.vreg_in_cap = imp.Block(DecouplingCapacitor(1 * uFarad(tol=0.2)))

      self.mem = imp.Block(SpiMemory(Range.all()))
      self.connect(self.ic.qspi, self.mem.spi)
      self.connect(self.ic.qspi_cs, self.mem.cs)


    self.connect(self.pwr, self.ic.vreg_vin, self.ic.adc_avdd, self.ic.usb_vdd)
    self.connect(self.ic.vreg_vout, self.ic.dvdd)

    self.dvdd_cap = ElementDict[DecouplingCapacitor]()
    for i in range(2):
      self.dvdd_cap[i] = self.Block(DecouplingCapacitor(0.1 * uFarad(tol=0.2))).connected(self.gnd, self.ic.dvdd)

    self.vreg_out_cap = self.Block(DecouplingCapacitor(1 * uFarad(tol=0.2))).connected(self.gnd, self.ic.dvdd)

  def generate(self, usb_requests: List[str],
               pin_assigns: List[str], gpio_requested: List[str], swd_swo_pin: str, swd_tdi_pin: str) -> None:
    if usb_requests:  # tighter frequency tolerances from USB usage require a crystal
      self.crystal = self.Block(OscillatorCrystal(frequency=12 * MHertz(tol=0.005)))  # 12MHz required for USB
      self.connect(self.crystal.gnd, self.gnd)
      self.connect(self.crystal.crystal, self.ic.xosc)

    if usb_requests:
      assert len(usb_requests) == 1
      usb_request_name = usb_requests[0]
      (self.usb_res, ), self.usb_chain = self.chain(
        self.ic.usb.request(usb_request_name),
        self.Block(Rp2040Usb()),
        self.usb.append_elt(UsbDevicePort.empty(), usb_request_name))
    self.usb.defined()

    if swd_swo_pin != 'NC':
      self.connect(self.ic.gpio.request('swd_swo'), self.swd.swo)
      pin_assigns.append(f'swd_swo={swd_swo_pin}')
    if swd_tdi_pin != 'NC':
      self.connect(self.ic.gpio.request('swd_tdi'), self.swd.tdi)
      pin_assigns.append(f'swd_tdi={swd_tdi_pin}')
    self.assign(self.ic.pin_assigns, pin_assigns)

    gpio_model = DigitalBidir.empty()
    for gpio_name in gpio_requested:
      self.connect(self.gpio.append_elt(gpio_model, gpio_name), self.ic.gpio.request(gpio_name))
    self.gpio.defined()
