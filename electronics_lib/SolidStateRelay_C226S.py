from electronics_abstract_parts import *


class C226S(SolidStateRelay_Device, FootprintBlock):
  def contents(self):
    super().contents()
    self.assign(self.led_forward_voltage, (1.0, 1.5)*Volt)
    self.assign(self.led_current_limit, (3, 50)*mAmp)
    self.assign(self.led_current_recommendation, (5, 10)*mAmp)  # test conditions; 3 mA is upper turn-on limit
    self.assign(self.load_current_limit, (0, 1.6)*Amp)  # higher pulsed current limit
    self.assign(self.load_resistance, (85, 500)*mAmp)  # 85mOhm is typical

    self.footprint(
      'U', 'Package_SO:SO-4_4.4x4.3mm_P2.54mm',
      {
        '1': self.leda,
        '2': self.ledk,
        '3': self.feta,
        '4': self.fetb,
      },
      mfr='Coto Technology', part='C226S',
      datasheet='https://www.cotorelay.com/wp-content/uploads/2014/10/c226s_c326s_mosfet_relay_datasheet.pdf'
    )
