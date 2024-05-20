from abc import ABCMeta, abstractmethod
from typing import List, Tuple

from .. import edgir
from .ScalaCompilerInterface import CompiledDesign


class BaseRefinementPass(metaclass=ABCMeta):
  """Abstract base class for a refinement pass, which takes a compiled design, and returns a list
  of additional solved values to be added."""
  # to be implemented per backend
  @abstractmethod
  def run(self, design: CompiledDesign) -> List[Tuple[edgir.LocalPath, edgir.ValueLit]]: pass
