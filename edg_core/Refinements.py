from __future__ import annotations

from typing import *
from itertools import chain
from .HierarchyBlock import Block
import edgir
from . import edgrpc


class Refinements():
  def __init__(self, class_refinements: Iterable[Tuple[Type[Block], Type[Block]]] = [],
               instance_refinements: Iterable[Tuple[Iterable[str], Type[Block]]] = [],
               class_values: Iterable[Tuple[Type[Block], Iterable[str], edgir.LitTypes]] = [],
               instance_values: Iterable[Tuple[Iterable[str], edgir.LitTypes]] = []):
    self.class_refinements = class_refinements
    self.instance_refinements = instance_refinements
    self.class_values = class_values
    self.instance_values = instance_values

  def populate_proto(self, pb: edgrpc.Refinements) -> edgrpc.Refinements:
    # TODO: this doesn't dedup refinement. Is this desired?
    # TODO explicit dedup and prioritization
    # TODO some kind of override annotation?
    for (src_cls, target_cls) in self.class_refinements:
      ref_entry = pb.subclasses.add()
      ref_entry.cls.target.name = src_cls._static_def_name()
      ref_entry.replacement.target.name = target_cls._static_def_name()

    for (src_path, target_cls) in self.instance_refinements:
      ref_entry = pb.subclasses.add()
      ref_entry.path.CopyFrom(edgir.LocalPathList(src_path))
      ref_entry.replacement.target.name = target_cls._static_def_name()

    for (src_cls, target_subpath, target_value) in self.class_values:
      val_entry = pb.values.add()
      val_entry.cls_param.cls.target.name = src_cls._static_def_name()
      val_entry.cls_param.param_path.CopyFrom(edgir.LocalPathList(target_subpath))
      val_entry.value.CopyFrom(edgir.lit_to_valuelit(target_value))

    for (src_path, target_value) in self.instance_values:
      val_entry = pb.values.add()
      val_entry.path.CopyFrom(edgir.LocalPathList(src_path))
      val_entry.value.CopyFrom(edgir.lit_to_valuelit(target_value))

    return pb

  def __add__(self, rhs: Refinements) -> Refinements:
    return Refinements(
      class_refinements=list(chain(self.class_refinements, rhs.class_refinements)),
      instance_refinements=list(chain(self.instance_refinements, rhs.instance_refinements)),
      class_values=list(chain(self.class_values, rhs.class_values)),
      instance_values=list(chain(self.instance_values, rhs.instance_values)),
    )
