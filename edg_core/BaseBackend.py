from abc import ABCMeta, abstractmethod
from typing import List, Tuple, Dict

import edgir
from edg_core import CompiledDesign


class BaseBackend(metaclass=ABCMeta):
  """Abstract base class for a backend, which takes a compiled design, and returns a list
  of outputs associated with paths."""
  # to be implemented per backend
  @abstractmethod
  def run(self, design: CompiledDesign) -> List[Tuple[edgir.LocalPath, str]]: pass
