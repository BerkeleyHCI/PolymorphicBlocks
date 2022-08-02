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


# In some cases stdout seems to buffer excessively, in which case starting python with -u seems to work
# https://stackoverflow.com/a/35467658/5875811
kHeaderMagicByte = b'\xfe'

if __name__ == '__main__':
  server = HdlInterface()
  stdin_deserializer = BufferDeserializer(edgrpc.HdlRequest, sys.stdin.buffer)
  stdout_serializer = BufferSerializer[edgrpc.HdlResponse](sys.stdout.buffer)

  while True:
    request = stdin_deserializer.read()
    if request is None:  # end of stream
      sys.exit(0)

    response = edgrpc.HdlResponse()
    if request.HasField('index_module'):
      indexed = server.IndexModule(request.index_module)  # by intent this crashes if it fails
      response.index_module.indexed.extend(indexed)
    elif request.HasField('get_library_element'):
      lib = server.GetLibraryElement(request.get_library_element)
      response.get_library_element.CopyFrom(lib)
    elif request.HasField('elaborate_generator'):
      gen = server.ElaborateGenerator(request.elaborate_generator)
      response.elaborate_generator.CopyFrom(gen)
    else:
      raise RuntimeError(f"Unknown request {request}")

    sys.stdout.buffer.write(b'\xfe')
    stdout_serializer.write(response)
