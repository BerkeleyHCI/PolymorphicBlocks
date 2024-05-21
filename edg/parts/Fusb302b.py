from ..abstract_parts import *
from .JlcPart import JlcPart


class Fusb302b_Device(InternalSubcircuit, FootprintBlock, JlcPart):
  def __init__(self) -> None:
    super().__init__()
    self.vbus = self.Port(VoltageSink(voltage_limits=(4, 21)))
    self.vdd = self.Port(VoltageSink(
      voltage_limits=(2.7, 5.5)*Volt,
      current_draw=(0.37, 40)*uAmp))  # Table 11, between disabled typ and standby typ
    self.vconn = self.Port(VoltageSink(
      voltage_limits=(2.7, 5.5)*Volt, current_draw=(0, 560)*mAmp), optional=True)
    self.gnd = self.Port(Ground())

    self.cc = self.Port(UsbCcPort())  # TODO pass in port models?
    i2c_model = DigitalBidir(  # interestingly, IO maximum voltages are not specified
      current_draw=(0, 0),  # leakage current (Table 13) not modeled
      voltage_out=(0, 0.35)*Volt,  # low-level output voltage
      current_limits=(-20, 0)*mAmp,  # low-level output current limits
      input_thresholds=(0.51, 1.32)*Volt,
      output_thresholds=(0.35, float('inf')) * Volt,
    )
    self.i2c = self.Port(I2cTarget(i2c_model, [0x22]))
    self.int_n = self.Port(DigitalSingleSource.low_from_supply(self.gnd), optional=True)

  def contents(self) -> None:
    self.footprint(
      'U', 'Package_DFN_QFN:WQFN-14-1EP_2.5x2.5mm_P0.5mm_EP1.45x1.45mm',
      {
        '1': self.cc.cc2,
        '2': self.vbus,
        '3': self.vdd,
        '4': self.vdd,
        '5': self.int_n,
        '6': self.i2c.scl,
        '7': self.i2c.sda,
        '8': self.gnd,
        '9': self.gnd,
        '10': self.cc.cc1,
        '11': self.cc.cc1,
        '12': self.vconn,
        '13': self.vconn,
        '14': self.cc.cc2,
        '15': self.gnd
      },
      mfr='ON Semiconductor', part='FUSB302B11MPX',  # actual several compatible variants
      datasheet='https://www.onsemi.com/pdf/datasheet/fusb302b-d.pdf'
    )
    self.assign(self.lcsc_part, 'C132291')
    self.assign(self.actual_basic_part, False)


class Fusb302b(Interface, Block):
  def __init__(self) -> None:
    super().__init__()
    self.ic = self.Block(Fusb302b_Device())
    self.pwr = self.Export(self.ic.vdd, [Power])
    self.gnd = self.Export(self.ic.gnd, [Common])
    self.vbus = self.Export(self.ic.vbus)
    # TODO conditionally generate Vconn capacitor to support powering cables

    self.cc = self.Export(self.ic.cc)
    self.i2c = self.Export(self.ic.i2c)
    self.int = self.Export(self.ic.int_n)

  def contents(self) -> None:
    super().contents()

    # From Figure 18, reference schematic diagram
    # minus the I2C pullups and interrupt pullups, which should be checked to be elsewhere
    # and the bulk capacitor, which we hope will be elsewhere
    self.vdd_cap = ElementDict[DecouplingCapacitor]()
    self.vdd_cap[0] = self.Block(DecouplingCapacitor(0.1 * uFarad(tol=0.2))).connected(self.gnd, self.pwr)
    self.vdd_cap[1] = self.Block(DecouplingCapacitor(10 * uFarad(tol=0.2))).connected(self.gnd, self.pwr)

    # Crecv is specified in the reference schematic, but doesn't show up on open-source example designs
