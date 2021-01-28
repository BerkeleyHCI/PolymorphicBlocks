from typing import Iterable, Union
from . import edgrpc
from . import edgir


def makeSolved(path: Iterable[Union[str, 'edgir.ReservedValue']], value: edgir.LitTypes) -> edgrpc.SolvedConstraints.Value:
  from . import edgrpc
  return edgrpc.SolvedConstraints.Value(
    path=edgir.LocalPathList(path), value=edgir.lit_to_valuelit(value)
  )

def designSolvedValues(design: edgir.Design) -> Iterable[edgrpc.SolvedConstraints.Value]:
  solved = edgrpc.SolvedConstraints()
  solved.ParseFromString(design.contents.meta.members.node['solved'].bin_leaf)
  return solved.values
