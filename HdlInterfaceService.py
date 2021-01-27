import grpc  # type: ignore
from concurrent import futures

from edg_core import HdlInterface, edgrpc


if __name__ == '__main__':
  server = grpc.server(futures.ThreadPoolExecutor(max_workers=1))
  edgrpc.add_HdlInterfaceServicer_to_server(HdlInterface(), server)  # type: ignore
  server.add_insecure_port('[::]:50051')
  print("started server")
  server.start()
  server.wait_for_termination()
