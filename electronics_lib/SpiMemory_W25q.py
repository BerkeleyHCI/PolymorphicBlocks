from electronics_abstract_parts import *
from .JlcPart import JlcPart


class W25q_Device(DiscreteChip, GeneratorBlock, JlcPart, FootprintBlock):
  PARTS = [
    # note, 8Mib version considered obsolete at DigiKey
    (16*1024*1024, 'W25Q16JVSSIQ', 'https://www.winbond.com/resource-files/w25q16jv%20spi%20revg%2003222018%20plus.pdf',
     'C82317', False),
    (32*1024*1024, 'W25Q32JVSSIQ', 'https://www.winbond.com/resource-files/w25q32jv%20revg%2003272018%20plus.pdf',
     'C82344', False),
    (64*1024*1024, 'W25Q64JVSSIQ', 'https://www.winbond.com/resource-files/w25q64jv%20revj%2003272018%20plus.pdf',
     'C179171', False),
    (128*1024*1024, 'W25Q128JVSIQ', 'https://www.winbond.com/resource-files/W25Q128JV%20RevI%2008232021%20Plus.pdf',
     'C97521', True),
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
    self.spi = self.Port(SpiSlave(dio_model, (0, 104)*MHertz))
    self.cs = self.Port(dio_model)

    self.actual_size = self.Parameter(IntExpr())

    self.generator(self.generate, size)

  def generate(self, size: Range):
    suitable_parts = [part for part in self.PARTS if part[0] in size]
    assert suitable_parts, f"no memory in requested size range {size}"
    part_size, part_pn, part_datasheet, part_lcsc, part_lcsc_basic = suitable_parts[0]

    self.assign(self.actual_size, part_size)
    self.footprint(
      'U', 'Package_SO:SOIC-8_3.9x4.9mm_P1.27mm',
      {
        '1': self.cs,
        '2': self.spi.miso,
        '3': self.vcc,  # /WP
        '4': self.gnd,
        '5': self.spi.mosi,
        '6': self.spi.sck,
        '7': self.vcc,  # /HOLD
        '8': self.vcc,
      },
      mfr='Winbond Electronics', part=part_pn,
      datasheet=part_datasheet
    )
    self.assign(self.lcsc_part, part_lcsc)
    self.assign(self.actual_basic_part, part_lcsc_basic)


class W25q(SpiMemory):
  """Winbond W25Q series of SPI memory devices
  """
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
