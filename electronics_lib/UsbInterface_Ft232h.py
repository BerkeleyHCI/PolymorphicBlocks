from electronics_abstract_parts import *
from .JlcPart import JlcPart


class Ft232hl_Device(DiscreteChip, FootprintBlock, JlcPart):
  def __init__(self) -> None:
    super().__init__()
    self.gnd = self.Port(Ground())
    self.vregin = self.Port(VoltageSink(  # bus-powered: connect to VBUS
      voltage_limits=(3.6, 5.5)*Volt,  # Table 5.2 for VREGIN=5v
      current_draw=(54, 54)*mAmp  # Table 5.2 typ for VREGIN=5v
    ))
    self.vccd = self.Port(VoltageSource(  # is an output since VREGIN is +5v
      voltage_out=(3.0, 3.6)*Volt,  # not specified, inferred from limits of connected inputs
      current_limits=(0, 60)*mAmp,  # not specified, inferred from draw of connected inputs
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

    dio_model = DigitalBidir.from_supply(  # except USB pins which are not 5v tolerant
      self.gnd, self.vccio,
      current_limits=(-16, 16)*mAmp,  # Table 5.1, assumed bidirectional
      voltage_limit_abs=(-0.3, 5.8)*Volt,  # Table 5.1 high impedance bidirectional
      input_threshold_abs=(0.8, 2.0)*Volt,  # Table 5.3
    )
    din_model = DigitalSink.from_bidir(dio_model)

    self.nreset = self.Port(din_model, optional=True)

    # TODO these should be aliased to the supported serial buses
    self.adbus0 = self.Port(dio_model, optional=True)
    self.adbus1 = self.Port(dio_model, optional=True)
    self.adbus2 = self.Port(dio_model, optional=True)
    self.adbus3 = self.Port(dio_model, optional=True)
    self.adbus4 = self.Port(dio_model, optional=True)
    self.adbus5 = self.Port(dio_model, optional=True)
    self.adbus6 = self.Port(dio_model, optional=True)
    self.adbus7 = self.Port(dio_model, optional=True)

    # these are GPIOs
    self.acbus0 = self.Port(dio_model, optional=True)
    self.acbus1 = self.Port(dio_model, optional=True)
    self.acbus2 = self.Port(dio_model, optional=True)
    self.acbus3 = self.Port(dio_model, optional=True)
    self.acbus4 = self.Port(dio_model, optional=True)
    self.acbus5 = self.Port(dio_model, optional=True)
    self.acbus6 = self.Port(dio_model, optional=True)
    self.acbus7 = self.Port(dio_model, optional=True)
    self.acbus8 = self.Port(dio_model, optional=True)
    self.acbus9 = self.Port(dio_model, optional=True)

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

        # TODO IMPLEMENT ME EEPROM
        # '45': self.eecs,
        # '44': self.eeclk,
        # '43': self.eedata,

        '13': self.adbus0,
        '14': self.adbus1,
        '15': self.adbus2,
        '16': self.adbus3,
        '17': self.adbus4,
        '18': self.adbus5,
        '19': self.adbus6,
        '20': self.adbus7,

        '21': self.acbus0,
        '25': self.acbus1,
        '26': self.acbus2,
        '27': self.acbus3,
        '28': self.acbus4,
        '29': self.acbus5,
        '30': self.acbus6,
        '31': self.acbus7,  # aka #PWRSAV
        '32': self.acbus8,
        '33': self.acbus9,
      },
      mfr='FTDI, Future Technology Devices International Ltd', part='FT232HL',
      datasheet='https://ftdichip.com/wp-content/uploads/2020/07/DS_FT232H.pdf'
    )
    self.assign(self.lcsc_part, "C51997")  # FT232HL-REEL
    self.assign(self.actual_basic_part, False)


