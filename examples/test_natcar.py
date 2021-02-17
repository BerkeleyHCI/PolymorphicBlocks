import os
import unittest
import sys

from edg import *
import edg_core.TransformUtil as tfu

class HalfBridgeWithDriver(Block):
  # TODO make not-UC21222 specific (generic HalfBridgeDriver interface?) and throw into a lib package
  def __init__(self):
    super().__init__()
    self.gnd = self.Port(Ground(), [Common])

    with self.implicit_connect(
        ImplicitConnect(self.gnd, [Common]),
    ) as imp:
      self.drv = imp.Block(Ucc21222_HalfbridgeDriver())
      self.pwr = self.Export(self.drv.pwr, [Power])
      self.connect(self.gnd, self.drv.gnd_drv)
      self.pwr_drv = self.Export(self.drv.pwr_drv)
      self.pwr_hv = self.Export(self.drv.pwr_hv)
      self.dis = self.Export(self.drv.dis)

      (self.rca, self.pda), _ = self.chain(
        imp.Block(DigitalLowPassRc(impedance=150*Ohm(tol=0.05), cutoff_freq=10*MHertz(tol=0.2))),
        imp.Block(PulldownResistor(resistance=10*kOhm(tol=0.2))),
        self.drv.ina)
      self.ina = self.Export(self.rca.input)
      (self.rcb, self.pdb), _ = self.chain(
        imp.Block(DigitalLowPassRc(impedance=150*Ohm(tol=0.05), cutoff_freq=10*MHertz(tol=0.2))),
        imp.Block(PulldownResistor(resistance=10*kOhm(tol=0.2))),
        self.drv.inb)
      self.inb = self.Export(self.rcb.input)

      self.hb = imp.Block(HalfBridgeNFet(frequency=(0, 1)*kHertz))
      self.connect(self.hb.pwr, self.pwr_hv)
      self.connect(self.drv.outa, self.hb.gate_high)
      self.connect(self.drv.outb, self.hb.gate_low)
      self.out = self.Export(self.hb.output)
      self.connect(self.hb.output.as_electrical_source(), self.drv.drv_common)

  def contents(self):
    super().contents()


class TestNatcar(Block):
  def contents(self) -> None:
    super().contents()

    self.pwr_in = self.Block(NatcarBatteryConnector())
    self.motor = self.Block(NatcarBrushedMotorConnector())

    self.vin = self.connect(self.pwr_in.pwr)
    self.gnd = self.connect(self.pwr_in.gnd)

    with self.implicit_connect(
        ImplicitConnect(self.pwr_in.gnd, [Common]),
    ) as imp:
      self.prot = imp.Block(ProtectionZenerDiode(voltage=15*Volt(tol=0.05)))
      self.connect(self.prot.pwr, self.pwr_in.pwr)

      self.adc_conn = imp.Block(BeagleBoneBlueAdcConnector())
      self.gpio_conn = imp.Block(BeagleBoneBlueGpioConnector())
      self.pwm_conn = imp.Block(BeagleBoneBlueGpsPwmConnector())
      self.servo_conn = imp.Block(BeagleBoneBlueDigitalPin())

      self.drv1 = imp.Block(HalfBridgeWithDriver())
      self.connect(self.drv1.pwr, self.gpio_conn.pwr)
      self.connect(self.drv1.pwr_hv, self.drv1.pwr_drv, self.pwr_in.pwr)
      self.connect(self.drv1.ina, self.pwm_conn.pwm1)
      self.connect(self.drv1.inb, self.pwm_conn.pwm0)
      self.connect(self.drv1.dis, self.gpio_conn.gp0)
      self.connect(self.drv1.out, self.motor.a)

      self.connect(self.pwr_in.gnd, self.motor.b)

      self.usb_conn = imp.Block(UsbAReceptacle())
      self.connect(self.usb_conn.shield.as_ground(), self.pwr_in.gnd)  # TODO should be default part of USB library
      (self.reg_bbl, self.bbl_led), _ = self.chain(
        self.pwr_in.pwr,
        imp.Block(Lmr33630(output_voltage=5.0*Volt(tol=0.04), input_ripple_limit=0.25*Volt,
                           ripple_current_factor=(0.25, 0.5))),
        imp.Block(VoltageIndicatorLed()),
        self.usb_conn.pwr)
      # TODO replace with forced override
      # self.constrain(self.reg_bbl.pwr_out.link().current_drawn == (0, 3)*Amp, unchecked=True)  # manual loading

      self.cam_conn = imp.Block(FreescaleLineCameraConnector())
      self.connect(self.cam_conn.vdd, self.gpio_conn.pwr)
      (self.cam_div, ), _ = self.chain(
        self.cam_conn.aout,
        imp.Block(SignalDivider(ratio=(1.8/3.6*0.85, 1.8/3.6), impedance=(500, 5000)*Ohm)),
        self.adc_conn.ain0)
      self.connect(self.cam_conn.si, self.gpio_conn.gp3)
      self.connect(self.cam_conn.clk, self.gpio_conn.gp2)

      self.srv = imp.Block(ServoConnector(current_draw=(0, 2)*Amp))
      (self.reg_srv, self.srv_led), _ = self.chain(
        self.pwr_in.pwr,
        imp.Block(Lmr33630(output_voltage=6.0*Volt(tol=0.055), input_ripple_limit=0.25*Volt,
                           ripple_current_factor=(0.25, 0.5))),
        imp.Block(VoltageIndicatorLed()),
        self.srv.pwr)
      self.connect(self.servo_conn.io, self.srv.sig)

      self.v1 = self.Block(MountingHole_NoPad_M2_5())
      self.v2 = self.Block(MountingHole_NoPad_M2_5())
      self.connect(self.pwr_in.gnd, self.v1.pad.as_ground(), self.v2.pad.as_ground())

    self.hole = ElementDict[MountingHole]()
    for i in range(4):
      self.hole[i] = self.Block(MountingHole_M3())

    self.duck = self.Block(DuckLogo())
    self.leadfree = self.Block(LeadFreeIndicator())
    self.id = self.Block(IdDots4())


