from electronics_abstract_parts import *
from .SpiMemory_93Lc import E93Lc_B
from .JlcPart import JlcPart


class Ft232hl_Device(InternalSubcircuit, FootprintBlock, JlcPart):
  def __init__(self) -> None:
    super().__init__()
    self.gnd = self.Port(Ground())
    self.vregin = self.Port(VoltageSink(  # bus-powered: connect to VBUS
      voltage_limits=(3.6, 5.5)*Volt,  # Table 5.2 for VREGIN=5v
      current_draw=(54, 54)*mAmp  # Table 5.2 typ for VREGIN=5v
    ))
    self.vccd = self.Port(VoltageSource(  # is an output since VREGIN is +5v
      voltage_out=(3.0, 3.6)*Volt,  # not specified, inferred from limits of connected inputs
      current_limits=(0, 62)*mAmp,  # not specified, inferred from draw of connected inputs + EEPROM
    ))
    self.vcccore = self.Port(VoltageSource(  # decouple with 0.1uF cap, recommended 1.62-1.98v
      voltage_out=(1.62, 1.98)*Volt,  # assumed from Vcore limits
      current_limits=(0, 0)*mAmp,  # not specified, external sourcing disallowed
    ))
    self.vcca = self.Port(VoltageSource(  # 1.8v output, decouple with 0.1uF cap
      voltage_out=(1.62, 1.98)*Volt,  # assumed from Vcore limits
    ))

    self.vphy = self.Port(VoltageSink(  # connect to 3v3 through 600R 0.5A ferrite
      voltage_limits=(3.0, 3.6)*Volt,  # Table 5.4
      current_draw=(0.010, 60)*mAmp,  # Table 5.4 suspend typ to operating max
    ))
    self.vpll = self.Port(VoltageSink(  # connect to 3v3 through 600R 0.5A ferrite
      voltage_limits=(3.0, 3.6)*Volt,  # Table 5.4 - both VPHY and VPLL
    ))
    self.vccio = self.Port(VoltageSink(
      voltage_limits=(2.97, 3.63)*Volt,  # Table 5.2, "cells are 5v tolerant"
      # current not specified
    ))

    self.osc = self.Port(CrystalDriver(frequency_limits=12*MHertz(tol=30e-6),
                                       voltage_out=self.vccd.link().voltage))  # assumed
    self.ref = self.Port(Passive())  # connect 12k 1% resistor to GND
    self.usb = self.Port(UsbDevicePort())

    self._dio_model = DigitalBidir.from_supply(  # except USB pins which are not 5v tolerant
      self.gnd, self.vccio,
      current_limits=(-16, 16)*mAmp,  # Table 5.1, assumed bidirectional
      voltage_limit_abs=(-0.3, 5.8)*Volt,  # Table 5.1 high impedance bidirectional
      input_threshold_abs=(0.8, 2.0)*Volt,  # Table 5.3
    )
    self._din_model = DigitalSink.from_bidir(self._dio_model)
    self._dout_model = DigitalSource.from_bidir(self._dio_model)

    self.nreset = self.Port(self._din_model, optional=True)

    self.eecs = self.Port(self._dout_model, optional=True)
    self.eeclk = self.Port(self._dout_model, optional=True)
    self.eedata = self.Port(self._dio_model, optional=True)

    # TODO these should be aliased to the supported serial buses
    self.adbus = self.Port(Vector(DigitalBidir.empty()))
    self.acbus = self.Port(Vector(DigitalBidir.empty()))

  def contents(self):
    super().contents()

    for i in range(8):
      self.adbus.append_elt(self._dio_model, str(i))
    for i in range(10):  # these are GPIOs
      self.acbus.append_elt(self._dio_model, str(i))

    self.footprint(  # pinning in order of table in Section 3.3
      'U', 'Package_QFP:LQFP-48_7x7mm_P0.5mm',
      {
        '40': self.vregin,
        '37': self.vcca,
        '38': self.vcccore,
        '39': self.vccd,
        '12': self.vccio,
        '24': self.vccio,
        '46': self.vccio,
        '8': self.vpll,
        '3': self.vphy,
        '4': self.gnd,  # AGND
        '9': self.gnd,  # AGND
        '41': self.gnd,  # AGND
        '10': self.gnd,
        '11': self.gnd,
        '22': self.gnd,
        '23': self.gnd,
        '35': self.gnd,
        '36': self.gnd,
        '47': self.gnd,
        '48': self.gnd,

        '1': self.osc.xtal_in,
        '2': self.osc.xtal_out,
        '5': self.ref,
        '6': self.usb.dm,
        '7': self.usb.dp,
        '42': self.gnd,  # TEST
        '34': self.nreset,  # active-low reset

        '45': self.eecs,
        '44': self.eeclk,
        '43': self.eedata,

        '13': self.adbus['0'],
        '14': self.adbus['1'],
        '15': self.adbus['2'],
        '16': self.adbus['3'],
        '17': self.adbus['4'],
        '18': self.adbus['5'],
        '19': self.adbus['6'],
        '20': self.adbus['7'],

        '21': self.acbus['0'],
        '25': self.acbus['1'],
        '26': self.acbus['2'],
        '27': self.acbus['3'],
        '28': self.acbus['4'],
        '29': self.acbus['5'],
        '30': self.acbus['6'],
        '31': self.acbus['7'],  # aka #PWRSAV
        '32': self.acbus['8'],
        '33': self.acbus['9'],
      },
      mfr='FTDI, Future Technology Devices International Ltd', part='FT232HL',
      datasheet='https://ftdichip.com/wp-content/uploads/2020/07/DS_FT232H.pdf'
    )
    self.assign(self.lcsc_part, "C51997")  # FT232HL-REEL
    self.assign(self.actual_basic_part, False)


