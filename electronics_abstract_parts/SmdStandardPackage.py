from typing import List, Optional, Dict

from electronics_model import *

@abstract_block
class SmdStandardPackage(Block):
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
  def __init__(self, *args, minimum_smd_package: StringLike = "", **kwargs):
    super().__init__(*args, **kwargs)
    self.minimum_smd_package = self.ArgParameter(minimum_smd_package)

  @classmethod
  def get_smd_packages_below(cls, minimum_smd_package: str, mapping: Optional[Dict[str, Optional[str]]] = None) -> List[str]:
    """Returns a list of SMD packages below some specified package size, as a list for an exclusionary filter.
    The mapping must be complete (define entries for all packages), but may map to None to ignore that entry
    (if there is no corresponding footprint)."""
    if not minimum_smd_package:  # none specified
      return []
    index = cls.PACKAGE_SIZE_ORDER.index(minimum_smd_package)  # a bad package spec throws a ValueError
    results = cls.PACKAGE_SIZE_ORDER[:index]
    if mapping is not None:
      mapped_results = []
      for result in results:
        mapped_result = mapping[result]
        if mapped_result is not None:
          mapped_results.append(mapped_result)
      return mapped_results
    else:
      return results
