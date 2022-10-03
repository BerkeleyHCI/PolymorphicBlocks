from typing import *
from electronics_abstract_parts import *


class E2154fs091_Device(DiscreteChip, FootprintBlock):
  def __init__(self) -> None:
    super().__init__()

    self.pwr = self.Port(VoltageSink(
      voltage_limits=(2.4, 3.6)*Volt, current_draw=(0, 10)*mAmp
    ), [Power])
    self.gnd = self.Port(Ground(), [Common])

    dio_model = DigitalBidir(
      voltage_limits=(-0, self.pwr.link().voltage.upper()),  # TODO needs some tolerance
      current_draw=(0, 0),
      voltage_out=(0, self.pwr.link().voltage.lower()),
      current_limits=(-400, 400) * uAmp,
      input_thresholds=(0.3 * self.pwr.link().voltage.upper(),
                        0.7 * self.pwr.link().voltage.upper()),
      output_thresholds=(0.4, self.pwr.link().voltage.upper() - 0.4),
    )

    self.busy = self.Port(DigitalSource.from_bidir(dio_model))
    self.reset = self.Port(DigitalSink.from_bidir(dio_model))
    self.dc = self.Port(DigitalSink.from_bidir(dio_model))
    self.cs = self.Port(DigitalSink.from_bidir(dio_model))
    self.spi = self.Port(SpiSlave(model=dio_model))

    # TODO model all these parts, then fix all the Passive connections
    self.gdr = self.Port(Passive())
    self.rese = self.Port(Passive())
    self.vslr = self.Port(Passive())
    self.vdhr = self.Port(Passive())
    self.vddd = self.Port(Passive())
    self.vdh = self.Port(Passive())
    self.vgh = self.Port(Passive())
    self.vdl = self.Port(Passive())
    self.vgl = self.Port(Passive())
    self.vcom = self.Port(Passive())

  def contents(self) -> None:
    super().contents()

    pinning: Dict[str, CircuitPort] = {
      # '1': ,  # NC
      '2': self.gdr,
      '3': self.rese,
      '4': self.vslr,  # NC / VSLR - for compatibility w/ Waveshare units
      '5': self.vdhr,  # NC / VSL - for compatibility w/ Waveshare units
      # '6': ,  # TSCL
      # '7': ,  # TSDA
      '8': self.gnd,  # BS, to set panel interface
      '9': self.busy,
      '10': self.reset,  # active-low reset
      '11': self.dc,  # data/control
      '12': self.cs,
      '13': self.spi.sck,
      '14': self.spi.mosi,
      '15': self.pwr,  # VddIO
      '16': self.pwr,  # Vdd
      '17': self.gnd,
      '18': self.vddd,
      # '19': ,  # VPP, for OTP programming
      '20': self.vdh,
      '21': self.vgh,
      '22': self.vdl,
      '23': self.vgl,
      '24': self.vcom,
    }

    self.footprint(
      'U', 'Connector_FFC-FPC:Hirose_FH12-24S-0.5SH_1x24-1MP_P0.50mm_Horizontal',  # TODO EPD outline
      {str(25-int(pin)): port for pin, port in pinning.items()},  # reversed since the FPC contacts face down
      part='E2154FS091, FH12-24S-0.5SH(55)',  # TODO multiple parts
      datasheet='https://www.pervasivedisplays.com/wp-content/uploads/2019/06/1P200-00_01_E2154CS091_24PINFPC_20180807-3.pdf',
    )
    # also, for the correct PN: 'https://download.siliconexpert.com/pdfs/2017/11/7/8/22/5/959/pervas_/manual/1p165-00_01_e2154fs091_24pinfpc_20171026.pdf'
    # trying for compatibility with https://www.waveshare.com/wiki/2.7inch_e-Paper_HAT_(B) / https://www.waveshare.com/w/upload/d/d8/2.7inch-e-paper-b-specification.pdf
    # other connectors specified by datasheet: STARCONN 6700S24 "or Compatible"


