from typing import *
from .HierarchyBlock import Block
from . import edgir, edgrpc


class Refinements(NamedTuple):
  class_refinements: Iterable[Tuple[Type[Block], Type[Block]]] = []
  instance_refinements: Iterable[Tuple[Iterable[str], Type[Block]]] = []
  class_values: Iterable[Tuple[Type[Block], Iterable[str], edgir.LitTypes]] = []
  instance_values: Iterable[Tuple[Iterable[str], edgir.LitTypes]] = []

  def populate_compiler_request(self, pb: edgrpc.CompilerRequest) -> edgrpc.CompilerRequest:
    # TODO: this doesn't dedup refinement. Is this desired?
    for (src_cls, target_cls) in self.class_refinements:
      ref_entry = pb.refinements.add()
      ref_entry.cls.target.name = src_cls._static_def_name()
      ref_entry.replacement.target.name = target_cls._static_def_name()

    for (src_path, target_cls) in self.instance_refinements:
      ref_entry = pb.refinements.add()
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
