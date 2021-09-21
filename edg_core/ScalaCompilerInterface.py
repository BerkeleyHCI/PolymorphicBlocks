from typing import Optional, Any, Type, Iterable, Union

import os
import subprocess

from . import edgir, edgrpc, BufferSerializer, BufferDeserializer
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
  RELATIVE_PATH = "compiler/target/scala-2.13/edg-compiler-assembly-0.1-SNAPSHOT.jar"

  def __init__(self):
    self.process: Optional[Any] = None
    self.request_serializer: Optional[BufferSerializer] = None
    self.response_deserializer: Optional[BufferDeserializer] = None

  def check_started(self) -> None:
    if self.process is None:
      if os.path.exists(self.RELATIVE_PATH):
        jar_path = self.RELATIVE_PATH
        print("Using development JAR")
      else:
        raise ValueError("No EDG Compiler JAR found")

      self.process = subprocess.Popen(
        ['java', '-jar', jar_path],
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE)

      self.request_serializer = BufferSerializer[edgrpc.CompilerRequest](self.process.stdin)
      assert self.process.stdout is not None
      self.response_deserializer = BufferDeserializer(edgrpc.CompilerResult, self.process.stdout)


  def compile(self, block: Type[Block], refinements: Refinements = Refinements(),
              errors_fatal: bool = True) -> CompiledDesign:
    self.check_started()

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

    assert result.HasField('design'), f"no compiled result, with error {result.error}"
    if result.error and errors_fatal:
      raise CompilerCheckError(f"error during compilation: \n{result.error}")
    return CompiledDesign(result)

  def close(self):
    pass


ScalaCompiler = ScalaCompilerInstance()
