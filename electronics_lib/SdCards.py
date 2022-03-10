from typing import *

from electronics_abstract_parts import *


@abstract_block
class SdCard(Memory):
  """Minimum connections for SD card, with IOs definitions set according to SD card spec"""
  def __init__(self) -> None:
    super().__init__()

    # Power characteristics from SD Physical Layer Simplified Spec Ver 6.00:
    # Voltage range from Fig 6-5, current limits from VDD_W_CURR_MAX table in 5.3.2 - note some cards may draw less
    self.pwr = self.Port(VoltageSink(voltage_limits=(2.7, 4.6) * Volt, current_draw=(0, 200) * mAmp), [Power])
    self.gnd = self.Port(Ground(), [Common])  # TODO need to peg at 0v

    # IO thresholds from NXP AN10911 "SD(HC)-memory card and MMC interface conditioning"
    # Many devices also allow a +/-0.3v tolerance above / below Vdd/Vss
    dio_model = DigitalBidir(
      voltage_limits=(-0.3 * Volt, self.pwr.link().voltage.upper() + 0.3 * Volt),
      current_draw=(0, 0) * Amp,
      voltage_out=(0 * Volt, self.pwr.link().voltage.upper()),
      current_limits=(0, 0) * mAmp,  # TODO drive strength not specified
      input_thresholds=(0.25 * self.pwr.link().voltage.lower(),
                        0.625 * self.pwr.link().voltage.upper()),
      output_thresholds=(0.125 * self.pwr.link().voltage.upper(),
                         0.75 * self.pwr.link().voltage.lower())
    )

    self.spi = self.Port(SpiSlave(dio_model), [InOut])  # TODO does this port directionality make sense?
    self.cs = self.Port(DigitalSink.from_bidir(dio_model))


class SdSocket(SdCard, Connector, FootprintBlock):
  """Full-sized SD card socket"""
  def __init__(self) -> None:
    super().__init__()

    # TODO switch current rating not provided by datasheet, here's some probably sane default
    sw_model = DigitalSingleSource.low_from_supply(self.gnd)  # current_limits=(0, 20)*mAmp
    self.cd = self.Port(sw_model, optional=True)
    self.wp = self.Port(sw_model, optional=True)

  def contents(self) -> None:
    super().contents()
    # TODO do we need capacitors?
    self.footprint(
      'J', 'Connector_Card:SD_Kyocera_145638009511859+',
      {
        '1': self.cs,
        '2': self.spi.mosi,
        '3': self.gnd,
        '4': self.pwr,
        '5': self.spi.sck,
        '6': self.gnd,
        '7': self.spi.miso,
        # '8': ,  # unused in SPI mode
        # '9': ,  # unused in SPI mode
        '10': self.cd,
        '11': self.wp,

        'SH': self.gnd,  # shell
      },
      mfr='Kyocera', part='145638009511859+',
      datasheet='http://global.kyocera.com/prdct/electro/product/pdf/5638.pdf'
    )


class MicroSdSocket(SdCard, Connector, FootprintBlock):
  """MicroSD socket"""
  def __init__(self) -> None:
    super().__init__()

  def contents(self):
    super().contents()
    # TODO add pull up resistors and capacitors and w/e?
    self.footprint(
      'J', 'Connector_Card:microSD_HC_Hirose_DM3BT-DSF-PEJS',
      {
        # '1': ,  # unused in SPI mode
        '2': self.cs,
        '3': self.spi.mosi,
        '4': self.pwr,
        '5': self.spi.sck,
        '6': self.gnd,
        '7': self.spi.miso,
        # '8': ,  # unused in SPI mode

        '11': self.gnd,  # shell
      },
      mfr='Mirose', part='DM3BT-DSF-PEJS',
      datasheet='https://www.hirose.com/product/download/?distributor=digikey&type=2d&lang=en&num=DM3BT-DSF-PEJS'
    )
