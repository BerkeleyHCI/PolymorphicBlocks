import sys

from edg_core import HdlInterface, edgrpc
from edg_core.HdlInterfaceServer import RollbackImporter
from edg_core import BufferDeserializer, BufferSerializer


if __name__ == '__main__':
  verbose = True

  server = HdlInterface(rollback=RollbackImporter())
  stdin_deserializer = BufferDeserializer(edgrpc.HdlRequest, sys.stdin.buffer)
  stdout_serializer = BufferSerializer[edgrpc.HdlResponse](sys.stdout.buffer)

  while True:
    request = stdin_deserializer.read()
    response = edgrpc.HdlResponse()
    if request.HasField('reload_module'):
      if verbose:
        print(f"ReloadModule({request.reload_module.name}) -> ", end='', flush=True)
      indexed = server.ReloadModule(request.reload_module)
      if verbose:
        print(f"(Indexed {len(indexed)})", flush=True)
      response.reload_module.indexed.extend(indexed)
    elif request.HasField('get_library_element'):
      if verbose:
        print(f"GetLibraryElement({request.get_library_element.element.target.name}) -> ", end='', flush=True)
      lib = server.GetLibraryElement(request.get_library_element)
      if verbose:
        if lib.HasField('error'):
          print(f"Error {lib.error}", flush=True)
        elif lib.HasField('refinements'):
          print(f"(elt, w/ refinements)", flush=True)
        else:
          print(f"(elt)", flush=True)
      response.get_library_element.CopyFrom(lib)
    elif request.HasField('elaborate_generator'):
      if verbose:
        print(f"ElaborateGenerator({request.elaborate_generator.element.target.name}) -> ", end='', flush=True)
      gen = server.ElaborateGenerator(request.elaborate_generator)
      if verbose:
        if gen.HasField('error'):
          print(f"Error {gen.error}", flush=True)
        else:
          print(f"(generated)", flush=True)
      response.elaborate_generator.CopyFrom(gen)
    else:
      print(f"Unknown request {response}")

    stdout_serializer.write(response)
