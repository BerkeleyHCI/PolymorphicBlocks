from electronics_abstract_parts import *


class Xbee_S3b_Device(DiscreteChip, CircuitBlock):
  def __init__(self):
    super().__init__()

    # only required pins are Vcc, GND, DOUT, DIN
    # also need RTS, DTR for serial firmware updates
    # DNC pins that are not in use
    self.pwr = self.Port(ElectricalSink(
      voltage_limits=(2.1, 3.6) * Volt,
      current_draw=(0.0025, 290) * mAmp  # 2.5uA sleep, 29mA receive, 290 mA max transmit
    ), [Power])
    self.gnd = self.Port(Ground(), [Common])

    digital_model = DigitalBidir.from_supply(
      self.gnd, self.pwr,
      voltage_limit_tolerance=(-0.3, 0.3)*Volt,  # TODO speculative deafult
      current_draw=(0, 0),  # TODO actually an unspecified default
      current_limits=(-2, 2) * mAmp,
      input_threshold_factor=(0.3, 0.7),
      output_threshold_factor=(0.05, 0.95)
    )

    self.data = self.Port(UartPort(digital_model), [Input])

    self.rssi = self.Port(DigitalSource(digital_model), optional=True)
    self.associate = self.Port(DigitalSource(digital_model), optional=True)

  def contents(self):
    super().contents()
    self.footprint(
      'U', 'Sparkfun_RF:XBEE',
      {
        '1': self.pwr,
        '2': self.data.tx,
        '3': self.data.rx,
        # '4': ,  # GPIO / SPI SO
        # '5': ,  # reset w/ internal PUR
        '6': self.rssi,  # GPIO / RSSI
        # '7': ,  # GPIO / PWM
        # '8': ,  # reserved
        # '9': ,  # GPIO / sleep control
        '10': self.gnd,
        # '11': ,  # GPIO / CS in
        # '12': ,  # GPIO / CTS
        # '13': ,  # GPIO / module status indicator
        '14': self.gnd,  # Vref, connected to GND if not using analog sampling
        '15': self.associate,  # GPIO / associate indicator
        # '16': ,  # GPIO / RTS
        # '17': ,  # GPIO / Ain / CS
        # '18': ,  # GPIO / Ain / SPI SCK
        # '19': ,  # GPIO / Ain / SPI attention
        # '20': ,  # GIO / Ain
      },
      mfr='Digi International', part='XBP9B-*',
      datasheet='https://www.digi.com/resources/documentation/digidocs/pdfs/90002173.pdf'
    )


class Xbee_S3b(IntegratedCircuit, CircuitBlock):
  """XBee-PRO 900HP, product numbers XBP9B-*"""
  def __init__(self) -> None:
    super().__init__()

    self.ic = self.Block(Xbee_S3b_Device())
    self.pwr = self.Export(self.ic.pwr, [Power])
    self.gnd = self.Export(self.ic.gnd, [Common])
    self.data = self.Export(self.ic.data)
    self.rssi = self.Export(self.ic.rssi, optional=True)
    self.associate = self.Export(self.ic.associate, optional=True)

  def contents(self):
    super().contents()

    with self.implicit_connect(
        ImplicitConnect(self.pwr, [Power]),
        ImplicitConnect(self.gnd, [Common])
    ) as imp:
      self.vdd_cap_0 = imp.Block(DecouplingCapacitor(
        capacitance=1.0*uFarad(tol=0.2),
      ))
      self.vdd_cap_1 = imp.Block(DecouplingCapacitor(
        capacitance=47*pFarad(tol=0.2),
      ))


class BlueSmirf(IntegratedCircuit, CircuitBlock):
  """SlueSMiRF Gold/Silver"""
  def __init__(self) -> None:
    super().__init__()

    self.pwr = self.Port(ElectricalSink(
      voltage_limits=(3, 6) * Volt,  # TODO added a -10% tolerance on the low side so things still work - technically out of spec
      current_draw=(0, 0),  # TODO actually an unspecified default
    ), [Power])
    self.gnd = self.Port(Ground(), [Common])

    digital_model = DigitalBidir.from_supply(
      pos=self.pwr, neg=self.gnd,
      voltage_limit_tolerance=(-0.3, 0.3)*Volt,  # TODO actually an unspecified default
      # TODO other parameters given the logic conversion circuit
      current_draw=(0, 0),  # TODO actually an unspecified default
      input_threshold_factor=(0.5, 0.5),  # TODO completely wild relaxed unrealistic guess
      output_threshold_factor=(0, 1)  # TODO completely wild relaxed unrealistic guess
    )

    self.data = self.Port(UartPort(digital_model), [Input])
    self.cts = self.Port(DigitalSink(digital_model), optional=True)
    self.rts = self.Port(DigitalSource(digital_model), optional=True)

  def contents(self):
    super().contents()
    self.footprint(
      'U', 'Connector_PinHeader_2.54mm:PinHeader_1x06_P2.54mm_Vertical',
      {
        '1': self.cts,
        '2': self.pwr,
        '3': self.gnd,
        '4': self.data.tx,
        '5': self.data.rx,
        '6': self.rts,
      },
      mfr='Sparkfun', part='BlueSMiRF',
      datasheet='https://www.sparkfun.com/products/12577'
    )
