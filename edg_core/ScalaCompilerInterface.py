from typing import Optional, Any, Type, Iterable, Union

import os
import subprocess

from . import edgir, edgrpc
from .BufferSerializer import BufferSerializer, BufferDeserializer
from .Core import builder
from .HierarchyBlock import Block
from .DesignTop import DesignTop
from .Refinements import Refinements


class CompilerCheckError(BaseException):
  pass


class CompiledDesign:
  def __init__(self, compiled: edgrpc.CompilerResult):
    self.result = compiled
    self.design = compiled.design
    self.contents = compiled.design.contents
    self.values = {value.path.SerializeToString(): edgir.valuelit_to_lit(value.value)
      for value in compiled.solvedValues}

  def get_value(self, path: Iterable[Union[str, 'edgir.ReservedValue']]) -> Optional[edgir.LitTypes]:
    path_key = edgir.LocalPathList(path).SerializeToString()
    return self.values.get(path_key, None)


class ScalaCompilerInstance:
  PRECOMPIED_RELPATH = "compiler/edg-compiler-precompiled.jar"
  DEV_RELPATH = "compiler/target/scala-2.13/edg-compiler-assembly-0.1-SNAPSHOT.jar"

  def __init__(self):
    self.process: Optional[Any] = None
    self.request_serializer: Optional[BufferSerializer[edgrpc.CompilerRequest]] = None
    self.response_deserializer: Optional[BufferDeserializer[edgrpc.CompilerResult]] = None

  def check_started(self) -> None:
    if self.process is None:
      if os.path.exists(self.DEV_RELPATH):
        jar_path = self.DEV_RELPATH
        print("Using development JAR")
      elif os.path.exists(self.PRECOMPIED_RELPATH):
        jar_path = self.PRECOMPIED_RELPATH
        print("Using precompiled JAR")
      else:
        raise ValueError("No EDG Compiler JAR found")

      self.process = subprocess.Popen(
        ['java', '-jar', jar_path],
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE)

      assert self.process.stdin is not None
      self.request_serializer = BufferSerializer[edgrpc.CompilerRequest](self.process.stdin)
      assert self.process.stdout is not None
      self.response_deserializer = BufferDeserializer(edgrpc.CompilerResult, self.process.stdout)


  def compile(self, block: Type[Block], refinements: Refinements = Refinements(),
              errors_fatal: bool = True) -> CompiledDesign:
    self.check_started()
    assert self.request_serializer is not None
    assert self.response_deserializer is not None

    request = edgrpc.CompilerRequest(
      modules=[block.__module__],
      design=edgir.Design(
        contents=builder.elaborate_toplevel(block(), f"in elaborating top design block {block}"))
    )
    if issubclass(block, DesignTop):  # TODO don't create another instance
      refinements = block().refinements() + refinements

    refinements.populate_proto(request.refinements)

    self.request_serializer.write(request)
    result = self.response_deserializer.read()
    assert result is not None
    assert result.HasField('design'), f"no compiled result, with error {result.error}"
    if result.error and errors_fatal:
      raise CompilerCheckError(f"error during compilation: \n{result.error}")
    return CompiledDesign(result)

  def close(self):
    pass


ScalaCompiler = ScalaCompilerInstance()