class E2154fs091(EInk):
  """1.54" 152x152px red/black/white e-ink display with 24-pin FPC connector, 0.5mm pitch"""
  def __init__(self) -> None:
    super().__init__()

    self.ic = self.Block(E2154fs091_Device())
    self.pwr = self.Export(self.ic.pwr, [Power])
    self.gnd = self.Export(self.ic.gnd, [Common])

    self.busy = self.Export(self.ic.busy)
    self.reset = self.Export(self.ic.reset)
    self.dc = self.Export(self.ic.dc)
    self.cs = self.Export(self.ic.cs)
    self.spi = self.Export(self.ic.spi)

  def contents(self) -> None:
    super().contents()

    self.boost_sw = self.Block(Fet.NFet(  # TODO should use switching NFet, but we don't know anything about frequency
      drain_voltage=(0, 30)*Volt,
      drain_current=(0, 0.8)*Amp,  # assumed, from inductor rating
      gate_voltage=(3, 16)*Volt,  # assumed, from capacitor ratings  # TODO use pwr voltage instead of hardcoding
      rds_on=(0, 85)*mOhm, gate_charge=(0, float('inf')),
      power=(0, 0.2)*Watt  # about 4x resistive loss @ 0.8A, 85mOhm; we don't know the switch frequency or drive current
    ))
    self.boost_ind = self.Block(Inductor(
      inductance=10*uHenry(tol=0.2), current=(0, 0.8)*Amp, frequency=100*kHertz(tol=0)
    ))
    self.boost_res = self.Block(Resistor(
      resistance=0.47*Ohm(tol=0.01), power=0*Watt(tol=0)  # TODO actual power numbers based on current draw
    ))
    self.boot_cap = self.Block(Capacitor(
      capacitance=(4.7, float('inf'))*uFarad, voltage=(0, 16)*Volt  # lower-bounded so it can be derated
    ))
    self.connect(self.pwr, self.boost_ind.a.adapt_to(VoltageSink()))
    self.connect(self.boost_ind.b, self.boost_sw.drain, self.boot_cap.pos)
    self.connect(self.boost_sw.gate, self.ic.gdr)
    self.connect(self.boost_sw.source, self.boost_res.a, self.ic.rese)
    self.connect(self.boost_res.b.adapt_to(VoltageSink()), self.gnd)

    self.vdd_cap0 = self.Block(DecouplingCapacitor(capacitance=0.11*uFarad(tol=0.2))).connected(self.gnd, self.pwr)
    self.vdd_cap1 = self.Block(DecouplingCapacitor(capacitance=1*uFarad(tol=0.2))).connected(self.gnd, self.pwr)

    decoupling_cap_model = Capacitor(
      capacitance=1*uFarad(tol=0.2), voltage=(0, 16)*Volt
    )

    # TODO make these actually DecouplingCaps?
    self.vslr_cap = self.Block(decoupling_cap_model)
    self.connect(self.ic.vslr, self.vslr_cap.pos)
    self.vdhr_cap = self.Block(decoupling_cap_model)
    self.connect(self.ic.vdhr, self.vdhr_cap.pos)
    self.vddd_cap = self.Block(decoupling_cap_model)
    self.connect(self.ic.vddd, self.vddd_cap.pos)
    self.vdh_cap = self.Block(decoupling_cap_model)
    self.connect(self.ic.vdh, self.vdh_cap.pos)
    self.vgh_cap = self.Block(decoupling_cap_model)
    self.connect(self.ic.vgh, self.vgh_cap.pos)
    self.vdl_cap = self.Block(decoupling_cap_model)
    self.connect(self.ic.vdl, self.vdl_cap.pos)
    self.vgl_cap = self.Block(decoupling_cap_model)
    self.connect(self.ic.vgl, self.vgl_cap.pos)
    self.vcom_cap = self.Block(decoupling_cap_model)
    self.connect(self.ic.vcom, self.vcom_cap.pos)

    self.connect(self.gnd,
                 self.vslr_cap.neg.adapt_to(Ground()),
                 self.vdhr_cap.neg.adapt_to(Ground()),
                 self.vddd_cap.neg.adapt_to(Ground()),
                 self.vdh_cap.neg.adapt_to(Ground()),
                 self.vgh_cap.neg.adapt_to(Ground()),
                 self.vdl_cap.neg.adapt_to(Ground()),
                 self.vgl_cap.neg.adapt_to(Ground()),
                 self.vcom_cap.neg.adapt_to(Ground()))

    diode_model = Diode(
      reverse_voltage=(0, 25)*Volt, current=(0, 2)*Amp, voltage_drop=(0, 0.5)*Volt,
      reverse_recovery_time=(0, 500e-9)  # guess from Digikey's classification for "fast recovery"
    )

    self.boost_dio = self.Block(diode_model)
    self.connect(self.boost_ind.b, self.boost_dio.anode)
    self.connect(self.boost_dio.cathode, self.vgh_cap.pos)
    self.vgl_dio = self.Block(diode_model)
    self.connect(self.vgl_cap.pos, self.vgl_dio.anode)
    self.connect(self.vgl_dio.cathode, self.boot_cap.neg)
    self.boot_dio = self.Block(diode_model)
    self.connect(self.boot_cap.neg, self.boot_dio.anode)
    self.connect(self.boot_dio.cathode.adapt_to(Ground()), self.gnd)
