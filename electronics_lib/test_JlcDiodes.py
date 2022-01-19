import unittest
from .test_passive_common import *
from .JlcDiodes import *

class JlcGeneralDiodeTestTop(Block):
  def __init__(self):
    super().__init__()
    self.dut = self.Block(JlcDiode(
      voltage_rating = (0, 1000) * Volt,
      current_rating = (0, 1) * Amp,
      voltage_drop = (0, 1.1) * Volt
    ))
    (self.dummya, ), _ = self.chain(self.dut.cathode, self.Block(PassiveDummy()))
    (self.dummyb, ), _ = self.chain(self.dut.anode, self.Block(PassiveDummy()))


class JlcGeneralDiodeTestCase(unittest.TestCase):
  def test_diode(self) -> None:
    compiled = ScalaCompiler.compile(JlcGeneralDiodeTestTop)
    self.assertEqual(compiled.get_value(['dut', 'footprint_name']), 'SOD-123FL')
    self.assertEqual(compiled.get_value(['dut', 'part']), 'SM4007PL')
    self.assertEqual(compiled.get_value(['dut', 'value']), '1.1V 1A 10uA 1kV 1kV - 1A SOD-123FL Diodes - General Purpose ROHS')
    self.assertEqual(compiled.get_value(['dut', 'lcsc_part']), 'C64898')


  def test_diode_part(self) -> None:
    compiled = ScalaCompiler.compile(JlcGeneralDiodeTestTop, Refinements(
      instance_values=[(['dut', 'part_spec'], 'M7')]
    ))
    self.assertEqual(compiled.get_value(['dut', 'footprint_name']), 'SMA,DO-214AC')
    self.assertEqual(compiled.get_value(['dut', 'part']), 'M7')
    self.assertEqual(compiled.get_value(['dut', 'value']), '1.1V 1A 1kV 5uA 1kV - 1A SMA(DO-214AC) Diodes - General Purpose ROHS')


  def test_diode_footprint(self) -> None:
    compiled = ScalaCompiler.compile(JlcGeneralDiodeTestTop, Refinements(
      instance_values=[(['dut', 'footprint_spec'], 'SMA,DO-214AC')]
    ))
    self.assertEqual(compiled.get_value(['dut', 'footprint_name']), 'SMA,DO-214AC')
    self.assertEqual(compiled.get_value(['dut', 'part']), 'M7')
    self.assertEqual(compiled.get_value(['dut', 'value']), '1.1V 1A 1kV 5uA 1kV - 1A SMA(DO-214AC) Diodes - General Purpose ROHS')



class JlcSwitchingDiodeTestTop(Block):
  def __init__(self):
    super().__init__()
    self.dut = self.Block(JlcDiode(
      voltage_rating = (0, 75) * Volt,
      current_rating = (0, 0.01) * Amp,
      voltage_drop = (0, 1) * Volt,
      reverse_recovery = (0, 4) * nSecond
    ))
    (self.dummya, ), _ = self.chain(self.dut.pos, self.Block(PassiveDummy()))
    (self.dummyb, ), _ = self.chain(self.dut.neg, self.Block(PassiveDummy()))


class JlcSwitchingDiodeTestCase(unittest.TestCase):
  def test_diode(self) -> None:
    compiled = ScalaCompiler.compile(JlcSwitchingDiodeTestTop)
    self.assertEqual(compiled.get_value(['dut', 'footprint_name']), 'LL-34')
    self.assertEqual(compiled.get_value(['dut', 'part']), 'LL4148')
    self.assertEqual(compiled.get_value(['dut', 'value']), '5uA 75V - 500mW 4ns 1V 10mA +175℃ (Tj) 200mA - 75V LL-34 Switching Diode ROHS')
    self.assertEqual(compiled.get_value(['dut', 'lcsc_part']), 'C9808')



class JlcSchottkyDiodeTestTop(Block):
  def __init__(self):
    super().__init__()
    self.dut = self.Block(JlcDiode(
      voltage_rating = (0, 30) * Volt,
      current_rating = (0, 0.2) * Amp,
      voltage_drop = (0, 0.8) * Volt
    ))
    (self.dummya, ), _ = self.chain(self.dut.pos, self.Block(PassiveDummy()))
    (self.dummyb, ), _ = self.chain(self.dut.neg, self.Block(PassiveDummy()))


class JlcSchottkyDiodeTestCase(unittest.TestCase):
  def test_diode(self) -> None:
    compiled = ScalaCompiler.compile(JlcSchottkyDiodeTestTop)
    self.assertEqual(compiled.get_value(['dut', 'footprint_name']), 'SOT-23-3')
    self.assertEqual(compiled.get_value(['dut', 'part']), 'BAT54C,215')
    self.assertEqual(compiled.get_value(['dut', 'value']), '30V 200mA 800mV @ 100mA SOT-23(SOT-23-3) Schottky Barrier Diodes (SBD) ROHS')
    self.assertEqual(compiled.get_value(['dut', 'lcsc_part']), 'C37704')



class JlcZenerDiodeTestTop(Block):
  def __init__(self):
    super().__init__()
    self.dut = self.Block(JlcDiode(
      zener_voltage = (0, 3.3) * Volt,
      power_rating = (0, 0.5) * Watt,
      forward_voltage_drop = (0, 1) * Volt
    ))
    (self.dummya, ), _ = self.chain(self.dut.pos, self.Block(PassiveDummy()))
    (self.dummyb, ), _ = self.chain(self.dut.neg, self.Block(PassiveDummy()))


class JlcZenerDiodeTestCase(unittest.TestCase):
  def test_diode(self) -> None:
    compiled = ScalaCompiler.compile(JlcZenerDiodeTestTop)
    self.assertEqual(compiled.get_value(['dut', 'footprint_name']), 'LL-34')
    self.assertEqual(compiled.get_value(['dut', 'part']), 'ZMM3V3')
    self.assertEqual(compiled.get_value(['dut', 'value']), '- 3.3V <2uA @ 1V 500mW LL-34 Zener Diodes ROHS')
    self.assertEqual(compiled.get_value(['dut', 'lcsc_part']), 'C8056')



class JlcTVSDiodeTestTop(Block):
  def __init__(self):
    super().__init__()
    self.dut = self.Block(JlcDiode(
      zener_voltage = (0, 3.3) * Volt,
      power_rating = (0, 0.5) * Watt,
      forward_voltage_drop = (0, 1) * Volt
    ))
    (self.dummya, ), _ = self.chain(self.dut.pos, self.Block(PassiveDummy()))
    (self.dummyb, ), _ = self.chain(self.dut.neg, self.Block(PassiveDummy()))


class JlcZenerDiodeTestCase(unittest.TestCase):
  def test_diode(self) -> None:
    compiled = ScalaCompiler.compile(JlcZenerDiodeTestTop)
    self.assertEqual(compiled.get_value(['dut', 'footprint_name']), 'LL-34')
    self.assertEqual(compiled.get_value(['dut', 'part']), 'ZMM3V3')
    self.assertEqual(compiled.get_value(['dut', 'value']), '- 3.3V <2uA @ 1V 500mW LL-34 Zener Diodes ROHS')
    self.assertEqual(compiled.get_value(['dut', 'lcsc_part']), 'C8056')