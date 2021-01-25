from typing import  Generator, cast

import grpc  # type: ignore
from concurrent import futures

import importlib
import inspect

from edg_core import edgrpc, edgir


class HdlInterface(edgrpc.HdlInterfaceServicer):  # type: ignore
  def LibraryElementsInModule(self, request: edgrpc.ModuleName, context) ->\
          Generator[edgir.LibraryPath, None, None]:
    print(request)
    yield edgir.LibraryPath(target=edgir.LocalStep(name=request.name))

  def GetLibraryElement(self, request: edgir.LibraryPath, context) -> edgir.Library.NS.Val:
    print(request)
    return edgir.Library.NS.Val()

  def ElaborateGenerator(self, request: edgrpc.GeneratorRequest, context) -> edgir.HierarchyBlock:
    print(request)
    return edgir.HierarchyBlock()


if __name__ == '__main__':
  server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
  edgrpc.add_HdlInterfaceServicer_to_server(HdlInterface(), server)  # type: ignore
  server.add_insecure_port('[::]:50051')
  print("started server")
  # server.start()
  # server.wait_for_termination()

  module = importlib.import_module('edg_core')
  module = importlib.import_module('electronics_abstract_parts')
  module = importlib.import_module('edg_core.test_generator')
  module = importlib.import_module('electronics_lib')

  from edg_core import LibraryElement
  from edg_core import Block, Port, Bundle, Link

  for (name, cls) in inspect.getmembers(module):
    if inspect.isclass(cls) and issubclass(cls, LibraryElement)\
            and (cls, 'non_library') not in cls._elt_properties:
      # obj = cast(LibraryElement, cls())
      # obj_name = obj._get_def_name()
      obj_name = cls._static_def_name()
      print(f"{cls} {obj_name}")

