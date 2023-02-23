from typing import Optional, Any, Dict, TypeVar, Generic, Callable, Union, List, Tuple
from electronics_model import *


StandardPinningType = TypeVar('StandardPinningType', bound=Block)
PinningFunction = Callable[[StandardPinningType], Dict[str, CircuitPort]]
@non_library
class StandardPinningFootprint(FootprintBlock, Generic[StandardPinningType]):
  """An infrastructural block that provides table to provide standard pin mapping from footprints."""

  FOOTPRINT_PINNING_MAP: Dict[Union[str, Tuple[str, ...]], PinningFunction]  # user-specified
  _EXPANDED_FOOTPRINT_PINNING_MAP: Optional[Dict[str, PinningFunction]] = None  # automatically-generated from above

  def _make_pinning(self, footprint: str) -> Dict[str, CircuitPort]:
    if self.__class__._EXPANDED_FOOTPRINT_PINNING_MAP is None:
      footprint_map = {}
      for pinning_footprints, pinning_fn in self.FOOTPRINT_PINNING_MAP.items():
        if isinstance(pinning_footprints, tuple):
          for pinning_footprint in pinning_footprints:
            assert pinning_footprint not in footprint_map, f"duplicate footprint entry {pinning_footprint}"
            footprint_map[pinning_footprint] = pinning_fn
        elif isinstance(pinning_footprints, str):
          assert pinning_footprints not in footprint_map, f"duplicate footprint entry {pinning_footprint}"
          footprint_map[pinning_footprints] = pinning_fn
        else:
          raise ValueError(f"unknown footprint entry {pinning_footprints}")
      self.__class__._EXPANDED_FOOTPRINT_PINNING_MAP = footprint_map
    return self.__class__._EXPANDED_FOOTPRINT_PINNING_MAP[footprint](self)
