from __future__ import annotations

import re
from typing import TypeVar, Type, overload, Union, Tuple


class PartParserUtil:
  """Collection of utilities for parsing part values, eg for reading in schematics
  or for parsing part tables."""

  class ParseError(Exception):
    pass

  SI_PREFIX_DICT = {
    '': 1,
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

  VALUE_REGEX = re.compile(f'^([\d./]+)\s*([{SI_PREFIXES}]?)(.+)$')
  DefaultType = TypeVar('DefaultType')
  @classmethod
  @overload
  def parse_value(cls, value: str, units: str) -> float: ...
  @classmethod
  @overload
  def parse_value(cls, value: str, units: str, default: DefaultType) -> Union[DefaultType, float]: ...
  @classmethod
  def parse_value(cls, value: str, units: str, default: Union[Type[ParseError], DefaultType] = ParseError) -> Union[DefaultType, float]:
    """Parses a value with unit and SI prefixes, for example '20 nF' would be parsed as 20e-9.
    Additionally supports fractional notation, eg 1/16W
    If the input is not a value:
      if default is not specified, raises a ParseError.
      if default is specified, returns the default."""
    matches = cls.VALUE_REGEX.match(value)
    if matches is not None and matches.group(3) == units:
      try:
        if '/' in matches.group(1):
          fractional_components = matches.group(1).split('/')
          assert len(fractional_components) == 2
          numeric_value = float(fractional_components[0]) / float(fractional_components[1])
        else:
          numeric_value = float(matches.group(1))
        return numeric_value * cls.SI_PREFIX_DICT[matches.group(2)]
      except ValueError:
        raise cls.ParseError(f"Cannot parse units '{units}' from '{value}'")
    else:
      if default == cls.ParseError:
        raise cls.ParseError(f"Cannot parse units '{units}' from '{value}'")
      else:
        return default  # type:ignore

  TOLERANCE_REGEX = re.compile(f'^(±)\s*([\d.]+)\s*(ppm|%)$')
  @classmethod
  def parse_tolerance(cls, value: str) -> Tuple[float, float]:
    """Parses a tolerance value and returns the negative and positive tolerance as a tuple of normalized values.
    For example, ±10% would be returned as (-0.1, 0.1)"""
    matches = cls.TOLERANCE_REGEX.match(value)
    if matches is not None:
      if matches.group(1) == '±':  # only support the ± case right now
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
