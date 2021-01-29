from typing import Iterable, Union
from . import edgrpc
from . import edgir


def makeSolved(path: Iterable[Union[str, 'edgir.ReservedValue']], value: edgir.LitTypes) -> edgrpc.CompilerResult.Value:
  from . import edgrpc
  return edgrpc.CompilerResult.Value(
    path=edgir.LocalPathList(path), value=edgir.lit_to_valuelit(value)
  )


def designSolvedValues(compiled: edgrpc.CompilerResult) -> Iterable[edgrpc.CompilerResult.Value]:
  return compiled.solvedValues
