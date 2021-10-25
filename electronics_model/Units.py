from edg_core import *

import math

Farad = LiteralConstructor(1, 'F')
uFarad = LiteralConstructor(1e-6, 'F')
nFarad = LiteralConstructor(1e-9, 'F')
pFarad = LiteralConstructor(1e-12, 'F')

Amp = LiteralConstructor(1, 'A')
mAmp = LiteralConstructor(1e-3, 'A')
uAmp = LiteralConstructor(1e-6, 'A')
nAmp = LiteralConstructor(1e-9, 'A')
pAmp = LiteralConstructor(1e-12, 'A')

Volt = LiteralConstructor(1, 'V')
mVolt = LiteralConstructor(1e-3, 'V')

MOhm = LiteralConstructor(1e6, 'Ω')
kOhm = LiteralConstructor(1e3, 'Ω')
Ohm = LiteralConstructor(1, 'Ω')
mOhm = LiteralConstructor(1e-3, 'Ω')

Henry = LiteralConstructor(1, 'H')
mHenry = LiteralConstructor(1e-3, 'H')
uHenry = LiteralConstructor(1e-6, 'H')

Hertz = LiteralConstructor(1, 'Hz')
kHertz = LiteralConstructor(1e3, 'Hz')
MHertz = LiteralConstructor(1e6, 'Hz')

Second = LiteralConstructor(1, 'S')
nSecond = LiteralConstructor(1e-9, 'S')

Watt = LiteralConstructor(1, 'W')


class UnitUtils:
  PREFIXES_POW3_HIGH = ['k', 'M', 'G', 'T', 'P', 'E', 'Z', 'Y']
  PREFIXES_POW3_LOW = ['m', 'u', 'n', 'p', 'f', 'a', 'z', 'y']

  @classmethod
  def num_to_prefix(cls, num: float, figs: int) -> str:
    if num == 0:
      return '0'
    elif num == -float('inf'):
      return '-inf'
    elif num == float('inf'):
      return 'inf'
    elif num < 0:
      sign = '-'
      num = -num
    else:
      sign = ''

    num_pwr3 = math.floor(math.log10(num) / 3)
    if num_pwr3 < 0:
      prefix_set = cls.PREFIXES_POW3_LOW
      num_pwr3_sign = -1
    else:
      prefix_set = cls.PREFIXES_POW3_HIGH
      num_pwr3_sign = 1
    num_pwr3 *= num_pwr3_sign

    if num_pwr3 > len(prefix_set) + 1:  # clip to top number
      num_pwr3 = len(prefix_set) + 1
    if num_pwr3 == 0:
      prefix = ''
    else:
      prefix = prefix_set[num_pwr3 - 1]

    num_prefix = num * 10**(-1 * num_pwr3_sign * num_pwr3 * 3)
    return f"{sign}{num_prefix:0.{figs}g}{prefix}"
