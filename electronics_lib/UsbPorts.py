from electronics_abstract_parts import *


@abstract_block
class UsbConnector(Connector):
  """USB connector of any generation / type."""
  USB2_VOLTAGE_RANGE = (4.75, 5.25)*Volt
  USB2_CURRENT_LIMITS = (0, 0.5)*Amp


class UsbAReceptacle(UsbConnector, FootprintBlock):
  def __init__(self) -> None:
    super().__init__()
    self.pwr = self.Port(VoltageSink(
      voltage_limits=self.USB2_VOLTAGE_RANGE,
      current_draw=self.USB2_CURRENT_LIMITS
    ), [Power])
    self.gnd = self.Port(Ground(), [Common])

    self.usb = self.Port(UsbDevicePort(), optional=True)
    self.shield = self.Port(Passive(), optional=True)

  def contents(self):
    super().contents()
    self.footprint(
      'J', 'Connector_USB:USB_A_Molex_105057_Vertical',
      {
        '1': self.pwr,
        '4': self.gnd,

        '2': self.usb.dm,
        '3': self.usb.dp,

        '5': self.shield,
      },
      mfr='Molex', part='105057',
      datasheet='https://www.molex.com/pdm_docs/sd/1050570001_sd.pdf'
    )


class UsbCReceptacle(UsbConnector, FootprintBlock):
  @init_in_parent
  def __init__(self, voltage_out: RangeExpr = UsbConnector.USB2_VOLTAGE_RANGE,  # allow custom PD voltage and current
               current_limits: RangeExpr = UsbConnector.USB2_CURRENT_LIMITS) -> None:
    super().__init__()
    self.pwr = self.Port(VoltageSource(voltage_out=voltage_out, current_limits=current_limits), optional=True)
    self.gnd = self.Port(GroundSource())

    self.usb = self.Port(UsbHostPort(), optional=True)
    self.shield = self.Port(Passive(), optional=True)

    # CC is pulled-up on source (DFP) side
    self.cc1 = self.Port(DigitalBidir(pullup_capable=True), optional=True)  # TODO re-type with USB CC specific type
    self.cc2 = self.Port(DigitalBidir(pullup_capable=True), optional=True)

  def contents(self):
    super().contents()
    self.footprint(
      'J', 'calisco:USB_C_Receptacle_BSC_A40-00119',
      {
        'A1B12': self.gnd,
        'A4B9': self.pwr,

        'A5': self.cc1,
        'A6': self.usb.dp,
        'A7': self.usb.dm,
        # 'A8': sbu1,

        # 'B8': sbu2
        'B7': self.usb.dm,
        'B6': self.usb.dp,
        'B5': self.cc2,

        'B4A9': self.pwr,
        'B1A12': self.gnd,

        'S': self.shield,
      },
      mfr='Sparkfun', part='COM-15111',
      datasheet='https://cdn.sparkfun.com/assets/8/6/b/4/5/A40-00119-A52-12.pdf'
    )


@abstract_block
class UsbDeviceConnector(UsbConnector):
  """Abstract base class for a USB device port connector"""
  def __init__(self) -> None:
    super().__init__()
    self.pwr = self.Port(VoltageSource(
      voltage_out=self.USB2_VOLTAGE_RANGE,
      current_limits=self.USB2_CURRENT_LIMITS
    ), optional=True)
    self.gnd = self.Port(GroundSource())

    self.usb = self.Port(UsbHostPort(), optional=True)


class UsbDeviceCReceptacle(UsbDeviceConnector):
  """Implementation of a USB device using a Type-C receptable as a upstream-facing port."""
  def __init__(self) -> None:
    super().__init__()

  def contents(self) -> None:
    self.port = self.Block(UsbCReceptacle())
    self.connect(self.pwr, self.port.pwr)
    self.connect(self.gnd, self.port.gnd, self.port.shield.as_ground())
    self.connect(self.usb, self.port.usb)

    with self.implicit_connect(
        ImplicitConnect(self.port.gnd, [Common]),
    ) as imp:
      pdr_model = PulldownResistor(resistance=5.1*kOhm(tol=0.01))
      (self.cc1_pull, ), _ = self.chain(imp.Block(pdr_model), self.port.cc1)
      (self.cc2_pull, ), _ = self.chain(imp.Block(pdr_model), self.port.cc2)


class UsbEsdDiode(TvsDiode, FootprintBlock):  # TODO maybe this should be a superclass?
  def __init__(self) -> None:
    super().__init__()
    self.gnd = self.Port(Ground(), [Common])
    self.usb = self.Port(UsbPassivePort(), [InOut])

  def contents(self):
    # Note, also compatible: https://www.diodes.com/assets/Datasheets/DT1452-02SO.pdf
    super().contents()
    self.footprint(
      'U', 'Package_TO_SOT_SMD:SOT-23',
      {
        '1': self.usb.dm,
        '2': self.usb.dp,
        '3': self.gnd,
      },
      mfr='Texas Instruments', part='TPD2E009',
      datasheet='https://www.ti.com/lit/ds/symlink/tpd2e009.pdf'
    )
