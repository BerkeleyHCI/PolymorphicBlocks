from typing import *

from electronics_abstract_parts import *
from .JlcPart import JlcPart


@abstract_block
class Lpc1549Base_Device(IoControllerDac, IoControllerCan, IoControllerUsb, BaseIoControllerPinmapGenerator,
                         InternalSubcircuit, GeneratorBlock, JlcPart, FootprintBlock):
  PACKAGE: str  # package name for footprint(...)
  PART: str  # part name for footprint(...)
  LCSC_PART: str

  SYSTEM_PIN_REMAP: Dict[str, Union[str, List[str]]]  # pin name in base -> pin name(s)
  RESOURCE_PIN_REMAP: Dict[str, str]  # resource name in base -> pin name

  def __init__(self, **kwargs) -> None:
    super().__init__(**kwargs)

    # Ports with shared references
    self.pwr = self.Port(VoltageSink(
      voltage_limits=(2.4, 3.6) * Volt,
      current_draw=(0, 19)*mAmp + self.io_current_draw.upper(),  # rough guesstimate from Figure 11.1 for supply Idd (active mode)
    ), [Power])
    self.gnd = self.Port(Ground(), [Common])

    # Additional ports (on top of IoController)
    # Crystals from table 15, 32, 33
    # TODO Table 32, model crystal load capacitance and series resistance ratings
    self.xtal = self.Port(CrystalDriver(frequency_limits=(1, 25)*MHertz, voltage_out=self.pwr.link().voltage),
                          optional=True)
    # Assumed from "32kHz crystal" in 14.5
    self.xtal_rtc = self.Port(CrystalDriver(frequency_limits=(32, 33)*kHertz, voltage_out=self.pwr.link().voltage),
                              optional=True)

    self.swd = self.Port(SwdTargetPort().empty())
    self._io_ports.insert(0, self.swd)

  def _system_pinmap(self) -> Dict[str, CircuitPort]:
    return VariantPinRemapper({
      'VddA': self.pwr,
      'VssA': self.gnd,
      'VrefP_ADC': self.pwr,
      'VrefP_DAC': self.pwr,
      'VrefN': self.gnd,
      'Vbat': self.pwr,
      'Vss': self.gnd,
      'Vdd': self.pwr,

      'XTALIN': self.xtal.xtal_in,  # TODO Table 3, note 11, float/gnd (gnd preferred) if not used
      'XTALOUT': self.xtal.xtal_out,  # TODO Table 3, note 11, float if not used
      'RTCXIN': self.xtal_rtc.xtal_in,  # 14.5 can be grounded if RTC not used
      'RTCXOUT': self.xtal_rtc.xtal_out,
    }).remap(self.SYSTEM_PIN_REMAP)

  def _io_pinmap(self) -> PinMapUtil:
    # Port models
    dio_5v_model = DigitalBidir.from_supply(
      self.gnd, self.pwr,
      voltage_limit_abs=(0, 5) * Volt,
      current_draw=(0, 0) * Amp,
      current_limits=(-50, 45) * mAmp,
      input_threshold_factor=(0.3, 0.7),
      pullup_capable=True, pulldown_capable=True
    )
    dio_non5v_model = DigitalBidir.from_supply(  # only used when overlapped w/ DAC PIO0_12
      self.gnd, self.pwr,  # up to VddA
      voltage_limit_tolerance=(0, 0) * Volt,
      current_draw=(0, 0) * Amp,
      current_limits=(-50, 45) * mAmp,
      input_threshold_factor=(0.3, 0.7),
      pullup_capable=True, pulldown_capable=True
    )
    dio_highcurrrent_model = DigitalBidir.from_supply(  # only used for PIO0_24
      self.gnd, self.pwr,
      voltage_limit_abs=(0, 5) * Volt,
      current_draw=(0, 0) * Amp,
      current_limits=(-50, 20) * mAmp,  # TODO: 12mA when Vdd < 2.7V
      input_threshold_factor=(0.3, 0.7),
      pullup_capable=True, pulldown_capable=True
    )

    adc_model = AnalogSink(
      voltage_limits=(self.gnd.link().voltage.lower(), self.pwr.link().voltage.upper()),
      current_draw=(0, 0) * Amp,
      impedance=(100, float('inf')) * kOhm
    )
    dac_model = AnalogSource(
      voltage_out=(self.gnd.link().voltage.lower(), self.pwr.link().voltage.upper() - 0.3),
      current_limits=RangeExpr.ALL,  # not given by spec
      impedance=(300, 300) * Ohm  # Table 25, "typical" rating
    )

    uart_model = UartPort(DigitalBidir.empty())
    spi_model = SpiController(DigitalBidir.empty())

    return PinMapUtil([  # partial table for 48- and 64-pin only
      PinResource('PIO0_0', {'PIO0_0': dio_5v_model, 'ADC0_10': adc_model}),
      PinResource('PIO0_1', {'PIO0_1': dio_5v_model, 'ADC0_7': adc_model}),
      PinResource('PIO0_2', {'PIO0_2': dio_5v_model, 'ADC0_6': adc_model}),
      PinResource('PIO0_3', {'PIO0_3': dio_5v_model, 'ADC0_5': adc_model}),
      PinResource('PIO0_4', {'PIO0_4': dio_5v_model, 'ADC0_4': adc_model}),
      PinResource('PIO0_5', {'PIO0_5': dio_5v_model, 'ADC0_3': adc_model}),
      PinResource('PIO0_6', {'PIO0_6': dio_5v_model, 'ADC0_2': adc_model}),
      PinResource('PIO0_7', {'PIO0_7': dio_5v_model, 'ADC0_1': adc_model}),

      PinResource('PIO0_8', {'PIO0_8': dio_5v_model, 'ADC0_0': adc_model}),
      PinResource('PIO0_9', {'PIO0_9': dio_5v_model, 'ADC1_1': adc_model}),
      PinResource('PIO0_10', {'PIO0_10': dio_5v_model, 'ADC1_2': adc_model}),
      PinResource('PIO0_11', {'PIO0_11': dio_5v_model, 'ADC1_3': adc_model}),
      PinResource('PIO0_12', {'PIO0_12': dio_non5v_model, 'DAC_OUT': dac_model}),
      PinResource('PIO0_13', {'PIO0_13': dio_5v_model, 'ADC1_6': adc_model}),
      PinResource('PIO0_14', {'PIO0_14': dio_5v_model, 'ADC1_7': adc_model}),
      PinResource('PIO0_15', {'PIO0_15': dio_5v_model, 'ADC1_8': adc_model}),
      PinResource('PIO0_16', {'PIO0_16': dio_5v_model, 'ADC1_9': adc_model}),
      PinResource('PIO0_17', {'PIO0_17': dio_5v_model}),

      PinResource('PIO0_18', {'PIO0_18': dio_5v_model}),
      PinResource('PIO0_19', {'PIO0_19': dio_5v_model}),
      PinResource('PIO0_20', {'PIO0_20': dio_5v_model}),
      PinResource('PIO0_21', {'PIO0_21': dio_5v_model}),  # also RESET
      PinResource('PIO0_22', {'PIO0_22': dio_5v_model}),
      PinResource('PIO0_23', {'PIO0_23': dio_5v_model}),
      PinResource('PIO0_24', {'PIO0_24': dio_highcurrrent_model}),
      PinResource('PIO0_25', {'PIO0_25': dio_5v_model}),
      PinResource('PIO0_26', {'PIO0_26': dio_5v_model}),

      PinResource('PIO0_27', {'PIO0_27': dio_5v_model}),
      PinResource('PIO0_28', {'PIO0_28': dio_5v_model}),
      PinResource('PIO0_29', {'PIO0_29': dio_5v_model}),
      PinResource('PIO0_30', {'PIO0_30': dio_5v_model, 'ADC0_11': adc_model}),
      PinResource('PIO0_31', {'PIO0_31': dio_5v_model, 'ADC0_9': adc_model}),
      PinResource('PIO1_0', {'PIO1_0': dio_5v_model, 'ADC0_8': adc_model}),
      PinResource('PIO1_1', {'PIO1_1': dio_5v_model, 'ADC1_0': adc_model}),
      PinResource('PIO1_2', {'PIO1_2': dio_5v_model, 'ADC1_4': adc_model}),
      PinResource('PIO1_3', {'PIO1_3': dio_5v_model, 'ADC1_5': adc_model}),
      PinResource('PIO1_4', {'PIO1_4': dio_5v_model, 'ADC1_10': adc_model}),
      PinResource('PIO1_5', {'PIO1_5': dio_5v_model, 'ADC1_11': adc_model}),


      PinResource('PIO1_6', {'PIO1_6': dio_5v_model}),
      PinResource('PIO1_7', {'PIO1_7': dio_5v_model}),
      PinResource('PIO1_8', {'PIO1_8': dio_5v_model}),
      PinResource('PIO1_9', {'PIO1_9': dio_5v_model}),
      PinResource('PIO1_10', {'PIO1_10': dio_5v_model}),
      PinResource('PIO1_11', {'PIO1_11': dio_5v_model}),

      PeripheralAnyResource('UART0', uart_model),
      PeripheralAnyResource('UART1', uart_model),
      PeripheralAnyResource('UART2', uart_model),
      PeripheralAnyResource('SPI0', spi_model),
      PeripheralAnyResource('SPI1', spi_model),
      PeripheralAnyResource('CAN0', CanControllerPort(DigitalBidir.empty())),

      PeripheralFixedResource('I2C0', I2cController(DigitalBidir.empty()), {
        'scl': ['PIO0_22'], 'sda': ['PIO0_23']
      }),
      PeripheralFixedPin('USB', UsbDevicePort(), {
        'dp': 'USB_DP', 'dm': 'USB_DM'
      }),

      # Figure 49: requires a pull-up on SWDIO and pull-down on SWCLK, but none on RESET.
      # Reset has an internal pull-up (or can be configured as unused), except when deep power down is needed
      PeripheralFixedResource('SWD', SwdTargetPort(DigitalBidir.empty()), {
        'swclk': ['PIO0_19'], 'swdio': ['PIO0_20'], 'reset': ['PIO0_21'],
      }),
    ]).remap_pins(self.RESOURCE_PIN_REMAP)

  def generate(self) -> None:
    super().generate()

    self.footprint(
      'U', self.PACKAGE,
      self._make_pinning(),
      mfr='NXP', part=self.PART,
      datasheet='https://www.nxp.com/docs/en/data-sheet/LPC15XX.pdf'
    )
    self.assign(self.lcsc_part, self.LCSC_PART)
    self.assign(self.actual_basic_part, False)


