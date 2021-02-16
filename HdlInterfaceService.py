import grpc  # type: ignore
from concurrent import futures
from edg_core import HdlInterface, edgrpc, edgir
from edg_core.HdlInterfaceServer import LibraryElementResolver, RollbackImporter


if __name__ == '__main__':
  # hdl_interface = HdlInterface(verbose=True, rollback=RollbackImporter())
  #
  # test = [x for x in hdl_interface.ReloadModule(edgrpc.ModuleName(name="examples.test_blinky"), None)]
  #
  # hdl_interface.GetLibraryElement(
  #   edgrpc.LibraryRequest(element=edgir.LibraryPath(target=edgir.LocalStep(name="examples.test_blinky.TestBlinkySimple"))),
  #   None)
  #
  # test = [x for x in hdl_interface.ReloadModule(edgrpc.ModuleName(name="examples.test_blinky"), None)]

  server = grpc.server(futures.ThreadPoolExecutor(max_workers=1))
  library = LibraryElementResolver()
  # hdl_interface =
  edgrpc.add_HdlInterfaceServicer_to_server(HdlInterface(verbose=True, rollback=RollbackImporter()), server)
  server.add_insecure_port('[::]:50051')
  server.start()

  print("started server")

  server.wait_for_termination()
