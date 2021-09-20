import sys

from edg_core import HdlInterface, edgrpc
from edg_core.HdlInterfaceServer import RollbackImporter
from edg_core import BufferDeserializer, BufferSerializer


if __name__ == '__main__':
  verbose = True

  server = HdlInterface(rollback=RollbackImporter())
  stdin_deserializer = BufferDeserializer(edgrpc.HdlRequest, sys.stdin.buffer)
  stdout_serializer = BufferSerializer[edgrpc.HdlResponse](sys.stdout.buffer)

  print(f"HDL Interface Server started",
        flush=True, file=sys.stderr)

  while True:
    request = stdin_deserializer.read()
    response = edgrpc.HdlResponse()
    if request.HasField('reload_module'):
      if verbose:
        print(f"ReloadModule({request.reload_module.name}) -> ", end='',
              flush=True, file=sys.stderr)

      indexed = []
      try:
        indexed = server.ReloadModule(request.reload_module)
      except BaseException as e:
        # TODO pipe full error into response
        print(f"Error {e}", flush=True, file=sys.stderr)

      if verbose:
        print(f"(Indexed {len(indexed)})",
              flush=True, file=sys.stderr)
      response.reload_module.indexed.extend(indexed)
    elif request.HasField('get_library_element'):
      if verbose:
        print(f"GetLibraryElement({request.get_library_element.element.target.name}) -> ", end='',
              flush=True, file=sys.stderr)
      lib = server.GetLibraryElement(request.get_library_element)
      if verbose:
        if lib.HasField('error'):
          print(f"Error {lib.error}",
                flush=True, file=sys.stderr)
        elif lib.HasField('refinements'):
          print(f"(elt, w/ refinements)",
                flush=True, file=sys.stderr)
        else:
          print(f"(elt)",
                flush=True, file=sys.stderr)
      response.get_library_element.CopyFrom(lib)
    elif request.HasField('elaborate_generator'):
      if verbose:
        print(f"ElaborateGenerator({request.elaborate_generator.element.target.name}) -> ", end='',
              flush=True, file=sys.stderr)
      gen = server.ElaborateGenerator(request.elaborate_generator)
      if verbose:
        if gen.HasField('error'):
          print(f"Error {gen.error}",
                flush=True, file=sys.stderr)
        else:
          print(f"(generated)",
                flush=True, file=sys.stderr)
      response.elaborate_generator.CopyFrom(gen)
    else:
      print(f"Unknown request {request}",
            flush=True, file=sys.stderr)

    stdout_serializer.write(response)
