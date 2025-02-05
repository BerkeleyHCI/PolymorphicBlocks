from typing import Optional, Any, Type, Iterable, Union, Dict, List, Tuple

import os
import subprocess
import sys

from .. import edgir
from .. import edgrpc
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
    return CompiledDesign(result.design, values, list(result.errors))

  @staticmethod
  def from_request(design: edgir.Design, values: Iterable[edgrpc.ExprValue]) -> 'CompiledDesign':
    values_dict = {value.path.SerializeToString(): edgir.valuelit_to_lit(value.value)
                   for value in values}
    return CompiledDesign(design, values_dict, [])

  def __init__(self, design: edgir.Design, values: Dict[bytes, edgir.LitTypes], errors: List[edgrpc.ErrorRecord]):
    self.design = design
    self.contents = design.contents  # convenience accessor
    self.errors = errors
    self._values = values

  def errors_str(self) -> str:
    err_strs = []
    for error in self.errors:
      error_pathname = edgir.local_path_to_str(error.path)
      if error.name:
        error_pathname += ':' + error.name
      err_strs.append(f"{error.kind} @ {error_pathname}: {error.details}")
    return '\n'.join([f'- {err_str}' for err_str in err_strs])

  # Reserved.V is a string because it doesn't load properly at runtime
  # Serialized strings are used since proto objects are mutable and unhashable
  def get_value(self, path: Union[edgir.LocalPath, Iterable[Union[str, 'edgir.Reserved.V']]]) ->\
          Optional[edgir.LitTypes]:
    if isinstance(path, edgir.LocalPath):
      localpath = path
    else:
      localpath = edgir.LocalPathList(path)
    return self._values.get(localpath.SerializeToString(), None)

  def append_values(self, values: List[Tuple[edgir.LocalPath, edgir.ValueLit]]):
    """Append solved values to this design, such as from a refinement pass"""
    for (value_path, value_value) in values:
      value_path_str = value_path.SerializeToString()
      assert value_path_str not in self._values
      self._values[value_path_str] = edgir.valuelit_to_lit(value_value)


class ScalaCompilerInstance:
  kDevRelpath = "../../compiler/target/scala-2.13/edg-compiler-assembly-0.1-SNAPSHOT.jar"
  kPrecompiledRelpath = "resources/edg-compiler-precompiled.jar"

  def __init__(self):
    self.process: Optional[Any] = None

  def check_started(self) -> None:
    if self.process is None:
      dev_path = os.path.join(os.path.dirname(__file__), self.kDevRelpath)
      precompiled_path = os.path.join(os.path.dirname(__file__), self.kPrecompiledRelpath)
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
        stderr=subprocess.PIPE
      )

  def compile(self, block: Type[Block], refinements: Refinements = Refinements(), *,
              ignore_errors: bool = False) -> CompiledDesign:
    from ..hdl_server.__main__ import process_request
    self.check_started()

    assert self.process is not None
    assert self.process.stdin is not None
    assert self.process.stdout is not None
    request_serializer = BufferSerializer[edgrpc.CompilerRequest](self.process.stdin)

    block_obj = block()
    request = edgrpc.CompilerRequest(
      design=edgir.Design(
        contents=builder.elaborate_toplevel(block_obj))
    )
    if isinstance(block_obj, DesignTop):
      refinements = block_obj.refinements() + refinements
    refinements.populate_proto(request.refinements)

    # write the initial request to the compiler process
    request_serializer.write(request)

    # until the compiler gives back the response, this acts as the HDL server,
    # taking requests in the opposite direction
    assert self.process.stdin is not None
    assert self.process.stdout is not None
    hdl_request_deserializer = BufferDeserializer(edgrpc.HdlRequest, self.process.stdout)
    hdl_response_serializer = BufferSerializer[edgrpc.HdlResponse](self.process.stdin)
    while True:
      sys.stdout.buffer.write(hdl_request_deserializer.read_stdout())
      sys.stdout.buffer.flush()
      hdl_request = hdl_request_deserializer.read()
      assert hdl_request is not None
      hdl_response = process_request(hdl_request)
      if hdl_response is None:
        break
      hdl_response_serializer.write(hdl_response)

    response_deserializer = BufferDeserializer(edgrpc.CompilerResult, self.process.stdout)
    result = response_deserializer.read()

    sys.stdout.buffer.write(response_deserializer.read_stdout())
    sys.stdout.buffer.flush()

    assert result is not None
    assert result.HasField('design')
    design = CompiledDesign.from_compiler_result(result)
    if result.errors and not ignore_errors:
      raise CompilerCheckError(f"error during compilation:\n{design.errors_str()}")
    return design

  def close(self):
    assert self.process is not None
    self.process.stdin.close()
    self.process.stdout.close()
    self.process.stderr.close()
    self.process.wait()


ScalaCompiler = ScalaCompilerInstance()
