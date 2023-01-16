from electronics_abstract_parts import *
from .JlcPart import JlcPart


class E93Lc_B_Device(DiscreteChip, GeneratorBlock, JlcPart, FootprintBlock):
  PARTS = [
    # 96LC56B seems to be the most popular version
    (2*1024, '93LC56B', 'https://ww1.microchip.com/downloads/en/DeviceDoc/21794G.pdf',
     'C190271', False),  # BT-I/OT variant
    # rest are out of stock at JLC in OT package
    # TODO check datasheets for the rest for parameter accuracy
    # (1*1024, '93LC46B', 'https://ww1.microchip.com/downloads/en/DeviceDoc/20001749K.pdf',
    #  'C2061604', False),  # BT-E/OT variant
    # (4*1024, '93LC66B', 'https://ww1.microchip.com/downloads/en/DeviceDoc/21795E.pdf',
    #  'C2061454', False),  # BT-I/OT variant
    # (8*1024, '93LC76B', 'https://ww1.microchip.com/downloads/en/DeviceDoc/21796M.pdf',
    #  'C2063754', False),  # BT-E/OT variant
    # (16*1024, '93LC86B', 'https://ww1.microchip.com/downloads/en/DeviceDoc/21797L.pdf',
    #  'C616337', False),  # BT-I/OT variant
  ]

  @init_in_parent
  def __init__(self, size: RangeLike):
    super().__init__()
    self.vcc = self.Port(VoltageSink(
      voltage_limits=(1.5, 5.5)*Volt,  # Table 1-1 VPOR to Vcc max under I test conditions
      current_draw=(0.001, 2)*mAmp  # standby max to write max
    ), [Power])
    self.gnd = self.Port(Ground(), [Common])

    dio_model = DigitalBidir.from_supply(
      self.gnd, self.vcc,
      voltage_limit_tolerance=(-0.6, 1),
      input_threshold_abs=(0.8, 2.0)  # Table 1-1, for Vcc > 2.7
    )
    self.spi = self.Port(SpiSlave(dio_model, (0, 2)*MHertz))  # for Vcc >= 2.5
    self.cs = self.Port(dio_model)

    self.actual_size = self.Parameter(IntExpr())

    self.generator(self.generate, size)

  def generate(self, size: Range):
    suitable_parts = [part for part in self.PARTS if part[0] in size]
    assert suitable_parts, f"no memory in requested size range {size}"
    part_size, part_pn, part_datasheet, part_lcsc, part_lcsc_basic = suitable_parts[0]

    self.assign(self.actual_size, part_size)
    self.footprint(
      'U', 'Package_TO_SOT_SMD:SOT-23-6',
      {
        '1': self.spi.miso,  # DO
        '2': self.gnd,
        '3': self.spi.mosi,  # DI
        '4': self.spi.sck,
        '5': self.cs,
        '6': self.vcc,
      },
      mfr='Microchip Technology', part=part_pn,
      datasheet=part_datasheet
    )
    self.assign(self.lcsc_part, part_lcsc)
    self.assign(self.actual_basic_part, part_lcsc_basic)


class E93Lc_B(SpiMemory):
  """93LCxxB series of SPI EEPROMs. The E prefix is because Python identifiers can't start with numbers
  Note, A variant is 8-bit word, B variant is 16-bit word
  """
  def contents(self):
    super().contents()

    self.ic = self.Block(E93Lc_B_Device(self.size))
    self.assign(self.actual_size, self.ic.actual_size)
    self.connect(self.pwr, self.ic.vcc)
    self.connect(self.gnd, self.ic.gnd)
    self.connect(self.spi, self.ic.spi)
    self.connect(self.cs, self.ic.cs)

    self.vcc_cap = self.Block(DecouplingCapacitor(
      capacitance=0.1*uFarad(tol=0.2)
    )).connected(self.gnd, self.pwr)
