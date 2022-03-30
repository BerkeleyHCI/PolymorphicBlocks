import unittest

from electronics_model import UartPort
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
    self.assertIn(AssignedResource(dio_model, 'DIO3', 'PIO3', '3'), mapped)
    self.assertIn(AssignedResource(dio_model, 'DIO2', 'PIO2', '2'), mapped)
    self.assertIn(AssignedResource(ain_model, 'AIO4', 'AIn4', '4'), mapped)
    self.assertIn(AssignedResource(ain_model, 'AIO5', 'AIn5', '5'), mapped)

  def test_assign_mixed(self):  # mix of user-specified and automatic assignments, assuming greedy algo
    dio_model = DigitalBidir()
    ain_model = AnalogSink()
    mapped = PinMapUtil([
      PinResource('1', {'PIO1': dio_model}),
      PinResource('2', {'PIO2': dio_model}),
      PinResource('3', {'PIO3': dio_model, 'AIn3': ain_model}),
      PinResource('4', {'PIO4': dio_model, 'AIn4': ain_model}),
      PinResource('5', {'AIn5': ain_model}),
    ]).assign([(DigitalBidir, ['DIO3', 'DIO1']), (AnalogSink, ['AIO5', 'AIO4'])],
              "DIO3=3;AIO4=4")
    self.assertIn(AssignedResource(dio_model, 'DIO3', 'PIO3', '3'), mapped)
    self.assertIn(AssignedResource(dio_model, 'DIO1', 'PIO1', '1'), mapped)
    self.assertIn(AssignedResource(ain_model, 'AIO4', 'AIn4', '4'), mapped)
    self.assertIn(AssignedResource(ain_model, 'AIO5', 'AIn5', '5'), mapped)

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

  def test_assign_bundle_fixed(self):
    usb_model = UsbDevicePort()
    mapped = PinMapUtil([
      PeripheralFixedPin('USB0', usb_model, {'dm': ['1', '2'], 'dp': ['3', '4']}),
    ]).assign([(UsbDevicePort, ['usb'])],
              "usb.dm=2;usb.dp=3")
    self.assertIn(AssignedResource(usb_model, 'usb', 'USB0', {'dm': '2', 'dp': '3'}), mapped)

  def test_assign_bundle_fixed_auto(self):
    usb_model = UsbDevicePort()
    mapped = PinMapUtil([
      PeripheralFixedPin('USB0', usb_model, {'dm': ['1', '2'], 'dp': ['3', '4']}),
    ]).assign([(UsbDevicePort, ['usb'])])
    self.assertIn(AssignedResource(usb_model, 'usb', 'USB0', {'dm': '1', 'dp': '3'}), mapped)

  def test_assign_bundle_fixed_badspec(self):
    usb_model = UsbDevicePort()
    with self.assertRaises(BadUserAssignError):
      PinMapUtil([
        PeripheralFixedPin('USB0', usb_model, {'dm': ['1', '2'], 'dp': ['3', '4']}),
      ]).assign([(UsbDevicePort, ['usb'])],
                "usb.dm=2;usb.dp=5")
    with self.assertRaises(BadUserAssignError):
      PinMapUtil([
        PeripheralFixedPin('USB0', usb_model, {'dm': ['1', '2'], 'dp': ['3', '4']}),
      ]).assign([(UsbDevicePort, ['usb'])],
                "usb.quack=1")

  def test_assign_bundle_delegating(self):
    dio_model = DigitalBidir()
    ain_model = AnalogSink()
    mapped = PinMapUtil([
      PinResource('1', {'PIO1': dio_model}),
      PinResource('2', {'PIO2': dio_model}),
      PinResource('3', {'PIO3': dio_model, 'AIn3': ain_model}),
      PinResource('5', {'AIn5': ain_model}),  # not assignable
      PeripheralAnyPinResource('UART0', UartPort()),
    ]).assign([(UartPort, ['uart'])],
              "uart.tx=1;uart.rx=3")
    self.assertEqual(mapped[0].name, 'uart')
    self.assertEqual(mapped[0].resource, 'UART0')
    self.assertEqual(mapped[0].pin, {'tx': '1', 'rx': '3'})

  def test_assign_bundle_delegating_auto(self):
    dio_model = DigitalBidir()
    ain_model = AnalogSink()
    mapped = PinMapUtil([
      PinResource('1', {'PIO1': dio_model}),
      PinResource('2', {'PIO2': dio_model}),
      PinResource('3', {'PIO3': dio_model, 'AIn3': ain_model}),
      PinResource('5', {'AIn5': ain_model}),  # not assignable
      PeripheralAnyPinResource('UART0', UartPort()),
    ]).assign([(UartPort, ['uart'])])
    self.assertEqual(mapped[0].name, 'uart')
    self.assertEqual(mapped[0].resource, 'UART0')
    self.assertEqual(mapped[0].pin, {'tx': '1', 'rx': '2'})

  def test_assign_bundle_delegating_badspec(self):
    dio_model = DigitalBidir()
    ain_model = AnalogSink()
    with self.assertRaises(BadUserAssignError):
      PinMapUtil([
        PinResource('1', {'PIO1': dio_model}),
        PinResource('2', {'PIO2': dio_model}),
        PinResource('3', {'PIO3': dio_model, 'AIn3': ain_model}),
        PinResource('5', {'AIn5': ain_model}),  # not assignable
        PeripheralAnyPinResource('UART0', UartPort()),
      ]).assign([(UartPort, ['uart'])],
                "uart.tx=1;uart.rx=5")
    with self.assertRaises(BadUserAssignError):
      PinMapUtil([
        PinResource('1', {'PIO1': dio_model}),
        PinResource('2', {'PIO2': dio_model}),
        PinResource('3', {'PIO3': dio_model, 'AIn3': ain_model}),
        PinResource('5', {'AIn5': ain_model}),  # not assignable
        PeripheralAnyPinResource('UART0', UartPort()),
      ]).assign([(UartPort, ['uart'])],
                "uart.quack=1")
