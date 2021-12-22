from typing import Iterable

from .Core import StructuredMetadata, Refable
from .IdentityDict import IdentityDict
import edgir

class MetaNamespaceOrder(StructuredMetadata):
  def __init__(self):
    self.order = []

  def append(self, elt: str):
    self.order.append(elt)

  def extend(self, elts: Iterable[str]):
    self.order.extend(elts)

  def _to_proto(self, ref_map: IdentityDict[Refable, edgir.LocalPath]) -> edgir.Metadata:
    pb = edgir.Metadata()
    for name in self.order:
      pb.namespace_order.names.append(name)
    return pb
