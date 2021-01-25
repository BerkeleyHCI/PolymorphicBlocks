import grpc  # type: ignore
from concurrent import futures

from . import edgrpc


class HdlInterface(edgrpc.HdlInterfaceServicer):  # type: ignore
  def LibraryElementsInModule(self, request, context):
    pass

  def GetLibraryElement(self, request, context):
    pass

  def ElaborateGenerator(self, request, context):
    pass


if __name__ == '__main__':
  server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
  edgrpc.add_HdlInterfaceServicer_to_server(HdlInterface(), server)  # type: ignore
  server.add_insecure_port('[::]:50051')
  server.start()
  server.wait_for_termination()
