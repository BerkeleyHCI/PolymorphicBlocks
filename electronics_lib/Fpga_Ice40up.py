from typing import *

from electronics_abstract_parts import *
from .JlcPart import JlcPart
from .PassiveConnector import PinHeader127DualShrouded


class Ice40TargetHeader(ProgrammingConnector, FootprintBlock):
  """Custom programming header for iCE40 loosely based on the SWD pinning"""
  def __init__(self):
    super().__init__()
    self.pwr = self.Port(VoltageSink.empty(), [Power])  # in practice this can power the target
    self.gnd = self.Port(Ground.empty(), [Common])  # TODO pin at 0v
    self.spi = self.Port(SpiMaster.empty())
    self.cs = self.Port(DigitalSource.empty())
    self.reset = self.Port(DigitalSource.empty())

  def contents(self):
    super().contents()
    self.conn = self.Block(PinHeader127DualShrouded(10))
    self.connect(self.pwr, self.conn.pins.request('1').adapt_to(VoltageSink()))
    self.connect(self.gnd, self.conn.pins.request('3').adapt_to(Ground()),
                 self.conn.pins.request('5').adapt_to(Ground()),
                 self.conn.pins.request('9').adapt_to(Ground()))
    self.connect(self.cs, self.conn.pins.request('2').adapt_to(DigitalSource()))  # swd: swdio
    self.connect(self.spi.sck, self.conn.pins.request('4').adapt_to(DigitalSource()))  # swd: swclk
    self.connect(self.spi.mosi, self.conn.pins.request('6').adapt_to(DigitalSource()))  # swd: swo
    self.connect(self.spi.miso, self.conn.pins.request('8').adapt_to(DigitalSink()))  # swd: NC or jtag: tdi
    self.connect(self.reset, self.conn.pins.request('10').adapt_to(DigitalSource()))


