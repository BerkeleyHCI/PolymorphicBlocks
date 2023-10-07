from __future__ import annotations

import re
from typing import TypeVar, Type, overload, Union, Tuple, Optional


class PartParserUtil:
  """Collection of utilities for parsing part values, eg for reading in schematics
  or for parsing part tables."""

  class ParseError(Exception):
    pass

  SI_PREFIX_DICT = {
    'p': 1e-12,
    'n': 1e-9,
    'μ': 1e-6,
    'µ': 1e-6,
    'u': 1e-6,
    'm': 1e-3,
    'k': 1e3,
    'M': 1e6,
    'G': 1e9,
  }
  SI_PREFIXES = ''.join(SI_PREFIX_DICT.keys())

  VALUE_REGEX = re.compile(f'^([\d./]+)\s*([{SI_PREFIXES}]?)(.*)$')
  DefaultType = TypeVar('DefaultType')
  @classmethod
  def parse_value(cls, value: str, units: str) -> float:
    """Parses a value with unit and SI prefixes, for example '20 nF' would be parsed as 20e-9.
    Supports inline prefix notation (eg, 2k2R) and fractional notation (eg, 1/16W)
    If the input is not a value:
      if default is not specified, raises a ParseError.
      if default is specified, returns the default."""
    value = value.strip()
    # validate units
    if not value.endswith(units):
      raise cls.ParseError(f"'{value}' does not have expected units '{units}'")
    value = value.removesuffix(units)
    # do not re-strip here, prefix must directly precede units
    prefix: Optional[str] = None
    if value[-1] in cls.SI_PREFIX_DICT.keys():
      prefix = value[-1]
      value = value[:-1]
    value = value.strip()  # allow a space between the value and prefix + units

    # at this point, only the numeric part remains (possibly with inline prefix, like 2k2)
    if '/' in value:  # fractional case
      fractional_components = value.split('/')
      if len(fractional_components) != 2:
        raise cls.ParseError(f"'{value}' has invalid fractional format")
      try:
        numeric_value = float(fractional_components[0]) / float(fractional_components[1])
      except ValueError:
        raise cls.ParseError(f"'{value}' is not a valid fraction")
    else:  # numeric case, possibly with inline prefix
      if value.isnumeric():
        numeric_value = float(value)
      else:  # check for inline prefix
        for test_prefix in cls.SI_PREFIX_DICT.keys():
          if test_prefix in value:
            value = value.replace(test_prefix, '.', 1)  # only replace the first one
            if prefix is not None:
              raise cls.ParseError(f"'{value}' contains multiple SI prefixes")
            prefix = test_prefix
        try:
          numeric_value = float(value)
        except ValueError:
          raise cls.ParseError(f"'{value}' is not numeric")
    if prefix is not None:
      return numeric_value * cls.SI_PREFIX_DICT[prefix]
    else:
      return numeric_value

  TOLERANCE_REGEX = re.compile(f'^(±)?\s*([\d.]+)\s*(ppm|%)$')
  @classmethod
  def parse_tolerance(cls, value: str) -> Tuple[float, float]:
    """Parses a tolerance value and returns the negative and positive tolerance as a tuple of normalized values.
    For example, ±10% would be returned as (-0.1, 0.1)"""
    matches = cls.TOLERANCE_REGEX.match(value)
    if matches is not None:
      if matches.group(1) is None or matches.group(1) == '±':  # only support the ± case right now
        if matches.group(3) == '%':
          scale = 1.0/100
        elif matches.group(3) == 'ppm':
          scale = 1e-6
        else:
          raise cls.ParseError(f"Cannot determine tolerance scale from '{value}'")
        parsed = float(matches.group(2))
        return -parsed * scale, parsed * scale
      else:
        raise cls.ParseError(f"Cannot determine tolerance type from '{value}'")
    else:
      raise cls.ParseError(f"Cannot parse tolerance from '{value}'")

  @classmethod
  def parse_tolerance_absolute(cls, value: str, center: float, units: str) -> Tuple[float, float]:
    """Parses a tolerance value and returns the negative and positive tolerance as a tuple of absolute values.
    String may not have leading or trailing whitespace, but may have whitespace between parts."""
    if value.startswith('±'):
      value = value.removeprefix('±')
    else:
      raise cls.ParseError(f"Unknown prefix for tolerance '{value}'")

    if value.endswith('%'):
      value = value.removesuffix('%').rstrip()
      tol = float(value) / 100 * center
      return (-tol, tol)
    elif value.endswith('ppm'):
      value = value.removesuffix('ppm').rstrip()
      tol = float(value) * 1e-6 * center
      return (-tol, tol)
    elif value.endswith(units):
      tol = cls.parse_value(value, units)
      return (-tol, tol)
    else:
      raise cls.ParseError(f"Unknown tolerance '{value}'")