class Ft232EepromDriver(InternalSubcircuit, Block):
  """Adapts the EECLK and EEDATA pins of the FT232 to the SPI of the EEPROM"""
  def __init__(self):
    super().__init__()
    self.pwr = self.Port(VoltageSink.empty())
    self.eeclk = self.Port(DigitalSink.empty())
    self.eedata = self.Port(DigitalBidir.empty())
    self.spi = self.Port(SpiController.empty())

  def contents(self):
    self.connect(self.eeclk, self.spi.sck)
    self.connect(self.eedata, self.spi.mosi)
    self.do_pull = self.Block(PullupResistor(10*kOhm(tol=0.05))).connected(self.pwr, self.spi.miso)
    self.do_res = self.Block(Resistor(2*kOhm(tol=0.05)))
    self.connect(self.spi.miso, self.do_res.a.adapt_to(DigitalSink()))  # sink side port is ideal
    self.connect(self.eedata, self.do_res.b.adapt_to(DigitalSource(
      voltage_out=self.spi.miso.link().voltage,
      output_thresholds=self.spi.miso.link().output_thresholds
    )))


class Ft232hl(Interface, GeneratorBlock):
  """USB multiprotocol converter"""
  def __init__(self) -> None:
    super().__init__()
    self.ic = self.Block(Ft232hl_Device())
    # TODO connect to 3.3v from ferrite
    self.pwr = self.Port(VoltageSink.empty(), [Power])
    self.gnd = self.Export(self.ic.gnd, [Common])

    self.usb = self.Export(self.ic.usb)

    # connect one of UART, MPSSE, or ADBUS pins
    self.uart = self.Port(UartPort.empty(), optional=True)
    self.mpsse = self.Port(SpiController.empty(), optional=True)
    self.mpsse_cs = self.Port(DigitalSource.empty(), optional=True)

    self.adbus = self.Port(Vector(DigitalBidir.empty()))
    self.acbus = self.Export(self.ic.acbus)

    # the generator is needed to mux the shared MPSSE and ADBUS pins
    self.generator_param(self.uart.is_connected(), self.mpsse.is_connected(), self.mpsse_cs.is_connected(),
                         self.adbus.requested())

  def contents(self) -> None:
    # connections from Figure 6.1, bus powered configuration
    self.vbus_fb = self.Block(SeriesPowerFerriteBead(hf_impedance=(600*Ohm(tol=0.25)))) \
      .connected(self.pwr, self.ic.vregin)

    cap_model = DecouplingCapacitor(0.1*uFarad(tol=0.2))
    self.vregin_cap0 = self.Block(DecouplingCapacitor(4.7*uFarad(tol=0.2))).connected(self.gnd, self.ic.vregin)
    self.vregin_cap1 = self.Block(cap_model).connected(self.gnd, self.ic.vregin)

    self.vphy_fb = self.Block(SeriesPowerFerriteBead(hf_impedance=(600*Ohm(tol=0.25)))) \
      .connected(self.ic.vccd, self.ic.vphy)
    self.vphy_cap = self.Block(cap_model).connected(self.gnd, self.ic.vphy)

    self.vpll_fb = self.Block(SeriesPowerFerriteBead(hf_impedance=(600*Ohm(tol=0.25)))) \
      .connected(self.ic.vccd, self.ic.vpll)
    self.vpll_cap = self.Block(cap_model).connected(self.gnd, self.ic.vpll)

    self.vcccore_cap = self.Block(cap_model).connected(self.gnd, self.ic.vcccore)
    self.vcca_cap = self.Block(cap_model).connected(self.gnd, self.ic.vcca)

    self.vccd_cap = self.Block(cap_model).connected(self.gnd, self.ic.vccd)

    self.connect(self.ic.vccd, self.ic.vccio)
    self.vccio_cap0 = self.Block(cap_model).connected(self.gnd, self.ic.vccio)
    self.vccio_cap1 = self.Block(cap_model).connected(self.gnd, self.ic.vccio)
    self.vccio_cap2 = self.Block(cap_model).connected(self.gnd, self.ic.vccio)

    self.ref_res = self.Block(Resistor(12*kOhm(tol=0.01)))
    self.connect(self.ref_res.a, self.ic.ref)
    self.connect(self.ref_res.b.adapt_to(Ground()), self.gnd)

    self.connect(self.ic.vccd.as_digital_source(), self.ic.nreset)  # in concept driven by VccIO

    self.crystal = self.Block(OscillatorReference(frequency=12*MHertz(tol=30e-6)))
    self.connect(self.crystal.gnd, self.gnd)
    self.connect(self.crystal.crystal, self.ic.osc)

    # optional EEPROM
    self.eeprom = self.Block(E93Lc_B(Range.exact(2 * 1024)))
    self.connect(self.eeprom.gnd, self.gnd)
    self.connect(self.eeprom.pwr, self.ic.vccio)
    self.connect(self.eeprom.cs, self.ic.eecs)
    self.eeprom_spi = self.Block(Ft232EepromDriver())
    self.connect(self.eeprom_spi.pwr, self.ic.vccio)
    self.connect(self.eeprom_spi.eeclk, self.ic.eeclk)
    self.connect(self.eeprom_spi.eedata, self.ic.eedata)
    self.connect(self.eeprom_spi.spi, self.eeprom.spi)

  def generate(self) -> None:
    # make connections and pin mutual exclusion constraints
    if self.get(self.uart.is_connected()):
      self.connect(self.uart.tx, self.ic.adbus.request('0'))
      self.connect(self.uart.rx, self.ic.adbus.request('1'))
    self.require(self.uart.is_connected().implies(~self.mpsse.is_connected()))
    self.require(self.uart.is_connected().implies('0' not in self.get(self.adbus.requested()) and
                                                  '1' not in self.get(self.adbus.requested())))

    if self.get(self.mpsse.is_connected()):
      self.connect(self.mpsse.sck, self.ic.adbus.request('0'))
      self.connect(self.mpsse.mosi, self.ic.adbus.request('1'))
      self.connect(self.mpsse.miso, self.ic.adbus.request('2'))
    if self.get(self.mpsse_cs.is_connected()):
      self.connect(self.mpsse_cs, self.ic.adbus.request('3'))
    # UART mutual exclusion already handled above
    self.require(self.mpsse.is_connected().implies('0' not in self.get(self.adbus.requested()) and
                                                   '1' not in self.get(self.adbus.requested()) and
                                                   '2' not in self.get(self.adbus.requested())))
    self.require(self.mpsse_cs.is_connected().implies('3' not in self.get(self.adbus.requested())))

    # require something to be connected
    self.require(self.uart.is_connected() | self.mpsse.is_connected() | bool(self.get(self.adbus.requested())))

    for elt in self.get(self.adbus.requested()):
      self.connect(self.adbus.append_elt(DigitalBidir.empty(), elt), self.ic.adbus.request(elt))
