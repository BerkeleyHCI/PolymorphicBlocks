from electronics_abstract_parts import *
from .JlcPart import JlcPart


class Ft232hl_Device(DiscreteChip, FootprintBlock, JlcPart):
  def __init__(self) -> None:
    super().__init__()
    self.gnd = self.Port(Ground())
    self.vregin = self.Port(VoltageSink(  # bus-powered: connect to VBUS
      #voltage_limits=(4.0, 5.25)*Volt,  # Table 6
      #current_draw=(0.080, 26)*mAmp  # TAble 3, suspended typ to normal max
    ))
    self.vccd = self.Port(VoltageSource(  # is an output since VREGIN is +5v
      # voltage_out=(3.0, 3.6)*Volt,  # Table 6
      # current_limits=(0, 100)*mAmp,  # Table 6 note
    ))
    self.vcccore = self.Port(VoltageSource(  # decouple with 0.1uF cap
      # voltage_out=(3.0, 3.6)*Volt,  # Table 6
      # current_limits=(0, 100)*mAmp,  # Table 6 note
    ))
    self.vcca = self.Port(VoltageSource(  # decouple with 0.1uF cap
      # voltage_out=(3.0, 3.6)*Volt,  # Table 6
      # current_limits=(0, 100)*mAmp,  # Table 6 note
    ))

    self.vphy = self.Port(VoltageSink(  # connect to 3v3 through 600R 0.5A ferrite
      # voltage_limits=(2.9, 5.8)*Volt,  # Table 6 max VBUS threshold Table 2 maximum
      # no current draw, is a sense input pin
    ))
    self.vpll = self.Port(VoltageSink(  # connect to 3v3 through 600R 0.5A ferrite
      # voltage_limits=(2.9, 5.8)*Volt,  # Table 6 max VBUS threshold Table 2 maximum
      # no current draw, is a sense input pin
    ))
    self.vccio = self.Port(VoltageSink(
      # voltage_limits=(2.9, 5.8)*Volt,  # Table 6 max VBUS threshold Table 2 maximum
      # no current draw, is a sense input pin
    ))

    self.osc = self.Port(CrystalDriver(frequency_limits=12*MHertz(tol=30e-6),
                                       voltage_out=self.vccd.link().voltage))  # assumed
    self.ref = self.Port(Passive())  # connect 12k 1% resistor to GND
    self.usb = self.Port(UsbDevicePort())

    dio_model = DigitalBidir.from_supply(
      # self.gnd, self.vdd,
      # current_limits=(-100, 100)*mAmp,  # Table 2, assumed sunk is symmetric since no source rating is given
      # voltage_limit_abs=(-0.3, 5.8)*Volt,
      # input_threshold_abs=(0.8, 2.0)*Volt,  # Table 4
    )
    din_model = DigitalSink.from_bidir(dio_model)
    dout_model = DigitalSource.from_bidir(dio_model)

    self.nreset = self.Port(din_model, optional=True)

    # TODO these should be aliased to the supported serial buses
    self.adbus0 = self.Port(dout_model, optional=True)
    self.adbus1 = self.Port(din_model, optional=True)
    self.adbus2 = self.Port(dout_model, optional=True)
    self.adbus3 = self.Port(din_model, optional=True)
    self.adbus4 = self.Port(dout_model, optional=True)
    self.adbus5 = self.Port(din_model, optional=True)
    self.adbus6 = self.Port(din_model, optional=True)
    self.adbus7 = self.Port(din_model, optional=True)

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
      'U', #'Package_DFN_QFN:QFN-28-1EP_5x5mm_P0.5mm_EP3.35x3.35mm',
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


class Ft232hl(PinMappable):
  """USB multiprotocol converter"""
  def __init__(self) -> None:
    super().__init__()
    self.ic = self.Block(Ft232hl_Device())
    # TODO connect to 3.3v from ferrite
    self.pwr = self.Export(self.ic.vregin, [Power])
    self.gnd = self.Export(self.ic.gnd, [Common])

    self.usb = self.Export(self.ic.usb)

    self.adbus0 = self.Export(self.ic.adbus0, optional=True)
    self.adbus1 = self.Export(self.ic.adbus1, optional=True)
    self.adbus2 = self.Export(self.ic.adbus2, optional=True)
    self.adbus3 = self.Export(self.ic.adbus3, optional=True)
    self.adbus4 = self.Export(self.ic.adbus4, optional=True)
    self.adbus5 = self.Export(self.ic.adbus5, optional=True)
    self.adbus6 = self.Export(self.ic.adbus6, optional=True)
    self.adbus7 = self.Export(self.ic.adbus7, optional=True)

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

  def contents(self) -> None:
    super().contents()

    # connections from Figure 6.1, bus powered configuration
    cap_model = DecouplingCapacitor(0.1*uFarad(tol=0.2))
    self.vregin_cap0 = self.Block(DecouplingCapacitor(4.7*uFarad(tol=0.2))).connected(self.gnd, self.ic.vregin)
    self.vregin_cap1 = self.Block(cap_model).connected(self.gnd, self.ic.vregin)

    # TODO connect to 3.3v from ferrite
    self.vphy_cap = self.Block(cap_model).connected(self.gnd, self.ic.vphy)

    # TODO connect to 3.3v from ferrite
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

    self.connect(self.ic.vccio.as_digital_source(), self.ic.nreset)

    self.crystal = self.Block(OscillatorCrystal(frequency=12*MHertz(tol=30e-6)))
    self.connect(self.crystal.gnd, self.gnd)
    self.connect(self.crystal.crystal, self.ic.osc)
