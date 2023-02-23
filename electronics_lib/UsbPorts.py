from electronics_abstract_parts import *
from electronics_lib.JlcPart import JlcPart


class UsbAReceptacle(UsbHostConnector, FootprintBlock):
  def __init__(self) -> None:
    super().__init__()
    self.pwr.init_from(VoltageSink(
      voltage_limits=self.USB2_VOLTAGE_RANGE,
      current_draw=self.USB2_CURRENT_LIMITS
    ))
    self.gnd.init_from(Ground())

    self.usb.init_from(UsbDevicePort())

  def contents(self):
    super().contents()
    self.footprint(
      'J', 'Connector_USB:USB_A_Molex_105057_Vertical',
      {
        '1': self.pwr,
        '4': self.gnd,

        '2': self.usb.dm,
        '3': self.usb.dp,

        '5': self.gnd,  # shield
      },
      mfr='Molex', part='105057',
      datasheet='https://www.molex.com/pdm_docs/sd/1050570001_sd.pdf'
    )


class UsbCReceptacle_Device(InternalSubcircuit, FootprintBlock, JlcPart):
  """Raw USB Type-C Receptacle
  Pullup capable indicates whether this port (or more accurately, the device on the other side) can pull
  up the signal. In UFP (upstream-facing, device) mode the power source should pull up CC."""
  @init_in_parent
  def __init__(self, voltage_out: RangeLike = UsbConnector.USB2_VOLTAGE_RANGE,  # allow custom PD voltage and current
               current_limits: RangeLike = UsbConnector.USB2_CURRENT_LIMITS,
               cc_pullup_capable: BoolLike = Default(False)) -> None:
    super().__init__()
    self.pwr = self.Port(VoltageSource(voltage_out=voltage_out, current_limits=current_limits), optional=True)
    self.gnd = self.Port(GroundSource())

    self.usb = self.Port(UsbHostPort(), optional=True)
    self.shield = self.Port(Passive(), optional=True)

    self.cc = self.Port(UsbCcPort(pullup_capable=cc_pullup_capable), optional=True)

  def contents(self):
    super().contents()

    self.assign(self.lcsc_part, 'C165948')  # note, many other pin-compatible parts also available
    self.assign(self.actual_basic_part, False)
    self.footprint(
      'J', 'Connector_USB:USB_C_Receptacle_XKB_U262-16XN-4BVC11',
      {
        'A1': self.gnd,
        'B12': self.gnd,
        'A4': self.pwr,
        'B9': self.pwr,

        'A5': self.cc.cc1,
        'A6': self.usb.dp,
        'A7': self.usb.dm,
        # 'A8': sbu1,

        # 'B8': sbu2
        'B7': self.usb.dm,
        'B6': self.usb.dp,
        'B5': self.cc.cc2,

        'B4': self.pwr,
        'A9': self.pwr,
        'B1': self.gnd,
        'A12': self.gnd,

        'S1': self.shield,
      },
      mfr='Sparkfun', part='COM-15111',
      datasheet='https://cdn.sparkfun.com/assets/8/6/b/4/5/A40-00119-A52-12.pdf'
    )


class UsbCReceptacle(UsbDeviceConnector, GeneratorBlock):
  """USB Type-C Receptacle that automatically generates the CC resistors if CC is not connected."""
  @init_in_parent
  def __init__(self, voltage_out: RangeLike = UsbConnector.USB2_VOLTAGE_RANGE,  # allow custom PD voltage and current
               current_limits: RangeLike = UsbConnector.USB2_CURRENT_LIMITS) -> None:
    super().__init__()

    self.conn = self.Block(UsbCReceptacle_Device(voltage_out=voltage_out, current_limits=current_limits))
    self.connect(self.pwr, self.conn.pwr)
    self.connect(self.gnd, self.conn.gnd)
    self.connect(self.usb, self.conn.usb)
    self.cc = self.Port(UsbCcPort.empty(), optional=True)  # external connectivity defines the circuit

    self.generator(self.generate, self.pwr.is_connected(), self.cc.is_connected())

  def generate(self, pwr_connected: bool, cc_connected: bool) -> None:
    if cc_connected:  # if CC externally connected, connect directly to USB port
      self.connect(self.cc, self.conn.cc)
      self.require(self.cc.is_connected().implies(self.pwr.is_connected()),
                   "USB power not used when CC connected")
    elif pwr_connected:  # otherwise generate the pulldown resistors for USB2 mode
      (self.cc_pull, ), _ = self.chain(self.conn.cc, self.Block(UsbCcPulldownResistor()))
      self.connect(self.cc_pull.gnd, self.gnd)
      self.require(self.pwr.voltage_out == UsbConnector.USB2_VOLTAGE_RANGE,
                   "when CC not connected, port restricted to USB 2.0 voltage")
      self.require(self.pwr.current_limits == UsbConnector.USB2_CURRENT_LIMITS,
                   "when CC not connected, port restricted to USB 2.0 current")

    # TODO there does not seem to be full agreement on what to do with the shield pin, we arbitrarily ground it
    self.connect(self.gnd, self.conn.shield.adapt_to(Ground()))


