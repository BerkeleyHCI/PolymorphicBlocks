from ..electronics_abstract_parts import *
from .JlcPart import JlcPart


class Cp2102_Device(InternalSubcircuit, FootprintBlock, JlcPart):
  def __init__(self) -> None:
    super().__init__()
    self.gnd = self.Port(Ground())
    self.regin = self.Port(VoltageSink(
      voltage_limits=(4.0, 5.25)*Volt,  # Table 6
      current_draw=(0.080, 26)*mAmp  # TAble 3, suspended typ to normal max
    ))
    self.vdd = self.Port(VoltageSource(  # as input, limits are 3.0-3.6v
      voltage_out=(3.0, 3.6)*Volt,  # Table 6
      current_limits=(0, 100)*mAmp,  # Table 6 note
    ))
    self.vbus = self.Port(VoltageSink(
      voltage_limits=(2.9, 5.8)*Volt,  # Table 6 max VBUS threshold Table 2 maximum
      # no current draw, is a sense input pin
    ))

    self.usb = self.Port(UsbDevicePort())

    dio_model = DigitalBidir.from_supply(
      self.gnd, self.vdd,
      current_limits=(-100, 100)*mAmp,  # Table 2, assumed sunk is symmetric since no source rating is given
      voltage_limit_abs=(-0.3, 5.8)*Volt,
      input_threshold_abs=(0.8, 2.0)*Volt,  # Table 4
    )
    din_model = DigitalSink.from_bidir(dio_model)
    dout_model = DigitalSource.from_bidir(dio_model)

    self.rst = self.Port(din_model, optional=True)
    self.suspend = self.Port(dout_model, optional=True)
    self.nsuspend = self.Port(dout_model, optional=True)

    self.uart = self.Port(UartPort(dio_model), optional=True)  # baud up to 921600bps
    self.ri = self.Port(din_model, optional=True)
    self.dcd = self.Port(din_model, optional=True)
    self.dtr = self.Port(dout_model, optional=True)
    self.dsr = self.Port(din_model, optional=True)
    self.rts = self.Port(dout_model, optional=True)
    self.cts = self.Port(din_model, optional=True)

    self.require(self.uart.is_connected() | self.ri.is_connected() | self.dcd.is_connected() | self.dtr.is_connected()
                 | self.dsr.is_connected() | self.rts.is_connected() | self.cts.is_connected())

    self.footprint(
      'U', 'Package_DFN_QFN:QFN-28-1EP_5x5mm_P0.5mm_EP3.35x3.35mm',
      {
        '1': self.dcd,
        '2': self.ri,
        '3': self.gnd,
        '4': self.usb.dp,
        '5': self.usb.dm,
        '6': self.vdd,
        '7': self.regin,
        '8': self.vbus,
        '9': self.rst,
        # 10: NC - per Table 9 can be unconnected or tied to Vdd
        '11': self.nsuspend,
        '12': self.suspend,
        # 13-22: NC (18 on CP2109 is VPP)
        '23': self.cts,
        '24': self.rts,
        '25': self.uart.rx,
        '26': self.uart.tx,
        '27': self.dsr,
        '28': self.dtr,
        '29': self.gnd,
      },
      mfr='Silicon Labs', part='CP2102',
      datasheet='https://www.silabs.com/documents/public/data-sheets/CP2102-9.pdf'
    )
    self.assign(self.lcsc_part, "C6568")  # CP2102-GMR
    self.assign(self.actual_basic_part, True)


class Cp2102(Interface, PinMappable):
  """USB-UART converter"""
  def __init__(self) -> None:
    super().__init__()
    self.ic = self.Block(Cp2102_Device())
    self.pwr = self.Export(self.ic.regin, [Power])
    self.gnd = self.Export(self.ic.gnd, [Common])

    self.usb = self.Export(self.ic.usb)
    self.suspend = self.Export(self.ic.suspend, optional=True)
    self.nsuspend = self.Export(self.ic.nsuspend, optional=True)

    self.uart = self.Export(self.ic.uart, optional=True)
    self.ri = self.Export(self.ic.ri, optional=True)
    self.dcd = self.Export(self.ic.dcd, optional=True)
    self.dtr = self.Export(self.ic.dtr, optional=True)
    self.dsr = self.Export(self.ic.dsr, optional=True)
    self.rts = self.Export(self.ic.rts, optional=True)
    self.cts = self.Export(self.ic.cts, optional=True)

  def contents(self) -> None:
    super().contents()
    self.connect(self.ic.regin, self.ic.vbus)
    self.connect(self.ic.vdd.as_digital_source(), self.ic.rst)

    self.regin_cap0 = self.Block(DecouplingCapacitor(1.0*uFarad(tol=0.2))).connected(self.gnd, self.ic.regin)
    self.regin_cap1 = self.Block(DecouplingCapacitor(0.1*uFarad(tol=0.2))).connected(self.gnd, self.ic.regin)
    self.vdd_cap = self.Block(DecouplingCapacitor(1.0*uFarad(tol=0.2))).connected(self.gnd, self.ic.vdd)
    # Vdd currently isn't externally exposed, but if externally used a 4.7uF capacitor is needed (Figure 5 Option 2)
