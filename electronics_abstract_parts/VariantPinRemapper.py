from typing import Dict, List, Union

from electronics_model import CircuitPort


class VariantPinRemapper:
  def __init__(self, mapping: Dict[str, CircuitPort]):
    self.mapping = mapping

  def remap(self, remap: Dict[str, Union[str, List[str]]]) -> Dict[str, CircuitPort]:
    pass