class Lpc1549_48_Device(Lpc1549Base_Device):
  PACKAGE = 'Package_QFP:LQFP-48_7x7mm_P0.5mm'
  PART = 'LPC1549JBD48'
  LCSC_PART = 'C71906'

  SYSTEM_PIN_REMAP = {
    'VddA': '16',
    'VssA': '17',
    'VrefP_ADC': '10',
    'VrefP_DAC': '14',
    'VrefN': '11',
    'Vbat': '30',
    'Vdd': ['27', '39', '42'],
    'Vss': ['20', '40', '41'],
    'XTALIN': '26',
    'XTALOUT': '25',
    'RTCXIN': '31',
    'RTCXOUT': '32',
  }
  RESOURCE_PIN_REMAP = {
    'PIO0_0': '1',
    'PIO0_1': '2',
    'PIO0_2': '3',
    'PIO0_3': '4',
    # 'PIO0_4': '5',  # ISP_0
    'PIO0_5': '6',
    'PIO0_6': '7',
    'PIO0_7': '8',

    'PIO0_8': '9',
    'PIO0_9': '12',
    'PIO0_10': '15',
    'PIO0_11': '18',
    'PIO0_12': '19',
    'PIO0_13': '21',
    'PIO0_14': '22',
    'PIO0_15': '23',
    # 'PIO0_16': '24',  # ISP_1
    'PIO0_17': '28',

    'PIO0_18': '13',
    'PIO0_19': '29',
    'PIO0_20': '33',
    'PIO0_21': '34',
    'PIO0_22': '37',
    'PIO0_23': '38',
    'PIO0_24': '43',
    'PIO0_25': '44',
    'PIO0_26': '45',

    'PIO0_27': '46',
    'PIO0_28': '47',
    'PIO0_29': '48',

    'USB_DP': '35',
    'USB_DM': '36',
  }


