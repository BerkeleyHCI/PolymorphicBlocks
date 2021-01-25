import grpc
from concurrent import futures

import edgrpc


class HdlInterface(edgrpc.HdlInterfaceServicer):
  def LibraryElementsInModule(self):
    pass

  def GetLibraryElement(self):
    pass

  def ElaborateGenerator(self):
    pass


if __name__ == '__main__':
  server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
  edgrpc.add_HdlInterfaceServicer_to_server(HdlInterface(), server)
  server.add_insecure_port('[::]:50051')
  server.start()
  server.wait_for_termination()
