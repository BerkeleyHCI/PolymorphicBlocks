import grpc  # type: ignore
from concurrent import futures

from . import edgrpc, edgir


class HdlInterface(edgrpc.HdlInterfaceServicer):  # type: ignore
  def LibraryElementsInModule(self, request: edgrpc.ModuleName, context) -> None:
    pass

  def GetLibraryElement(self, request: edgir.LibraryPath, context) -> edgir.Library.NS.Val:
    pass

  def ElaborateGenerator(self, request: edgrpc.GeneratorRequest, context) -> edgir.HierarchyBlock:
    pass


if __name__ == '__main__':
  server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
  edgrpc.add_HdlInterfaceServicer_to_server(HdlInterface(), server)  # type: ignore
  server.add_insecure_port('[::]:50051')
  server.start()
  server.wait_for_termination()
