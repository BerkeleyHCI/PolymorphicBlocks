from electronics_abstract_parts import *


class G3VM_61GR2(SolidStateRelay, FootprintBlock):
  def contents(self):
    super().contents()
    self.assign(self.led_forward_voltage, (1.18, 1.48)*Volt)
    self.assign(self.led_current_limit, (3, 30)*mAmp)
    self.assign(self.led_current_recommendation, (5, 25)*mAmp)  # typ=10mA
    self.assign(self.load_voltage_limit, (-48, 48)*Volt)
    self.assign(self.load_current_limit, (0, 1.3)*Amp)
    self.assign(self.load_resistance, (80, 130)*mOhm)  # 80 mOhm is typical

    self.footprint(
      'U', 'Package_SO:SO-4_4.4x4.3mm_P2.54mm',
      {
        '1': self.leda,
        '2': self.ledk,
        '3': self.feta,
        '4': self.fetb,
      },
      mfr='Omron Electronics', part='G3VM-61GR2',
      datasheet='https://omronfs.omron.com/en_US/ecb/products/pdf/en-g3vm_61gr2.pdf'
    )
