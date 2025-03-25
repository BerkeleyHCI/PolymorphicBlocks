from ..abstract_parts import *
from .JlcPart import JlcPart


class Drv8870_Device(InternalSubcircuit, FootprintBlock, JlcPart):
  def __init__(self) -> None:
    super().__init__()
    self.gnd = self.Port(Ground())
    self.vm = self.Port(VoltageSink.from_gnd(
      self.gnd,
      voltage_limits=(6.5, 45)*Volt, current_draw=RangeExpr())
    )
    self.vref = self.Port(VoltageSink.from_gnd(
      self.gnd,
      voltage_limits=(0.3, 5)*Volt,  # operational from 0-0.3v, but degraded accuracy
      current_draw=(0, 0)*Amp
    ))

    din_model = DigitalSink.from_supply(
      self.gnd, self.vm,
      voltage_limit_abs=(-0.3, 7)*Volt,
      input_threshold_abs=(0.5, 1.5)*Volt,
      pulldown_capable=True  # internal 100kOhm pulldown
    )
    self.in1 = self.Port(din_model)
    self.in2 = self.Port(din_model)

    dout_model = DigitalSource.from_supply(self.gnd, self.vm, current_limits=(-3.6, 3.6)*Amp)  # peak output current
    self.out1 = self.Port(dout_model)
    self.out2 = self.Port(dout_model)

    self.isen = self.Port(VoltageSink(
      current_draw=RangeExpr()
    ))

  def contents(self) -> None:
    self.assign(self.isen.current_draw,
                (0, self.out1.link().current_drawn.abs().upper().max(
                  self.out2.link().current_drawn.abs().upper())))
    self.assign(self.vm.current_draw, (10, 10000) * uAmp +  # from sleep to max operating
                self.isen.current_draw)

    self.footprint(
      'U', 'Package_SO:HSOP-8-1EP_3.9x4.9mm_P1.27mm_EP2.41x3.1mm',
      {
        '1': self.gnd,
        '3': self.in1,
        '2': self.in2,
        '7': self.isen,
        '6': self.out1,
        '8': self.out2,
        '5': self.vm,
        '4': self.vref,
        '9': self.gnd,  # thermal pad
      },
      mfr='Texas Instruments', part='DRV8870DDAR',  # also compatible w/ PW package (no GND pad)
      datasheet='https://www.ti.com/lit/ds/symlink/drv8870.pdf'
    )
    self.assign(self.lcsc_part, 'C86590')
    self.assign(self.actual_basic_part, False)


class Drv8870(BrushedMotorDriver):
  """Brushed DC motor driver, 6.5-45v, PWM control, internally current limited using current sense and trip point"""
  @init_in_parent
  def __init__(self, current_trip: RangeLike = (2, 3)*Amp) -> None:
    super().__init__()
    self.ic = self.Block(Drv8870_Device())
    self.gnd = self.Export(self.ic.gnd, [Common])
    self.pwr = self.Export(self.ic.vm, [Power])
    self.vref = self.Export(self.ic.vref)

    self.in1 = self.Export(self.ic.in1)
    self.in2 = self.Export(self.ic.in2)
    self.out1 = self.Export(self.ic.out1)
    self.out2 = self.Export(self.ic.out2)

    self.current_trip = self.ArgParameter(current_trip)

  def contents(self) -> None:
    super().contents()
    self.vm_cap0 = self.Block(DecouplingCapacitor(0.1*uFarad(tol=0.2))).connected(self.gnd, self.ic.vm)
    # the upper tolerable range of these caps is extended to allow search flexibility when voltage derating
    self.vm_cap1 = self.Block(DecouplingCapacitor((47*0.8, 100)*uFarad)).connected(self.gnd, self.ic.vm)
    self.isen_res = self.Block(SeriesPowerResistor(  # TODO use Range.cancel_multiple for proper tolerance prop
      resistance=self.vref.link().voltage / 10 / self.current_trip
    )).connected(self.gnd.as_voltage_source(), self.ic.isen)
