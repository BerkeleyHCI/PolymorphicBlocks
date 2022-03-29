import unittest

from .PinMappable import PinMapUtil, PinResource, Passive, PeripheralFixedPin, UsbDevicePort, PeripheralAnyPinResource, \
  DigitalBidir, AnalogSink, AssignedResource, AutomaticAssignError, BadUserAssignError


class PinMapUtilTest(unittest.TestCase):
  def test_remap(self):
    mapper = PinMapUtil([
      PinResource('PIO1', {'PIO1': Passive()}),
      PinResource('PIO2', {'PIO2': Passive()}),  # dropped
      PeripheralFixedPin('Per1', UsbDevicePort(), {'dp': ['PIO4', 'PIO5'], 'dm': ['PIO6', 'PIO7']}),
      PeripheralAnyPinResource('Per2', UsbDevicePort()),
    ])
    remapped = mapper.remap_pins({
      'PIO1': '1',
      'PIO4': '4',
      'PIO5': '5',
      'PIO6': '6',
      'PIO7': '7',
    })

    assert isinstance(remapped.resources[0], PinResource)  # typer doesn't understand asserttrue
    assert isinstance(mapper.resources[0], PinResource)
    self.assertEqual(remapped.resources[0].pin, '1')
    self.assertTrue(remapped.resources[0].name_models is mapper.resources[0].name_models)  # to avoid __eq__ on models

    assert isinstance(remapped.resources[1], PeripheralFixedPin)
    assert isinstance(mapper.resources[2], PeripheralFixedPin)
    self.assertEqual(remapped.resources[1].name, 'Per1')
    self.assertTrue(remapped.resources[1].port_model is mapper.resources[2].port_model)
    self.assertEqual(remapped.resources[1].inner_allowed_pins, {'dp': ['4', '5'], 'dm': ['6', '7']})

    self.assertTrue(remapped.resources[2] is mapper.resources[3])  # simple passthrough

  @staticmethod
  def assigned_resource_equal(res1: AssignedResource, res2: AssignedResource):
    """Equality check between AssignedResource that avoids triggering Port.__eq__"""
    return res1.port_model is res2.port_model and\
      res1.name == res2.name and res1.resource == res2.resource and res1.pin == res2.pin


  def test_assign_assigned(self):  # fully user-specified
    dio_model = DigitalBidir()
    ain_model = AnalogSink()
    mapped = PinMapUtil([
      PinResource('1', {'PIO1': dio_model}),
      PinResource('2', {'PIO2': dio_model}),
      PinResource('3', {'PIO3': dio_model, 'AIn3': ain_model}),
      PinResource('4', {'PIO4': dio_model, 'AIn4': ain_model}),
      PinResource('5', {'AIn5': ain_model}),
    ]).assign([(DigitalBidir, ['DIO3', 'DIO2']), (AnalogSink, ['AIO4', 'AIO5'])],
              "DIO3=3;DIO2=2;AIO4=4;AIO5=5")
    self.assertTrue(self.assigned_resource_equal(mapped[0], AssignedResource(dio_model, 'DIO3', 'PIO3', '3')))
    self.assertTrue(self.assigned_resource_equal(mapped[1], AssignedResource(dio_model, 'DIO2', 'PIO2', '2')))
    self.assertTrue(self.assigned_resource_equal(mapped[2], AssignedResource(ain_model, 'AIO4', 'AIn4', '4')))
    self.assertTrue(self.assigned_resource_equal(mapped[3], AssignedResource(ain_model, 'AIO5', 'AIn5', '5')))

  def test_assign_mixed(self):  # mix of user-specified and automatic assignments, assuming greedy algo
    dio_model = DigitalBidir()
    ain_model = AnalogSink()
    mapped = PinMapUtil([
      PinResource('1', {'PIO1': dio_model}),
      PinResource('2', {'PIO2': dio_model}),
      PinResource('3', {'PIO3': dio_model, 'AIn3': ain_model}),
      PinResource('4', {'PIO4': dio_model, 'AIn4': ain_model}),
      PinResource('5', {'AIn5': ain_model}),
    ]).assign([(DigitalBidir, ['DIO3', 'DIO1']), (AnalogSink, ['AIO3', 'AIO4'])],
              "DIO3=3;AIO4=4")
    self.assertTrue(self.assigned_resource_equal(mapped[0], AssignedResource(dio_model, 'DIO3', 'PIO3', '3')))
    self.assertTrue(self.assigned_resource_equal(mapped[1], AssignedResource(dio_model, 'DIO1', 'PIO1', '1')))
    self.assertTrue(self.assigned_resource_equal(mapped[2], AssignedResource(ain_model, 'AIO4', 'AIn4', '4')))
    self.assertTrue(self.assigned_resource_equal(mapped[3], AssignedResource(ain_model, 'AIO5', 'AIn5', '5')))

  def test_assign_bad(self):  # bad user-specified assignments
    dio_model = DigitalBidir()
    ain_model = AnalogSink()
    with self.assertRaises(BadUserAssignError):
      PinMapUtil([
        PinResource('1', {'PIO1': dio_model}),
        PinResource('3', {'PIO3': dio_model, 'AIn3': ain_model}),
      ]).assign([(AnalogSink, ['AIO'])],
                "AIO=1")

  def test_assign_duplicated(self):  # duplicated (over-assigned resources) user-specified assignments
    dio_model = DigitalBidir()
    ain_model = AnalogSink()
    with self.assertRaises(BadUserAssignError):
      PinMapUtil([
        PinResource('1', {'PIO1': dio_model}),
        PinResource('3', {'PIO3': dio_model, 'AIn3': ain_model}),
      ]).assign([(AnalogSink, ['AIO1', 'AIO2'])],
                "AIO1=3;AIO2=3")

  def test_assign_overflow(self):  # more requested ports than available resources
    dio_model = DigitalBidir()
    ain_model = AnalogSink()
    with self.assertRaises(AutomaticAssignError):
      PinMapUtil([
        PinResource('1', {'PIO1': dio_model}),
        PinResource('3', {'PIO3': dio_model, 'AIn3': ain_model}),
      ]).assign([(AnalogSink, ['AIO3', 'AIO4'])])

  def test_assign_bundle(self):  # more requested ports than available resources
    self.assertEqual(True, False)