@abstract_block
class Ice40up_Device(BaseIoControllerPinmapGenerator, InternalSubcircuit, GeneratorBlock, JlcPart, FootprintBlock):
  """Base class for iCE40 UltraPlus FPGAs, 2.8k-5.2k logic cells."""
  SYSTEM_PIN_REMAP: Dict[str, Union[str, List[str]]]  # pin name in base -> pin name(s)
  RESOURCE_PIN_REMAP: Dict[str, str]  # resource name in base -> pin name
  PACKAGE: str  # package name for footprint(...)
  PART: str  # part name for footprint(...)
  JLC_PART: str  # part number for lcsc_part

  BITSTREAM_BITS: int = 0

  @staticmethod
  def make_dio_model(gnd: VoltageSink, vccio: VoltageSink):
    return DigitalBidir.from_supply(
      gnd, vccio,
      voltage_limit_tolerance=(-0.3, 0.2) * Volt,  # table 4.13
      current_limits=(-8, 8)*mAmp,  # for LVCMOS 3.3 (least restrictive)
      current_draw=(0, 0)*Amp,
      input_threshold_abs=(0.8, 2.0),  # most restrictive, for LVCMOS 3.3
      pullup_capable=True, pulldown_capable=False,
    )

  def __init__(self, **kwargs) -> None:
    super().__init__(**kwargs)

    self.gnd = self.Port(Ground(), [Common])
    self.vccio_1 = self.Port(VoltageSink(
      voltage_limits=(1.71, 3.46)*Volt,  # table 4.2
      current_draw=(0.0005, 9)*mAmp + self.io_current_draw.upper()  # table 4.6, static to startup peak; no max given
    ))  # TODO IO currents should be allocated per-bank

    vccio_model = VoltageSink(
      voltage_limits=(1.71, 3.46)*Volt,  # table 4.2
      current_draw=(0.0005, 2) * mAmp  # table 4.6, static to startup peak
    )
    self.vccio_0 = self.Port(vccio_model)
    self.vccio_2 = self.Port(vccio_model)

    self.vcc = self.Port(VoltageSink(  # core supply voltage
      voltage_limits=(1.14, 1.26) * Volt,  # table 4.2
      current_draw=(0.075, 12) * mAmp  # table 4.6, static to startup peak; no max given
    ))
    self.vpp_2v5 = self.Port(VoltageSink(  # NVCM operating voltage, excluding programming mode
      voltage_limits=(2.3, 3.45) * Volt,  # table 4.2, for master/slave/NVCM config
    ))
    self.vcc_pll = self.Port(VoltageSink(  # PLL supply voltage
      voltage_limits=(1.14, 1.26) * Volt,  # table 4.2
    ))
    # note, section 4.5 recommended power sequence: Vcc, Vcc_pll -> Spi_VccIO1 -> Vpp_2v5
    # VccIO0/2 can be applied anytime after Vcc, Vcc_pll
    self._pio1_model = self.make_dio_model(self.gnd, self.vccio_1)
    self._dpio1_model = self._pio1_model

    self.creset_b = self.Port(DigitalSink.from_bidir(self._pio1_model))  # no internal PUR, must be driven (or 10k pulled up)
    self.cdone = self.Port(DigitalSource.from_bidir(self._pio1_model), optional=True)  # dedicated on SG48, shared on UWG30

    # TODO requirements on SPI device frequency
    # TODO this is really bidirectional, so this could be either separate ports or split ports
    self.spi_config = self.Port(SpiMaster(self._dpio1_model))
    self.spi_config_cs = self.Port(self._dpio1_model)

  def _system_pinmap(self) -> Dict[str, CircuitPort]:    # names consistent with pinout spreadsheet
    return VariantPinRemapper({
      'VCCPLL': self.vcc_pll,
      'VCC': self.vcc,
      'SPI_Vccio1': self.vccio_1,
      'VCCIO_0': self.vccio_0,
      'VCCIO_2': self.vccio_2,
      'VPP_2V5': self.vpp_2v5,
      'GND': self.gnd,

      'CRESET_B': self.creset_b,
      'CDONE': self.cdone,

      'IOB_32a_SPI_SO': self.spi_config.mosi,
      'IOB_33b_SPI_SI': self.spi_config.miso,
      'IOB_34a_SPI_SCK': self.spi_config.sck,
      'IOB_35b_SPI_SS': self.spi_config_cs,
    }).remap(self.SYSTEM_PIN_REMAP)

  def _io_pinmap(self) -> PinMapUtil:
    pio0_model = self.make_dio_model(self.gnd, self.vccio_0)
    dpio0_model = pio0_model  # differential capability currently not modeled
    pio1_model = self._pio1_model
    dpio1_model = self._dpio1_model
    pio2_model = self.make_dio_model(self.gnd, self.vccio_2)
    dpio2_model = pio2_model


  # hard macros, not tied to any particular pin
    i2c_model = I2cMaster(DigitalBidir.empty())  # user I2C, table 4.7
    spi_model = SpiMaster(DigitalBidir.empty(), (0, 45)*MHertz)  # user SPI, table 4.10

    return PinMapUtil([  # names consistent with pinout spreadsheet
      PinResource('IOB_0a', {'IOB_0a': pio2_model}),
      PinResource('IOB_2a', {'IOB_2a': dpio2_model}),
      PinResource('IOB_3b_G6', {'IOB_3b_G6': dpio2_model}),
      PinResource('IOB_4a', {'IOB_4a': dpio2_model}),
      PinResource('IOB_5b', {'IOB_5b': dpio2_model}),
      PinResource('IOB_6a', {'IOB_6a': pio2_model}),
      PinResource('IOB_8a', {'IOB_8a': dpio2_model}),
      PinResource('IOB_9b', {'IOB_9b': dpio2_model}),

      PinResource('IOB_10a', {'IOB_10a': dpio1_model}),
      PinResource('IOB_11b_G5', {'IOB_11b_G5': dpio1_model}),
      PinResource('IOB_12a_G4', {'IOB_12a_G4': dpio1_model}),  # shared with DONE on UWG30
      PinResource('IOB_13b', {'IOB_13b': dpio1_model}),
      PinResource('IOB_16a', {'IOB_16a': pio1_model}),
      PinResource('IOB_18a', {'IOB_18a': pio1_model}),
      PinResource('IOB_20a', {'IOB_20a': pio1_model}),
      PinResource('IOB_22a', {'IOB_22a': dpio1_model}),
      PinResource('IOB_23b', {'IOB_23b': dpio1_model}),
      PinResource('IOB_24a', {'IOB_24a': dpio1_model}),
      PinResource('IOB_25b_G3', {'IOB_25b_G3': dpio1_model}),
      PinResource('IOB_29b', {'IOB_29b': pio1_model}),
      PinResource('IOB_31b', {'IOB_31b': pio1_model}),

      PinResource('IOB_36b', {'IOB_36b': dpio0_model}),
      PinResource('IOB_37a', {'IOB_37a': dpio0_model}),
      PinResource('IOB_38b', {'IOB_38b': dpio0_model}),
      PinResource('IOB_39a', {'IOB_39a': dpio0_model}),
      PinResource('IOB_41a', {'IOB_41a': pio0_model}),
      PinResource('IOB_42b', {'IOB_42b': dpio0_model}),
      PinResource('IOB_43a', {'IOB_43a': dpio0_model}),
      PinResource('IOB_44b', {'IOB_44b': dpio0_model}),
      PinResource('IOB_45a_G1', {'IOB_45a_G1': dpio0_model}),
      PinResource('IOB_46b_G0', {'IOB_46b_G0': dpio0_model}),
      PinResource('IOB_47a', {'IOB_47a': pio0_model}),
      PinResource('IOB_48b', {'IOB_48b': dpio0_model}),
      PinResource('IOB_49a', {'IOB_49a': dpio0_model}),
      PinResource('IOB_50b', {'IOB_50b': dpio0_model}),
      PinResource('IOB_51a', {'IOB_51a': dpio0_model}),

      # RGB2/1/0 skipped since they're open-drain only and constant-current analog drive

      # hard macros I2C and SPI
      PeripheralAnyResource('I2C1', i2c_model),
      PeripheralAnyResource('I2C1', i2c_model),
      PeripheralAnyResource('SPI1', spi_model),
      PeripheralAnyResource('SPI2', spi_model),
    ]).remap_pins(self.RESOURCE_PIN_REMAP)

  def generate(self) -> None:
    super().generate()

    self.footprint(
      'U', self.PACKAGE,
      self._make_pinning(),
      mfr='Lattice Semiconductor Corporation', part=self.PART,
      datasheet='https://www.latticesemi.com/-/media/LatticeSemi/Documents/DataSheets/iCE/iCE40-UltraPlus-Family-Data-Sheet.ashx'
    )
    self.assign(self.lcsc_part, self.JLC_PART)
    self.assign(self.actual_basic_part, False)


