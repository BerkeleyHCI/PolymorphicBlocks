from typing import List, Optional, Dict

from electronics_abstract_parts import PartsTableFootprintSelector, PartsTableRow
from electronics_model import *

@abstract_block
class SmdStandardPackage(InternalBlock, Block):
  """A base mixin for any device that can generate into a standard SMT package, the 0402/0603/0805/etc series.
  This provides a parameter that can be globally set to specify a minimum package size.
  Devices may generate into nonstandard packages, those are not affected.
  If this parameter is empty, no minimums are applied.

  Inheriting this class does not provide any behavior, it only adds the minimum parameter.

  For non-generators classes that inherit this, the minimum size should be used as an assertion."""

  PACKAGE_SIZE_ORDER = [  # list of package sizes recognized by this filter
    '01005',
    '0201',
    '0402',
    '0603',
    '0805',
    '1206',
    '1210',
    '1806',
    '1812',
    '2010',
    '2512',
  ]

  @init_in_parent
  def __init__(self, *args, smd_min_package: StringLike = "", **kwargs):
    super().__init__(*args, **kwargs)
    self.smd_min_package = self.ArgParameter(smd_min_package)

  @classmethod
  def get_smd_packages_below(cls, smd_min_package: str, mapping: Dict[str, Optional[str]]) -> List[str]:
    """Returns a list of SMD packages below some specified package size, as a list for an exclusionary filter.
    The mapping must be complete (define entries for all packages), but may map to None to ignore that entry
    (if there is no corresponding footprint)."""
    if not smd_min_package:  # none specified
      return []
    index = cls.PACKAGE_SIZE_ORDER.index(smd_min_package)  # a bad package spec throws a ValueError
    results = cls.PACKAGE_SIZE_ORDER[:index]
    mapped_results = []
    for result in results:
      mapped_result = mapping[result]
      if mapped_result is not None:
        mapped_results.append(mapped_result)
    return mapped_results


@non_library
class SmdStandardPackageSelector(SmdStandardPackage, PartsTableFootprintSelector):
  SMD_FOOTPRINT_MAP: Dict[str, Optional[str]]  # subclass-defined, maps standard packages (e.g., 0402) to footprints

  def __init__(self, *args, **kwargs):
    super().__init__(*args, **kwargs)
    self.generator_param(self.smd_min_package)

  def _row_filter(self, row: PartsTableRow) -> bool:
    minimum_invalid_footprints = SmdStandardPackage.get_smd_packages_below(  # TODO optimize to not run for every row
      self.get(self.smd_min_package), self.SMD_FOOTPRINT_MAP)
    return super()._row_filter(row) and \
      (row[self.KICAD_FOOTPRINT] not in minimum_invalid_footprints)
