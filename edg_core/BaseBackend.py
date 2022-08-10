from abc import ABCMeta, abstractmethod
from typing import List, Tuple, Dict

import edgir
import edgrpc


class BaseBackend(metaclass=ABCMeta):
  """Abstract base class for a backend, which takes a compiled design, and returns a list
  of outputs associated with paths.
  Values are the compiler solved values, encoded as a protobuf string since we can't hash proto objects."""
  def run_from_compiler_result(self, result: edgrpc.CompilerResult) -> List[Tuple[edgir.LocalPath, str]]:
    values = {value.path.SerializeToString(): edgir.valuelit_to_lit(value.value)
              for value in result.solvedValues}
    return self.run(result.design, values)

  def run_from_backend_request(self, request: edgrpc.BackendRequest) -> List[Tuple[edgir.LocalPath, str]]:
    values = {value.path.SerializeToString(): edgir.valuelit_to_lit(value.value)
              for value in request.solvedValues}
    return self.run(request.design, values)

  # to be implemented per backend
  @abstractmethod
  def run(self, design: edgir.Design, values: Dict[str, edgir.LitTypes]) -> List[Tuple[edgir.LocalPath, str]]: pass
