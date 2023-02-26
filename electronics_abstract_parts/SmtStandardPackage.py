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
  def __init__(self, *, minimum_smd_package: StringLike = ""):
    super().__init__()
    self.minimum_smt_package = self.ArgParameter(minimum_smd_package)
