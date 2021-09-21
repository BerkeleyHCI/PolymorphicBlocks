import sys

from edg_core import HdlInterface, edgrpc
from edg_core.HdlInterfaceServer import RollbackImporter
from edg_core import BufferDeserializer, BufferSerializer


if __name__ == '__main__':
  verbose = False

  def eprint(*args, **kwargs):
    # Print to stderr, to avoid messing up the stdout communication channel
    if verbose:
      print(*args, **kwargs, file=sys.stderr, flush=True)

  server = HdlInterface(rollback=RollbackImporter())
  stdin_deserializer = BufferDeserializer(edgrpc.HdlRequest, sys.stdin.buffer)
  stdout_serializer = BufferSerializer[edgrpc.HdlResponse](sys.stdout.buffer)

  eprint(f"HDL Interface Server started")

  while True:
    request = stdin_deserializer.read()
    if request is None:  # end of stream
      sys.exit(0)

    response = edgrpc.HdlResponse()
    if request.HasField('reload_module'):
      eprint(f"ReloadModule({request.reload_module.name}) -> ", end='')

      indexed = []
      try:
        indexed = server.ReloadModule(request.reload_module)
      except BaseException as e:
        # TODO pipe full error into response
        eprint(f"Error {e}")

      eprint(f"(Indexed {len(indexed)})")
      response.reload_module.indexed.extend(indexed)
    elif request.HasField('get_library_element'):
      if verbose:
        eprint(f"GetLibraryElement({request.get_library_element.element.target.name}) -> ", end='')

      lib = server.GetLibraryElement(request.get_library_element)

      if lib.HasField('error'):
        eprint(f"Error {lib.error}")
      elif lib.HasField('refinements'):
        eprint(f"(elt, w/ refinements)")
      else:
        eprint(f"(elt)")
      response.get_library_element.CopyFrom(lib)
    elif request.HasField('elaborate_generator'):
      eprint(f"ElaborateGenerator({request.elaborate_generator.element.target.name}) -> ", end='')

      gen = server.ElaborateGenerator(request.elaborate_generator)

      if gen.HasField('error'):
        eprint(f"Error {gen.error}")
      else:
        eprint(f"(generated)")
      response.elaborate_generator.CopyFrom(gen)
    else:
      eprint(f"Unknown request {request}")

    stdout_serializer.write(response)