class NatcarTestCase(unittest.TestCase):
  def test_design(self) -> None:
    ElectronicsDriver([sys.modules[__name__]]).generate_write_block(
      TestNatcar(),
      os.path.splitext(__file__)[0],
      {
        # TODO we don't use the proper chip since Digikey incorrectly list the footprint as TO-263-4 (3 pins + tab)
        # and was not included in the product table
        # tfu.Path.empty().append_block('drv1').append_block('hb').append_block('high').append_param('part'): 'CSD18542KTT',
        # tfu.Path.empty().append_block('drv1').append_block('hb').append_block('low').append_param('part'): 'CSD18542KTT',
        tfu.Path.empty().append_block('drv1').append_block('hb').append_block('high').append_param('footprint_name'): 'Package_TO_SOT_SMD:TO-263-2',
        tfu.Path.empty().append_block('drv1').append_block('hb').append_block('low').append_param('footprint_name'): 'Package_TO_SOT_SMD:TO-263-2',
        tfu.Path.empty().append_block('drv1').append_block('drv').append_block('boot_dio').append_param('footprint_name'): 'Diode_SMD:D_SOD-123',

        tfu.Path.empty().append_block('prot').append_param('package'): 'Diode_SMD:D_SOD-123',

        tfu.Path.empty().append_block('reg_bbl').append_block('out_cap').append_block('cap').append_param('footprint_name'): 'Capacitor_SMD:C_1206_3216Metric',
        tfu.Path.empty().append_block('reg_bbl').append_block('out_cap').append_block('cap').append_param('single_nominal_capacitance'): (0.0, 10e-6),
        tfu.Path.empty().append_block('reg_bbl').append_block('in_cap').append_block('cap').append_param('footprint_name'): 'Capacitor_SMD:C_1206_3216Metric',
        tfu.Path.empty().append_block('reg_bbl').append_block('in_cap').append_block('cap').append_param('single_nominal_capacitance'): (0.0, 10e-6),

        tfu.Path.empty().append_block('reg_srv').append_block('out_cap').append_block('cap').append_param('footprint_name'): 'Capacitor_SMD:C_1206_3216Metric',
        tfu.Path.empty().append_block('reg_srv').append_block('out_cap').append_block('cap').append_param('single_nominal_capacitance'): (0.0, 10e-6),
        tfu.Path.empty().append_block('reg_srv').append_block('in_cap').append_block('cap').append_param('footprint_name'): 'Capacitor_SMD:C_1206_3216Metric',
        tfu.Path.empty().append_block('reg_srv').append_block('in_cap').append_block('cap').append_param('single_nominal_capacitance'): (0.0, 10e-6),
      }
    )
