import sys

import edgrpc
from edg_core import HdlInterface
from edg_core import BufferDeserializer, BufferSerializer

# This magic line of code makes the reloading in HdlInterfaceServer not break.
# Otherwise, for some reason, it sees duplicate modules.
# I don't know why this works, or what the root cause is, but this makes things work...
# Possibly because even the test case code in edg_core getting rolled back causes issues?
# even if nothing else in core depends on that test code
from blinky_skeleton import *

if __name__ == '__main__':
  verbose = False

  def eprint(*args, **kwargs):
    # Print to stderr, to avoid messing up the stdout communication channel
    if verbose:
      print(*args, **kwargs, file=sys.stderr, flush=True)

  server = HdlInterface()
  stdin_deserializer = BufferDeserializer(edgrpc.HdlRequest, sys.stdin.buffer)
  stdout_serializer = BufferSerializer[edgrpc.HdlResponse](sys.stdout.buffer)

  eprint(f"HDL Interface Server started")

  while True:
    request = stdin_deserializer.read()
    if request is None:  # end of stream
      sys.exit(0)

    response = edgrpc.HdlResponse()
    if request.HasField('index_module'):
      eprint(f"IndexModule({request.index_module.name}) -> ", end='')

      indexed = []
      try:
        indexed = server.IndexModule(request.index_module)
      except BaseException as e:
        # TODO pipe full error into response
        eprint(f"Error {e}")

      eprint(f"(Indexed {len(indexed)})")
      response.index_module.indexed.extend(indexed)
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
