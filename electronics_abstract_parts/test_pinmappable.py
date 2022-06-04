import unittest

from .PinMappable import UartPort, Volt, mAmp
from .PinMappable import PinMapUtil, PinResource, Passive, PeripheralFixedPin, UsbDevicePort, PeripheralAnyResource, \
  DigitalBidir, AnalogSink, AllocatedResource, AutomaticAllocationError, BadUserAssignError, PeripheralFixedResource


class PinMapUtilTest(unittest.TestCase):
  def test_remap(self):
    mapper = PinMapUtil([
      PinResource('PIO1', {'PIO1': Passive()}),
      PinResource('PIO2', {'PIO2': Passive()}),  # dropped
      PeripheralFixedPin('Per1', UsbDevicePort(), {'dp': 'PIO4', 'dm': 'PIO6'}),
      PeripheralAnyResource('Per2', UsbDevicePort()),
    ])
    remapped = mapper.remap_pins({
      'PIO1': '1',
      'PIO4': '4',
      'PIO6': '6',
    })

    assert isinstance(remapped.resources[0], PinResource)  # typer doesn't understand asserttrue
    assert isinstance(mapper.resources[0], PinResource)
    self.assertEqual(remapped.resources[0].pin, '1')
    self.assertTrue(remapped.resources[0].name_models is mapper.resources[0].name_models)  # to avoid __eq__ on models

    assert isinstance(remapped.resources[1], PeripheralFixedPin)
    assert isinstance(mapper.resources[2], PeripheralFixedPin)
    self.assertEqual(remapped.resources[1].name, 'Per1')
    self.assertTrue(remapped.resources[1].port_model is mapper.resources[2].port_model)
    self.assertEqual(remapped.resources[1].inner_allowed_pins, {'dp': '4', 'dm': '6'})

    self.assertTrue(remapped.resources[2] is mapper.resources[3])  # simple passthrough

  def test_assign_assigned(self):  # fully user-specified
    dio_model = DigitalBidir()
    ain_model = AnalogSink()
    allocated = PinMapUtil([
      PinResource('1', {'PIO1': dio_model}),
      PinResource('2', {'PIO2': dio_model}),
      PinResource('3', {'PIO3': dio_model, 'AIn3': ain_model}),
      PinResource('4', {'PIO4': dio_model, 'AIn4': ain_model}),
      PinResource('5', {'AIn5': ain_model}),
    ]).allocate([(DigitalBidir, ['DIO3', 'DIO2']), (AnalogSink, ['AIO4', 'AIO5'])],
                ["DIO3=3", "DIO2=2", "AIO4=4", "AIO5=5"])
    self.assertIn(AllocatedResource(dio_model, 'DIO3', 'PIO3', '3'), allocated)
    self.assertIn(AllocatedResource(dio_model, 'DIO2', 'PIO2', '2'), allocated)
    self.assertIn(AllocatedResource(ain_model, 'AIO4', 'AIn4', '4'), allocated)
    self.assertIn(AllocatedResource(ain_model, 'AIO5', 'AIn5', '5'), allocated)

  def test_assign_mixed(self):  # mix of user-specified and automatic assignments, assuming greedy algo
    dio_model = DigitalBidir()
    ain_model = AnalogSink()
    allocated = PinMapUtil([
      PinResource('1', {'PIO1': dio_model}),
      PinResource('2', {'PIO2': dio_model}),
      PinResource('3', {'PIO3': dio_model, 'AIn3': ain_model}),
      PinResource('4', {'PIO4': dio_model, 'AIn4': ain_model}),
      PinResource('5', {'AIn5': ain_model}),
    ]).allocate([(DigitalBidir, ['DIO3', 'DIO1']), (AnalogSink, ['AIO5', 'AIO4'])],
                ["DIO3=3", "AIO4=4"])
    self.assertIn(AllocatedResource(dio_model, 'DIO3', 'PIO3', '3'), allocated)
    self.assertIn(AllocatedResource(dio_model, 'DIO1', 'PIO1', '1'), allocated)
    self.assertIn(AllocatedResource(ain_model, 'AIO4', 'AIn4', '4'), allocated)
    self.assertIn(AllocatedResource(ain_model, 'AIO5', 'AIn5', '5'), allocated)

  def test_assign_bad(self):  # bad user-specified assignments
    dio_model = DigitalBidir()
    ain_model = AnalogSink()
    with self.assertRaises(BadUserAssignError):
      PinMapUtil([
        PinResource('1', {'PIO1': dio_model}),
        PinResource('3', {'PIO3': dio_model, 'AIn3': ain_model}),
      ]).allocate([(AnalogSink, ['AIO'])],
                  ["AIO=1"])

  def test_assign_duplicated(self):  # duplicated (over-assigned resources) user-specified assignments
    dio_model = DigitalBidir()
    ain_model = AnalogSink()
    with self.assertRaises(BadUserAssignError):
      PinMapUtil([
        PinResource('1', {'PIO1': dio_model}),
        PinResource('3', {'PIO3': dio_model, 'AIn3': ain_model}),
      ]).allocate([(AnalogSink, ['AIO1', 'AIO2'])],
                  ["AIO1=3", "AIO2=3"])

  def test_assign_overflow(self):  # more requested ports than available resources
    dio_model = DigitalBidir()
    ain_model = AnalogSink()
    with self.assertRaises(AutomaticAllocationError):
      PinMapUtil([
        PinResource('1', {'PIO1': dio_model}),
        PinResource('3', {'PIO3': dio_model, 'AIn3': ain_model}),
      ]).allocate([(AnalogSink, ['AIO3', 'AIO4'])])

  def test_assign_bundle_fixed(self):
    usb_model = UsbDevicePort()
    allocated = PinMapUtil([
      PeripheralFixedPin('USB0', usb_model, {'dm': '2', 'dp': '3'}),
    ]).allocate([(UsbDevicePort, ['usb'])],
                ["usb.dm=2", "usb.dp=3"])
    self.assertIn(AllocatedResource(usb_model, 'usb', 'USB0', {'dm': ('2', None), 'dp': ('3', None)}), allocated)

  def test_assign_bundle_fixed_auto(self):
    usb_model = UsbDevicePort()
    allocated = PinMapUtil([
      PeripheralFixedPin('USB0', usb_model, {'dm': '2', 'dp': '3'}),
    ]).allocate([(UsbDevicePort, ['usb'])])
    self.assertIn(AllocatedResource(usb_model, 'usb', 'USB0', {'dm': ('2', None), 'dp': ('3', None)}), allocated)

  def test_assign_bundle_fixed_badspec(self):
    usb_model = UsbDevicePort()
    with self.assertRaises(BadUserAssignError):
      PinMapUtil([
        PeripheralFixedPin('USB0', usb_model, {'dm': '2', 'dp': '3'}),
      ]).allocate([(UsbDevicePort, ['usb'])],
                  ["usb.dm=2", "usb.dp=5"])
    with self.assertRaises(BadUserAssignError):
      PinMapUtil([
        PeripheralFixedPin('USB0', usb_model, {'dm': '2', 'dp': '3'}),
      ]).allocate([(UsbDevicePort, ['usb'])],
                  ["usb.quack=1"])

  def test_assign_bundle_delegating(self):
    dio_model = DigitalBidir()
    ain_model = AnalogSink()
    allocated = PinMapUtil([
      PinResource('1', {'PIO1': dio_model}),
      PinResource('2', {'PIO2': dio_model}),
      PinResource('3', {'PIO3': dio_model, 'AIn3': ain_model}),
      PinResource('5', {'AIn5': ain_model}),  # not assignable
      PeripheralAnyResource('UART0', UartPort(DigitalBidir.empty())),
    ]).allocate([(UartPort, ['uart'])],
                ["uart.tx=1", "uart.rx=3"])
    self.assertEqual(allocated[0].name, 'uart')
    self.assertEqual(allocated[0].resource_name, 'UART0')
    self.assertEqual(allocated[0].pin, {'tx': ('1', 'PIO1'), 'rx': ('3', 'PIO3')})

  def test_assign_bundle_delegating_auto(self):
    dio_model = DigitalBidir()
    ain_model = AnalogSink()
    allocated = PinMapUtil([
      PinResource('1', {'PIO1': dio_model}),
      PinResource('2', {'PIO2': dio_model}),
      PinResource('3', {'PIO3': dio_model, 'AIn3': ain_model}),
      PinResource('5', {'AIn5': ain_model}),  # not assignable
      PeripheralAnyResource('UART0', UartPort(DigitalBidir.empty())),
    ]).allocate([(UartPort, ['uart'])])
    self.assertEqual(allocated[0].name, 'uart')
    self.assertEqual(allocated[0].resource_name, 'UART0')
    self.assertEqual(allocated[0].pin, {'tx': ('1', 'PIO1'), 'rx': ('2', 'PIO2')})

  def test_assign_bundle_delegating_badspec(self):
    dio_model = DigitalBidir()
    ain_model = AnalogSink()
    with self.assertRaises(BadUserAssignError):
      PinMapUtil([
        PinResource('1', {'PIO1': dio_model}),
        PinResource('2', {'PIO2': dio_model}),
        PinResource('3', {'PIO3': dio_model, 'AIn3': ain_model}),
        PinResource('5', {'AIn5': ain_model}),  # not assignable
        PeripheralAnyResource('UART0', UartPort(DigitalBidir.empty())),
      ]).allocate([(UartPort, ['uart'])],
                  ["uart.tx=1", "uart.rx=5"])
    with self.assertRaises(BadUserAssignError):
      PinMapUtil([
        PinResource('1', {'PIO1': dio_model}),
        PinResource('2', {'PIO2': dio_model}),
        PinResource('3', {'PIO3': dio_model, 'AIn3': ain_model}),
        PinResource('5', {'AIn5': ain_model}),  # not assignable
        PeripheralAnyResource('UART0', UartPort(DigitalBidir.empty())),
      ]).allocate([(UartPort, ['uart'])],
                  ["uart.quack=1"])

  def test_assign_bundle_delegating_fixed(self):
    dio_model = DigitalBidir()
    dio_model_tx = DigitalBidir(
      voltage_out=3.3 * Volt(tol=0.01),
    )
    dio_model_rx = DigitalBidir(
      current_draw=1 * mAmp(tol=0.01)
    )
    ain_model = AnalogSink()
    allocated = PinMapUtil([
      PinResource('1', {'PIO1': dio_model_rx}),
      PinResource('2', {'PIO2': dio_model}),
      PinResource('3', {'PIO3': dio_model_tx, 'AIn3': ain_model}),
      PinResource('5', {'AIn5': ain_model}),  # not assignable
      PeripheralFixedResource('UART0', UartPort(DigitalBidir.empty()), {
        'tx': ['PIO3'], 'rx': ['PIO1']
      }),
    ]).allocate([(UartPort, ['uart'])])
    self.assertEqual(allocated[0].name, 'uart')
    self.assertEqual(allocated[0].resource_name, 'UART0')
    self.assertEqual(allocated[0].pin, {'tx': ('3', 'PIO3'), 'rx': ('1', 'PIO1')})

    assert isinstance(allocated[0].port_model, UartPort)
    self.assertTrue(allocated[0].port_model.tx.voltage_out.initializer is not None)
    self.assertTrue(allocated[0].port_model.tx.voltage_out.initializer is dio_model_tx.voltage_out.initializer)
    self.assertTrue(allocated[0].port_model.rx.current_draw.initializer is not None)
    self.assertTrue(allocated[0].port_model.rx.current_draw.initializer is dio_model_rx.current_draw.initializer)

  def test_assign_bundle_delegating_notconnected(self):
    dio_model = DigitalBidir()
    allocated = PinMapUtil([
      PinResource('1', {'PIO1': dio_model}),
      PeripheralAnyResource('UART0', UartPort(DigitalBidir.empty())),
    ]).allocate([(UartPort, ['uart'])],
                ['uart.tx=NC'])
    self.assertEqual(allocated[0].name, 'uart')
    self.assertEqual(allocated[0].resource_name, 'UART0')
    self.assertEqual(allocated[0].pin, {'rx': ('1', 'PIO1')})
