from typing import Optional, Any, Type

import os
import grpc  # type: ignore
from concurrent import futures
import subprocess

from . import edgir, edgrpc
from .HierarchyBlock import Block
from .HdlInterfaceServer import HdlInterface, CachedLibrary


class ScalaCompiler:
  RELATIVE_PATH = "compiler/target/scala-2.13/edg-compiler-assembly-0.1-SNAPSHOT.jar"
  library = CachedLibrary()  # TODO should this be instance-specific?

  def __init__(self):
    self.server: Optional[Any] = grpc.server(futures.ThreadPoolExecutor(max_workers=1))
    edgrpc.add_HdlInterfaceServicer_to_server(HdlInterface(self.library), self.server)  # type: ignore
    self.server.add_insecure_port('[::]:50051')
    self.server.start()
    print("started server")

  def compile(self, block: Type[Block]) -> edgir.Design:
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
      shell=True,  # apparently makes it possible for py4j to open the socket w/ subprocess?!
      stdin=subprocess.PIPE,
      stdout=subprocess.PIPE)
    # assert process.stdout is not None
    # output = cls.elk_process.stdout.readline().decode('utf-8')
    out, errs = process.communicate()
    print(out)

    raise NotImplementedError

  def close(self):
    assert self.server is not None
    self.server.stop()
    self.server.wait_for_termination()  # is this needed?
    self.server = None
