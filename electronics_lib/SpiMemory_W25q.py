from electronics_abstract_parts import *
from .JlcPart import JlcPart


class W25q_Device(InternalSubcircuit, GeneratorBlock, JlcPart, FootprintBlock):
  PARTS = [
    # prefer the basic part version
    (128*1024*1024, 'W25Q128JVSIQ', 'https://www.winbond.com/resource-files/W25Q128JV%20RevI%2008232021%20Plus.pdf',
     'C97521', True),
    # note, 8Mib version considered obsolete at DigiKey
    (16*1024*1024, 'W25Q16JVSSIQ', 'https://www.winbond.com/resource-files/w25q16jv%20spi%20revg%2003222018%20plus.pdf',
     'C82317', False),
    (32*1024*1024, 'W25Q32JVSSIQ', 'https://www.winbond.com/resource-files/w25q32jv%20revg%2003272018%20plus.pdf',
     'C82344', False),
    (64*1024*1024, 'W25Q64JVSSIQ', 'https://www.winbond.com/resource-files/w25q64jv%20revj%2003272018%20plus.pdf',
     'C179171', False),
    # higher capacity variants available but not in SOIC-8
  ]

  @init_in_parent
  def __init__(self, size: RangeLike):
    super().__init__()
    self.vcc = self.Port(VoltageSink(
      voltage_limits=(2.7, 3.6)*Volt,  # relaxed range that goes up to 104MHz
      current_draw=(0.001, 25)*uAmp  # typ. power down to max write / erase
    ), [Power])
    self.gnd = self.Port(Ground(), [Common])

    dio_model = DigitalBidir.from_supply(
      self.gnd, self.vcc,
      voltage_limit_tolerance=(-0.5, 0.4),
      input_threshold_factor=(0.3, 0.7)
    )
    self.spi = self.Port(SpiPeripheral(dio_model, (0, 104) * MHertz))
    self.cs = self.Port(dio_model)
    self.wp = self.Port(dio_model)
    self.hold = self.Port(dio_model)

    self.actual_size = self.Parameter(IntExpr())

    self.size = self.ArgParameter(size)
    self.generator_param(self.size)

  def generate(self):
    super().generate()
    suitable_parts = [part for part in self.PARTS if part[0] in self.get(self.size)]
    assert suitable_parts, "no memory in requested size range"
    part_size, part_pn, part_datasheet, part_lcsc, part_lcsc_basic = suitable_parts[0]

    self.assign(self.actual_size, part_size)
    self.footprint(
      'U', 'Package_SO:SOIC-8_5.23x5.23mm_P1.27mm',
      {
        '1': self.cs,
        '2': self.spi.miso,
        '3': self.wp,
        '4': self.gnd,
        '5': self.spi.mosi,
        '6': self.spi.sck,
        '7': self.hold,
        '8': self.vcc,
      },
      mfr='Winbond Electronics', part=part_pn,
      datasheet=part_datasheet
    )
    self.assign(self.lcsc_part, part_lcsc)
    self.assign(self.actual_basic_part, part_lcsc_basic)


class W25q(SpiMemory ,SpiMemoryQspi, GeneratorBlock):
  """Winbond W25Q series of SPI memory devices
  """
  def __init__(self, *args, **kwargs):
    super().__init__(*args, **kwargs)
    self.generator_param(self.io2.is_connected(), self.io3.is_connected())

  def contents(self):
    super().contents()

    self.ic = self.Block(W25q_Device(self.size))
    self.assign(self.actual_size, self.ic.actual_size)
    self.connect(self.pwr, self.ic.vcc)
    self.connect(self.gnd, self.ic.gnd)
    self.connect(self.spi, self.ic.spi)
    self.connect(self.cs, self.ic.cs)

    self.vcc_cap = self.Block(DecouplingCapacitor(
      capacitance=0.1*uFarad(tol=0.2)
    )).connected(self.gnd, self.pwr)

  def generate(self):
    super().generate()

    self.require(self.io2.is_connected() == self.io3.is_connected())
    if self.get(self.io2.is_connected()):  # connect QSPI lines if used
      self.connect(self.io2, self.ic.wp)
      self.connect(self.io3, self.ic.hold)
    else:  # otherwise tie high by default
      self.connect(self.pwr.as_digital_source(), self.ic.wp, self.ic.hold)
