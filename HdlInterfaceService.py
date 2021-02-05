import grpc  # type: ignore
from concurrent import futures

from edg_core import HdlInterface, edgrpc
from edg_core.HdlInterfaceServer import CachedLibrary


if __name__ == '__main__':
  server = grpc.server(futures.ThreadPoolExecutor(max_workers=1))
  library = CachedLibrary()
  edgrpc.add_HdlInterfaceServicer_to_server(HdlInterface(library, verbose=True), server)  # type: ignore
  server.add_insecure_port('[::]:50051')
  print("started server")
  server.start()
  server.wait_for_termination()
