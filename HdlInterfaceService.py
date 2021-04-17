import grpc  # type: ignore
from concurrent import futures
from edg_core import HdlInterface, edgrpc
from edg_core.HdlInterfaceServer import LibraryElementResolver, RollbackImporter


if __name__ == '__main__':
  server = grpc.server(futures.ThreadPoolExecutor(max_workers=1))
  library = LibraryElementResolver()
  edgrpc.add_HdlInterfaceServicer_to_server(HdlInterface(verbose=True, rollback=RollbackImporter()), server)
  server.add_insecure_port('[::]:50051')
  server.start()
  print("started server")

  server.wait_for_termination()
