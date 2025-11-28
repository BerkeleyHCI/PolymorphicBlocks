from abc import abstractmethod
from typing import List, Tuple, Dict

from .. import edgir
from .ScalaCompilerInterface import CompiledDesign


class BaseBackend:
  """Abstract base class for a backend, which takes a compiled design, and returns a list
  of outputs associated with paths."""
  # to be implemented per backend
  @abstractmethod
  def run(self, design: CompiledDesign, args: Dict[str, str] = {}) -> List[Tuple[edgir.LocalPath, str]]:
    raise NotImplementedError()