class Lpc1549_64_Device(Lpc1549Base_Device):
  PACKAGE = 'Package_QFP:LQFP-64_10x10mm_P0.5mm'
  PART = 'LPC1549JBD64'
  LCSC_PART = 'C74507'

  SYSTEM_PIN_REMAP = {
    'VddA': '20',
    'VssA': '21',
    'VrefP_ADC': '13',
    'VrefP_DAC': '18',
    'VrefN': '14',
    'Vbat': '41',
    'Vdd': ['22', '37', '52', '57'],
    'Vss': ['26', '27', '55', '56'],
    'XTALIN': '36',
    'XTALOUT': '35',
    'RTCXIN': '42',
    'RTCXOUT': '43',
  }
  RESOURCE_PIN_REMAP = {
    'PIO0_0': '2',
    'PIO0_1': '5',
    'PIO0_2': '6',
    'PIO0_3': '7',
    'PIO0_4': '8',
    'PIO0_5': '9',
    'PIO0_6': '10',
    'PIO0_7': '11',

    'PIO0_8': '12',
    'PIO0_9': '16',
    'PIO0_10': '19',
    'PIO0_11': '23',
    'PIO0_12': '24',
    'PIO0_13': '29',
    'PIO0_14': '30',
    'PIO0_15': '31',
    'PIO0_16': '32',
    'PIO0_17': '39',

    'PIO0_18': '17',
    'PIO0_19': '40',
    'PIO0_20': '44',
    'PIO0_21': '45',
    'PIO0_22': '49',
    'PIO0_23': '50',
    'PIO0_24': '58',
    'PIO0_25': '60',
    'PIO0_26': '61',

    'PIO0_27': '62',
    'PIO0_28': '63',
    'PIO0_29': '64',
    'PIO0_30': '1',
    'PIO0_31': '3',
    'PIO1_0': '4',
    'PIO1_1': '15',
    'PIO1_2': '25',
    'PIO1_3': '28',
    'PIO1_4': '33',
    'PIO1_5': '34',
    'PIO1_6': '46',
    'PIO1_7': '51',
    'PIO1_8': '53',
    # 'PIO1_9': '54',  # ISP_0
    'PIO1_10': '59',
    # 'PIO1_11': '38',  # ISP_1

    'USB_DP': '47',
    'USB_DM': '48',
  }