class Ice40up5k_Sg48_Device(Ice40up_Device):
  SYSTEM_PIN_REMAP = {
    'VCCPLL': '29',
    'VCC': ['5', '30'],
    'SPI_Vccio1': '22',
    'VCCIO_0': '33',
    'VCCIO_2': '1',
    'VPP_2V5': '24',
    'GND': '49',  # "Paddle"

    'CRESET_B': '8',
    'CDONE': '7',

    'IOB_32a_SPI_SO': '14',
    'IOB_33b_SPI_SI': '17',
    'IOB_34a_SPI_SCK': '15',
    'IOB_35b_SPI_SS': '16',
  }

  RESOURCE_PIN_REMAP = {
    'IOB_0a': '46',
    'IOB_2a': '47',
    'IOB_3b_G6': '44',
    'IOB_4a': '48',
    'IOB_5b': '45',
    'IOB_6a': '2',
    'IOB_8a': '4',
    'IOB_9b': '3',
    'IOB_13b': '6',
    'IOB_16a': '9',
    'IOB_18a': '10',
    'IOB_20a': '11',
    'IOB_22a': '12',
    'IOB_23b': '21',
    'IOB_24a': '13',
    'IOB_25b_G3': '20',
    'IOB_29b': '19',
    'IOB_31b': '18',
    'IOB_36b': '25',
    'IOB_37a': '23',
    'IOB_38b': '27',
    'IOB_39a': '26',
    'IOB_41a': '28',
    'IOB_42b': '31',
    'IOB_43a': '32',
    'IOB_44b': '34',
    'IOB_45a_G1': '37',
    'IOB_46b_G0': '35',
    'IOB_48b': '36',
    'IOB_49a': '43',
    'IOB_50b': '38',
    'IOB_51a': '42',
  }

  PACKAGE = 'Package_DFN_QFN:QFN-48-1EP_7x7mm_P0.5mm_EP5.3x5.3mm'
  PART = 'ICE40UP5K-SG48'
  JLC_PART = 'C2678152'

  BITSTREAM_BITS = 833288


