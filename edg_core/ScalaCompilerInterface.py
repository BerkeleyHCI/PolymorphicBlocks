from typing import Optional, Any, Type, Iterable, Union, Dict, List, Tuple

import os
import subprocess
import sys

import edgir
import edgrpc
from .BufferSerializer import BufferSerializer, BufferDeserializer
from .Core import builder
from .HierarchyBlock import Block
from .DesignTop import DesignTop
from .Refinements import Refinements


class CompilerCheckError(BaseException):
  pass


class CompiledDesign:
  @staticmethod
  def from_compiler_result(result: edgrpc.CompilerResult) -> 'CompiledDesign':
    values = {value.path.SerializeToString(): edgir.valuelit_to_lit(value.value)
              for value in result.solvedValues}
    return CompiledDesign(result.design, values, result.error)

  @staticmethod
  def from_request(design: edgir.Design, values: Iterable[edgrpc.ExprValue]) -> 'CompiledDesign':
    values_dict = {value.path.SerializeToString(): edgir.valuelit_to_lit(value.value)
                   for value in values}
    return CompiledDesign(design, values_dict, "")

  def __init__(self, design: edgir.Design, values: Dict[bytes, edgir.LitTypes], error: str):
    self.design = design
    self.contents = design.contents  # convenience accessor
    self.error = error
    self._values = values

  # Reserved.V is a string because it doesn't load properly at runtime
  # Serialized strings are used since proto objects are mutable and unhashable
  def get_value(self, path: Iterable[Union[str, 'edgir.Reserved.V']]) -> Optional[edgir.LitTypes]:
    path_key = edgir.LocalPathList(path).SerializeToString()
    return self._values.get(path_key, None)

  def append_values(self, values: List[Tuple[edgir.LocalPath, edgir.ValueLit]]):
    """Append solved values to this design, such as from a refinement pass"""
    for (value_path, value_value) in values:
      value_path_str = value_path.SerializeToString()
      assert value_path_str not in self._values
      self._values[value_path_str] = edgir.valuelit_to_lit(value_value)


class ScalaCompilerInstance:
  DEV_RELPATH = "../compiler/target/scala-2.13/edg-compiler-assembly-0.1-SNAPSHOT.jar"
  PRECOMPIED_RELPATH = "resources/edg-compiler-precompiled.jar"

  def __init__(self, *, suppress_stderr: bool = False):
    self.process: Optional[Any] = None
    self.suppress_stderr = suppress_stderr
    self.request_serializer: Optional[BufferSerializer[edgrpc.CompilerRequest]] = None
    self.response_deserializer: Optional[BufferDeserializer[edgrpc.CompilerResult]] = None

  def check_started(self) -> None:
    if self.process is None:
      dev_path = os.path.join(os.path.dirname(__file__), self.DEV_RELPATH)
      precompiled_path = os.path.join(os.path.dirname(__file__), self.PRECOMPIED_RELPATH)
      if os.path.exists(dev_path):
        jar_path = dev_path
        print("Using development JAR")
      elif os.path.exists(precompiled_path):
        jar_path = precompiled_path
      else:
        raise ValueError(f"No EDG Compiler JAR found")

      self.process = subprocess.Popen(
        ['java', '-jar', jar_path],
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE if self.suppress_stderr else None
      )

      assert self.process.stdin is not None
      self.request_serializer = BufferSerializer[edgrpc.CompilerRequest](self.process.stdin)
      assert self.process.stdout is not None
      self.response_deserializer = BufferDeserializer(edgrpc.CompilerResult, self.process.stdout)

  def compile(self, block: Type[Block], refinements: Refinements = Refinements(), *,
              ignore_errors: bool = False) -> CompiledDesign:
    self.check_started()
    assert self.request_serializer is not None
    assert self.response_deserializer is not None

    block_obj = block()
    request = edgrpc.CompilerRequest(
      design=edgir.Design(
        contents=builder.elaborate_toplevel(block_obj))
    )
    if isinstance(block_obj, DesignTop):
      refinements = block_obj.refinements() + refinements

    refinements.populate_proto(request.refinements)

    self.request_serializer.write(request)
    result = self.response_deserializer.read()

    sys.stdout.buffer.write(self.response_deserializer.read_stdout())
    sys.stdout.buffer.flush()

    assert result is not None
    assert result.HasField('design')
    if result.error and not ignore_errors:
      raise CompilerCheckError(f"error during compilation: \n{result.error}")
    return CompiledDesign.from_compiler_result(result)

  def close(self):
    assert self.process is not None
    self.process.stdin.close()
    self.process.stdout.close()
    if self.suppress_stderr:
      self.process.stderr.close()
    self.process.wait()


ScalaCompiler = ScalaCompilerInstance()
