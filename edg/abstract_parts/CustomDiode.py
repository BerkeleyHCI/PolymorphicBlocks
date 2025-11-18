from ..electronics_model import *
from .AbstractDiodes import Diode


class CustomDiode(Diode, FootprintBlock, GeneratorBlock):
  def __init__(self, *args, footprint_spec: StringLike = "",
               manufacturer_spec: StringLike = "", part_spec: StringLike = "", **kwargs):
    super().__init__(*args, **kwargs)
    self.footprint_spec = self.ArgParameter(footprint_spec)  # actual_footprint left to the actual footprint
    self.manufacturer_spec = self.ArgParameter(manufacturer_spec)
    self.part_spec = self.ArgParameter(part_spec)

    self.generator_param(self.footprint_spec)

    # use ideal specs, which can be overridden with refinements
    self.assign(self.actual_voltage_rating, Range.all())
    self.assign(self.actual_current_rating, Range.all())
    self.assign(self.actual_voltage_drop, Range.zero_to_upper(0))
    self.assign(self.actual_reverse_recovery_time, Range.zero_to_upper(0))

  def generate(self) -> None:
    self.footprint(
      self._STANDARD_FOOTPRINT.REFDES_PREFIX, self.footprint_spec,
      self._STANDARD_FOOTPRINT._make_pinning(self, self.get(self.footprint_spec)),
      mfr=self.manufacturer_spec, part=self.part_spec,
      value=self.part_spec,
      datasheet=""
    )
