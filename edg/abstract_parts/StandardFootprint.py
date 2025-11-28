from typing import Optional, Dict, TypeVar, Generic, Callable, Union, Tuple, ClassVar, Type
from typing_extensions import Self

from ..electronics_model import *


StandardPinningType = TypeVar('StandardPinningType', bound=Block)
PinningFunction = Callable[[StandardPinningType], Dict[str, CircuitPort]]
class StandardFootprint(Generic[StandardPinningType]):
  """A shared helper class that provides a table to provide standard pin mapping from footprints."""
  REFDES_PREFIX: ClassVar[str]
  FOOTPRINT_PINNING_MAP: ClassVar[Dict[Union[str, Tuple[str, ...]], PinningFunction[StandardPinningType]]]  # user-specified
  _EXPANDED_FOOTPRINT_PINNING_MAP: Optional[Dict[str, PinningFunction[StandardPinningType]]] = None  # automatically-generated from above

  @classmethod
  def _footprint_pinning_map(cls) -> Dict[str, PinningFunction[StandardPinningType]]:
    """Returns the footprint pinning map as a dict of footprint name -> pinning fn, generating and caching the
    expanded table as needed"""
    if cls._EXPANDED_FOOTPRINT_PINNING_MAP is None:
      footprint_map = {}
      for pinning_footprints, pinning_fn in cls.FOOTPRINT_PINNING_MAP.items():
        if isinstance(pinning_footprints, tuple):
          for pinning_footprint in pinning_footprints:
            assert pinning_footprint not in footprint_map, f"duplicate footprint entry {pinning_footprint}"
            footprint_map[pinning_footprint] = pinning_fn
        elif isinstance(pinning_footprints, str):
          assert pinning_footprints not in footprint_map, f"duplicate footprint entry {pinning_footprint}"
          footprint_map[pinning_footprints] = pinning_fn
        else:
          raise ValueError(f"unknown footprint entry {pinning_footprints}")
      cls._EXPANDED_FOOTPRINT_PINNING_MAP = footprint_map
    return cls._EXPANDED_FOOTPRINT_PINNING_MAP

  @classmethod
  def _make_pinning(cls, block: StandardPinningType, footprint: str) -> Dict[str, CircuitPort]:
    """Returns the pinning for a footprint for a specific block's pins"""
    return cls._footprint_pinning_map()[footprint](block)


@non_library
class HasStandardFootprint(Block):
  """Base class that defines that a class supports a StandardFootprint"""
  # the footprint can be a lambda to allow the pinning to be defined after
  _STANDARD_FOOTPRINT: ClassVar[Union[Type[StandardFootprint[Self]],
                                      Callable[[], Type[StandardFootprint[Self]]]]]

  @classmethod
  def _standard_footprint(cls) -> Type[StandardFootprint[Self]]:
    """Returns the StandardFootprint class for this block"""
    if callable(cls._STANDARD_FOOTPRINT):
      return cls._STANDARD_FOOTPRINT()  # type: ignore
    else:
      return cls._STANDARD_FOOTPRINT
