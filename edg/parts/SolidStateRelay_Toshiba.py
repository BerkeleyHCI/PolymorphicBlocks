from ..abstract_parts import *


class Tlp3545a(SolidStateRelay, FootprintBlock, GeneratorBlock):
  @init_in_parent
  def __init__(self, *args, swap: BoolLike = False, **kwargs):
    super().__init__(*args, **kwargs)
    self.swap = self.ArgParameter(swap)
    self.generator_param(self.swap)

  def generate(self):
    super().generate()
    self.assign(self.led_forward_voltage, (1.50, 1.80)*Volt)
    self.assign(self.led_current_limit, (5, 30)*mAmp)
    self.assign(self.led_current_recommendation, (5, 25)*mAmp)  # typ=10mA
    self.assign(self.load_voltage_limit, (-48, 48)*Volt)  # recommended, up to 60 max
    self.assign(self.load_current_limit, (-4, 4)*Amp)
    self.assign(self.load_resistance, (35, 60)*mOhm)  # 'A' connection, supports AC but higher resistance

    self.footprint(
      'U', 'Package_DIP:SMDIP-6_W7.62mm',
      {
        '1': self.leda,
        '2': self.ledk,
        # '3': nc,
        '4': self.feta if not self.get(self.swap) else self.fetb,  # 'A' connection
        # '5': source - common
        '6': self.fetb if not self.get(self.swap) else self.feta,
      },
      mfr='Toshiba', part='TLP3545A(TP1,F',
      datasheet='https://toshiba.semicon-storage.com/info/docget.jsp?did=60318&prodName=TLP3545A'
    )


class Tlp170am(SolidStateRelay, FootprintBlock, GeneratorBlock):
  @init_in_parent
  def __init__(self, *args, swap: BoolLike = False, **kwargs):
    super().__init__(*args, **kwargs)
    self.swap = self.ArgParameter(swap)
    self.generator_param(self.swap)

  def generate(self):
    super().generate()
    self.assign(self.led_forward_voltage, (1.1, 1.4)*Volt)  # 1.27 nominal
    self.assign(self.led_current_limit, (2, 30)*mAmp)
    self.assign(self.led_current_recommendation, (2, 25)*mAmp)  # typ=2mA
    self.assign(self.load_voltage_limit, (-48, 48)*Volt)  # recommended, up to 60 max
    self.assign(self.load_current_limit, (-700, 700)*mAmp)
    self.assign(self.load_resistance, (0.15, 0.30)*Ohm)

    self.footprint(
      'U', 'Package_SO:SO-4_4.4x3.6mm_P2.54mm',  # package outline by just a tad (0.15mm)
      {
        '1': self.leda,
        '2': self.ledk,
        '3': self.feta if not self.get(self.swap) else self.fetb,
        '4': self.fetb if not self.get(self.swap) else self.feta,
      },
      mfr='Toshiba', part='TLP170AM(TPL,E',
      datasheet='https://toshiba.semicon-storage.com/info/TLP170AM_datasheet_en_20210524.pdf?did=69016&prodName=TLP170AM'
    )
