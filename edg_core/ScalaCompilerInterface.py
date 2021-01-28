from typing import Optional, Any, Type

import os
import grpc  # type: ignore
from concurrent import futures
import subprocess

from . import edgir, edgrpc
from .HierarchyBlock import Block
from .HdlInterfaceServer import HdlInterface, CachedLibrary


class ScalaCompilerInstance:
  RELATIVE_PATH = "compiler/target/scala-2.13/edg-compiler-assembly-0.1-SNAPSHOT.jar"

  def __init__(self):
    self.server: Optional[Any] = None
    self.library = CachedLibrary()  # TODO should this be instance-specific?

  def check_server_started(self) -> Any:
    if self.server is None:
      self.server = grpc.server(futures.ThreadPoolExecutor(max_workers=1))
      edgrpc.add_HdlInterfaceServicer_to_server(HdlInterface(self.library), self.server)  # type: ignore
      self.server.add_insecure_port('[::]:50051')
      self.server.start()
    return self.server

  def compile(self, block: Type[Block]) -> edgir.Design:
    self.check_server_started()

    # TODO perhaps make compiler process persistent
    if os.path.exists(self.RELATIVE_PATH):
      jar_path = self.RELATIVE_PATH
      print("Using development JAR")
    else:
      raise ValueError("No EDG Compiler JAR found")

    block_name = block._static_def_name()
    block_modules = block.__module__

    process = subprocess.Popen(
      ['java', '-jar', jar_path, str(block_modules), block_name],
      stdin=subprocess.PIPE,
      stdout=subprocess.PIPE)
    out, errs = process.communicate()

    design = edgir.Design()
    design.ParseFromString(out)
    return design

  def close(self):
    assert self.server is not None
    self.server.stop()
    self.server.wait_for_termination()  # is this needed?
    self.server = None


ScalaCompiler = ScalaCompilerInstance()
