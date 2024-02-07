from electronics_abstract_parts import *


class Tlp3545a(SolidStateRelay, FootprintBlock):
  def contents(self):
    super().contents()
    self.assign(self.led_forward_voltage, (1.50, 1.80)*Volt)
    self.assign(self.led_current_limit, (5, 30)*mAmp)
    self.assign(self.led_current_recommendation, (5, 19.5)*mAmp)  # typ=10mA
    self.assign(self.load_voltage_limit, (-48, 48)*Volt)
    self.assign(self.load_current_limit, (0, 2.6)*Amp)
    self.assign(self.load_resistance, (35, 60)*mOhm)  # 'A' connection, supports AC but higher resistance

    self.footprint(
      'U', 'Package_DIP:SMDIP-6_W7.62mm',
      {
        '1': self.leda,
        '2': self.ledk,
        # '3': nc,
        '4': self.feta,  # 'A' connection
        # '5': source - common
        '6': self.fetb,
      },
      mfr='Toshiba', part='TLP3545A(TP1,F',
      datasheet='https://toshiba.semicon-storage.com/info/docget.jsp?did=60318&prodName=TLP3545A'
    )
