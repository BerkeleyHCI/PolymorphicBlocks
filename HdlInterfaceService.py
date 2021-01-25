from typing import  Generator

import grpc  # type: ignore
from concurrent import futures

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
  server.start()
  server.wait_for_termination()