@abstract_block
class Ice40up(Fpga, IoController):
  """Application circuit for the iCE40UP series FPGAs, pre-baked for 'common' applications
  (3.3v supply with 1.2v core not shared, external FLASH programming, no NVCM programming).

  TODO: generator support for CRAM (volatile) programming mode, diode 2v5 NVCM supply.
  """
  DEVICE: Type[Ice40up_Device] = Ice40up_Device

  def __init__(self, **kwargs):
    super().__init__(**kwargs)
    self.cdone = self.Port(DigitalSource.empty(), optional=True)

  def contents(self):
    super().contents()

    # schematics don't seem to be available for the official reference designs,
    # so the decoupling caps are kind of arbitrary (except the PLL)
    # in theory, there are supply sequencing requirements, but designs like UPduino
    # seem to work fine without sequencing circuitry
    with self.implicit_connect(
        ImplicitConnect(self.pwr, [Power]),
        ImplicitConnect(self.gnd, [Common])
    ) as imp:
      self.ic = imp.Block(self.DEVICE(pin_assigns=self.pin_assigns))
      self.connect(self.pwr, self.ic.vccio_1, self.ic.vccio_0, self.ic.vccio_2, self.ic.vpp_2v5)
      self._export_ios_from(self.ic)
      self.assign(self.actual_pin_assigns, self.ic.actual_pin_assigns)
      self.connect(self.ic.cdone, self.cdone)

      self.vcc_reg = imp.Block(LinearRegulator((1.14, 1.26)*Volt))
      self.reset_pu = imp.Block(PullupResistor(10*kOhm(tol=0.05))).connected(io=self.ic.creset_b)

      self.mem = imp.Block(SpiMemory(Range.from_lower(self.ic.BITSTREAM_BITS)))

      self.prog = imp.Block(Ice40TargetHeader())
      self.connect(self.prog.reset, self.ic.creset_b)

      # this defaults to flash programming, but to use CRAM programming you can swap the
      # SDI/SDO pins on the debug probe and disconnect the CS line
      self.spi_merge = self.Block(MergedSpiMaster()).connected_from(self.ic.spi_config, self.prog.spi)
      self.connect(self.spi_merge.out, self.mem.spi)
      self.connect(self.ic.spi_config_cs, self.prog.cs)
      (self.cs_jmp, ), _ = self.chain(self.ic.spi_config_cs, self.Block(DigitalJumper()), self.mem.cs)
      # SPI_SS_B is sampled on boot to determine boot config, needs to be high for PROM config
      self.mem_pu = imp.Block(PullupResistor(10*kOhm(tol=0.05))).connected(io=self.mem.cs)

      self.vio_cap0 = imp.Block(DecouplingCapacitor(0.1 * uFarad(tol=0.2)))
      self.vio_cap1 = imp.Block(DecouplingCapacitor(0.1 * uFarad(tol=0.2)))
      self.vio_cap2 = imp.Block(DecouplingCapacitor(0.1 * uFarad(tol=0.2)))
      self.vpp_cap = imp.Block(DecouplingCapacitor(0.1 * uFarad(tol=0.2)))

    with self.implicit_connect(  # Vcc (core) power domain
        ImplicitConnect(self.vcc_reg.pwr_out, [Power]),
        ImplicitConnect(self.gnd, [Common])
    ) as imp:
      self.connect(self.vcc_reg.pwr_out, self.ic.vcc)
      self.pll_res = imp.Block(SeriesPowerResistor(100*Ohm(tol=0.05)))

      self.vcc_cap = imp.Block(DecouplingCapacitor(0.1 * uFarad(tol=0.2)))

    with self.implicit_connect(  # PLL power domain, section 2 of the iCE40 Hardware Checklist
        ImplicitConnect(self.pll_res.pwr_out, [Power]),
        ImplicitConnect(self.gnd, [Common])
    ) as imp:
      self.connect(self.pll_res.pwr_out, self.ic.vcc_pll)

      self.pll_lf = imp.Block(DecouplingCapacitor(10 * uFarad(tol=0.2)))
      self.pll_hf = imp.Block(DecouplingCapacitor(0.1 * uFarad(tol=0.2)))


class Ice40up5k_Sg48(Ice40up):
  DEVICE = Ice40up5k_Sg48_Device
