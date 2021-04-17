from typing import *
from electronics_abstract_parts import *


class Nhd_312_25664uc_Device(DiscreteChip, FootprintBlock):
  def __init__(self) -> None:
    super().__init__()

    self.vdd = self.Port(VoltageSink(
      voltage_limits=(3*0.95, 3.3) * Volt,  # Chapter 5, no minimum given, assuming a -5% tolerance
      current_draw=(0.003, 290) * mAmp  # Chapter 5, typ sleep current to 100% brightness at 3v
    ))
    self.vss = self.Port(Ground())

    io_model = DigitalBidir.from_supply(
      self.vss, self.vdd,
      voltage_limit_tolerance=(-0.3, 0.3)*Volt,  # not stated, assumed
      current_draw=0*mAmp(tol=0),  # not stated, assumed
      current_limits=0*mAmp(tol=0),  # not stated, assumed
      input_threshold_factor=(0.2, 0.8),
      output_threshold_factor=(0.1, 0.9)
    )
    self.dc = self.Port(DigitalSink(io_model))
    self.sclk = self.Port(DigitalSink(io_model))
    self.sdin = self.Port(DigitalSink(io_model))

    self.nres = self.Port(DigitalSink(io_model))
    self.ncs = self.Port(DigitalSink(io_model))

  def contents(self):
    super().contents()

    pinning: Dict[str, CircuitPort] = {
      '1': self.vss,
      '2': self.vdd,
      # '3':  # no connect
      '4': self.dc,
      '5': self.vss,  # R/nW in parallel interface
      '6': self.vss,  # E/nRD in parallel interface
      '7': self.sclk,
      '8': self.sdin,
      # '9'  # no connect  # DB2 in parallel interface
      '10': self.vss,  # DB3 in parallel interface
      '11': self.vss,  # DB4 in parallel interface
      '12': self.vss,  # DB5 in parallel interface
      '13': self.vss,  # DB6 in parallel interface
      '14': self.vss,  # DB7 in parallel interface
      # '15':  # no connect
      '16': self.nres,
      '17': self.ncs,
      # '18':  # no connect
      '19': self.vss,  # BS1 parallel (1) / serial (0) mode
      '20': self.vss,  # BS0 4-wire serial mode
    }

    self.footprint(
      'U', 'calisco:NHD-3.12-25664UCB2',
      pinning,
      part='20-pin header, NHD-3.12-25664UCB2'  # TODO multiple parts
    )


class Nhd_312_25664uc(Oled, Block):
  """256x64 3.12" passive-matrix OLED"""
  def __init__(self) -> None:
    super().__init__()

    self.device = self.Block(Nhd_312_25664uc_Device())
    self.gnd = self.Export(self.device.vss, [Common])
    self.pwr = self.Export(self.device.vdd, [Power])
    self.reset = self.Export(self.device.nres)
    self.dc = self.Export(self.device.dc)
    self.cs = self.Export(self.device.ncs)
    self.spi = self.Port(SpiSlave())

  def contents(self):
    super().contents()

    self.connect(self.spi.sck, self.device.sclk)
    self.connect(self.spi.mosi, self.device.sdin)