class Ft232hl(GeneratorBlock):
  """USB multiprotocol converter"""
  def __init__(self) -> None:
    super().__init__()
    self.ic = self.Block(Ft232hl_Device())
    # TODO connect to 3.3v from ferrite
    self.pwr = self.Export(self.ic.vregin, [Power])
    self.gnd = self.Export(self.ic.gnd, [Common])

    self.usb = self.Export(self.ic.usb)

    # connect one of UART, MPSSE, or ADBUS pins
    self.uart = self.Port(UartPort.empty(), optional=True)
    self.mpsse = self.Port(SpiMaster.empty(), optional=True)
    self.mpsse_cs = self.Port(DigitalSource.empty(), optional=True)

    self.adbus0 = self.Port(DigitalBidir.empty(), optional=True)
    self.adbus1 = self.Port(DigitalBidir.empty(), optional=True)
    self.adbus2 = self.Port(DigitalBidir.empty(), optional=True)
    self.adbus3 = self.Port(DigitalBidir.empty(), optional=True)
    self.adbus4 = self.Port(DigitalBidir.empty(), optional=True)
    self.adbus5 = self.Port(DigitalBidir.empty(), optional=True)
    self.adbus6 = self.Port(DigitalBidir.empty(), optional=True)
    self.adbus7 = self.Port(DigitalBidir.empty(), optional=True)

    self.acbus0 = self.Export(self.ic.acbus0, optional=True)
    self.acbus1 = self.Export(self.ic.acbus1, optional=True)
    self.acbus2 = self.Export(self.ic.acbus2, optional=True)
    self.acbus3 = self.Export(self.ic.acbus3, optional=True)
    self.acbus4 = self.Export(self.ic.acbus4, optional=True)
    self.acbus5 = self.Export(self.ic.acbus5, optional=True)
    self.acbus6 = self.Export(self.ic.acbus6, optional=True)
    self.acbus7 = self.Export(self.ic.acbus7, optional=True)
    self.acbus8 = self.Export(self.ic.acbus8, optional=True)
    self.acbus9 = self.Export(self.ic.acbus9, optional=True)

    self.generator(self.generate, self.uart.is_connected(), self.mpsse.is_connected(), self.mpsse_cs.is_connected(),
                   self.adbus0.is_connected(), self.adbus1.is_connected(),
                   self.adbus2.is_connected(), self.adbus3.is_connected(),
                   self.adbus4.is_connected(), self.adbus5.is_connected(),
                   self.adbus6.is_connected(), self.adbus7.is_connected())

  def generate(self, uart_connected: bool, mpsse_connected: bool, mpsse_cs_connected: bool,
               adbus0_connected: bool, adbus1_connected: bool, adbus2_connected: bool, adbus3_connected: bool,
               adbus4_connected: bool, adbus5_connected: bool, adbus6_connected: bool, adbus7_connected: bool) -> None:
    # make connections and pin mutual exclusion constraints
    if uart_connected:
      self.connect(self.uart.tx, self.ic.adbus0)
      self.connect(self.uart.rx, self.ic.adbus1)
    self.require(self.uart.is_connected().implies(~self.mpsse.is_connected()))
    self.require(self.uart.is_connected().implies(~self.adbus0.is_connected() & ~self.adbus1.is_connected()))

    if mpsse_connected:
      self.connect(self.mpsse.sck, self.ic.adbus0)
      self.connect(self.mpsse.mosi, self.ic.adbus1)
      self.connect(self.mpsse.miso, self.ic.adbus2)
    if mpsse_cs_connected:
      self.connect(self.mpsse_cs, self.ic.adbus3)
    # UART mutual exclusion already handled above
    self.require(self.mpsse.is_connected().implies(
      ~self.adbus0.is_connected() & ~self.adbus1.is_connected() & ~self.adbus2.is_connected()))
    self.require(self.mpsse_cs.is_connected().implies(~self.adbus3.is_connected()))

    adbus_pairs = [
      (adbus0_connected, self.adbus0, self.ic.adbus0),
      (adbus1_connected, self.adbus1, self.ic.adbus1),
      (adbus2_connected, self.adbus2, self.ic.adbus2),
      (adbus3_connected, self.adbus3, self.ic.adbus3),
      (adbus4_connected, self.adbus4, self.ic.adbus4),
      (adbus5_connected, self.adbus5, self.ic.adbus5),
      (adbus6_connected, self.adbus6, self.ic.adbus6),
      (adbus7_connected, self.adbus7, self.ic.adbus7),
    ]
    for (port_connected, port, ic_port) in adbus_pairs:
      if port_connected:
        self.connect(port, ic_port)

    self.require(self.uart.is_connected() | self.mpsse.is_connected() |
                 self.adbus0.is_connected() | self.adbus1.is_connected() | self.adbus2.is_connected() |
                 self.adbus3.is_connected() | self.adbus4.is_connected() | self.adbus5.is_connected() |
                 self.adbus6.is_connected() | self.adbus7.is_connected())

    # connections from Figure 6.1, bus powered configuration
    cap_model = DecouplingCapacitor(0.1*uFarad(tol=0.2))
    self.vregin_cap0 = self.Block(DecouplingCapacitor(4.7*uFarad(tol=0.2))).connected(self.gnd, self.ic.vregin)
    self.vregin_cap1 = self.Block(cap_model).connected(self.gnd, self.ic.vregin)

    self.connect(self.ic.vccd, self.ic.vphy)  # TODO through a ferrite
    self.vphy_cap = self.Block(cap_model).connected(self.gnd, self.ic.vphy)

    self.connect(self.ic.vccd, self.ic.vpll)  # TODO through a ferrite
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

    self.crystal = self.Block(OscillatorCrystal(frequency=12*MHertz(tol=30e-6)))
    self.connect(self.crystal.gnd, self.gnd)
    self.connect(self.crystal.crystal, self.ic.osc)