class Lpc1549SwdPull(InternalSubcircuit, Block):
  def __init__(self):
    super().__init__()
    self.pwr = self.Port(VoltageSink.empty(), [Power])
    self.gnd = self.Port(Ground.empty(), [Common])
    self.swd = self.Port(SwdPullPort(DigitalSingleSource.empty()), [InOut])

  def contents(self):
    super().contents()
    self.swd.reset.init_from(DigitalSingleSource())  # not connected, ideal model
    self.swdio = self.Block(PullupResistor((10, 100) * kOhm(tol=0.05))).connected(self.pwr, self.swd.swdio)
    self.swclk = self.Block(PulldownResistor((10, 100) * kOhm(tol=0.05))).connected(self.gnd, self.swd.swclk)


@abstract_block
class Lpc1549Base(IoControllerDac, IoControllerCan, IoControllerUsb, Microcontroller,
                  IoControllerWithSwdTargetConnector, WithCrystalGenerator, IoControllerPowerRequired,
                  BaseIoControllerExportable):
  DEVICE: Type[Lpc1549Base_Device] = Lpc1549Base_Device  # type: ignore
  DEFAULT_CRYSTAL_FREQUENCY = 12*MHertz(tol=0.005)

  def __init__(self, **kwargs):
    super().__init__(**kwargs)
    self.ic: Lpc1549Base_Device

  def contents(self):
    super().contents()

    with self.implicit_connect(
        ImplicitConnect(self.pwr, [Power]),
        ImplicitConnect(self.gnd, [Common])
    ) as imp:
      self.ic = imp.Block(self.DEVICE(pin_assigns=ArrayStringExpr()))  # defined in generator to mix in SWO/TDI
      self.connect(self.xtal_node, self.ic.xtal)
      (self.swd_pull, ), _ = self.chain(self.swd_node,
                                        imp.Block(Lpc1549SwdPull()),
                                        self.ic.swd)

      # one set of 0.1, 0.01uF caps for each Vdd, Vss pin, per reference schematic
      self.pwr_cap = ElementDict[DecouplingCapacitor]()
      for i in range(3):
        self.pwr_cap[i*2] = imp.Block(DecouplingCapacitor(0.1 * uFarad(tol=0.2)))
        self.pwr_cap[i*2+1] = imp.Block(DecouplingCapacitor(0.01 * uFarad(tol=0.2)))
      self.vbat_cap = imp.Block(DecouplingCapacitor(0.1 * uFarad(tol=0.2)))

      # one set of 0.1, 10uF caps for each VddA, VssA pin, per reference schematic
      self.pwra_cap = ElementDict[DecouplingCapacitor]()
      self.pwra_cap[0] = imp.Block(DecouplingCapacitor(0.1 * uFarad(tol=0.2)))
      self.pwra_cap[1] = imp.Block(DecouplingCapacitor(10 * uFarad(tol=0.2)))

      self.vref_cap = ElementDict[DecouplingCapacitor]()
      self.vref_cap[0] = imp.Block(DecouplingCapacitor(0.1 * uFarad(tol=0.2)))
      self.vref_cap[1] = imp.Block(DecouplingCapacitor(0.1 * uFarad(tol=0.2)))
      self.vref_cap[2] = imp.Block(DecouplingCapacitor(10 * uFarad(tol=0.2)))

  def _crystal_required(self) -> bool:  # crystal needed for CAN or USB b/c tighter freq tolerance
    return len(self.get(self.can.requested())) > 0 or len(self.get(self.usb.requested())) > 0 \
        or super()._crystal_required()


class Lpc1549_48(Lpc1549Base):
  DEVICE = Lpc1549_48_Device


class Lpc1549_64(Lpc1549Base):
  DEVICE = Lpc1549_64_Device