class UsbMicroBReceptacle(UsbDeviceConnector, FootprintBlock):
  def __init__(self) -> None:
    super().__init__()

  def contents(self):
    super().contents()
    self.pwr.init_from(VoltageSource(
      voltage_out=self.USB2_VOLTAGE_RANGE,
      current_limits=self.USB2_CURRENT_LIMITS
    ))
    self.gnd.init_from(GroundSource())
    self.usb.init_from(UsbHostPort())

    self.footprint(
      'J', 'Connector_USB:USB_Micro-B_Molex-105017-0001',
      {
        '1': self.pwr,
        '5': self.gnd,

        '2': self.usb.dm,
        '3': self.usb.dp,

        # '4': TODO: ID pin

        '6': self.gnd,  # shield
      },
      mfr='Molex', part='105017-0001',
      datasheet='https://www.molex.com/pdm_docs/sd/1050170001_sd.pdf'
    )


class UsbCcPulldownResistor(InternalSubcircuit, Block):
  """Pull-down resistors on the CC lines for a device to request power from a type-C UFP port,
  without needing a USB PD IC."""
  def __init__(self) -> None:
    super().__init__()
    self.cc = self.Port(UsbCcPort.empty(), [Input])
    self.gnd = self.Port(Ground.empty(), [Common])

  def contents(self) -> None:
    super().contents()
    pdr_model = PulldownResistor(resistance=5.1*kOhm(tol=0.01))
    self.cc1 = self.Block(pdr_model).connected(self.gnd, self.cc.cc1)
    self.cc2 = self.Block(pdr_model).connected(self.gnd, self.cc.cc2)


class Tpd2e009(UsbEsdDiode, FootprintBlock, JlcPart):
  def contents(self):
    # Note, also compatible: https://www.diodes.com/assets/Datasheets/DT1452-02SO.pdf
    # PESD5V0X1BT,215 (different architecture, but USB listed as application)
    super().contents()
    self.gnd.init_from(Ground())
    self.usb.init_from(UsbPassivePort())
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


class Pesd5v0x1bt(UsbEsdDiode, FootprintBlock, JlcPart):
  """Ultra low capacitance ESD protection diode (0.9pF typ), suitable for USB and GbE"""
  def contents(self):
    super().contents()
    self.gnd.init_from(Ground())
    self.usb.init_from(UsbPassivePort())
    self.assign(self.lcsc_part, 'C456094')
    self.assign(self.actual_basic_part, False)
    self.footprint(
      'U', 'Package_TO_SOT_SMD:SOT-23',
      {
        '1': self.usb.dm,
        '2': self.usb.dp,
        '3': self.gnd,
      },
      mfr='Nexperia', part='PESD5V0X1BT',
      datasheet='https://assets.nexperia.com/documents/data-sheet/PESD5V0X1BT.pdf'
    )


class Pgb102st23(UsbEsdDiode, FootprintBlock, JlcPart):
  """ESD suppressor, suitable for high speed protocols including USB2.0, 0.12pF typ"""
  def contents(self):
    super().contents()
    self.gnd.init_from(Ground())
    self.usb.init_from(UsbPassivePort())
    self.assign(self.lcsc_part, 'C126830')
    self.assign(self.actual_basic_part, False)
    self.footprint(
      'U', 'Package_TO_SOT_SMD:SOT-23',
      {
        '1': self.usb.dm,
        '2': self.usb.dp,
        '3': self.gnd,
      },
      mfr='Littelfuse', part='PGB102ST23',
      datasheet='https://www.littelfuse.com/~/media/electronics/datasheets/pulseguard_esd_suppressors/littelfuse_pulseguard_pgb1_datasheet.pdf.pdf'
    )
