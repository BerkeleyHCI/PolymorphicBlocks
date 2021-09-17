from edg_core import HdlInterface, edgrpc
from edg_core.HdlInterfaceServer import LibraryElementResolver, RollbackImporter

import sys
import io

from edg_core import BufferDeserializer, BufferSerializer


if __name__ == '__main__':
  stdin_deserializer = BufferDeserializer(edgrpc.HdlRequest, sys.stdin.buffer)
  stdout_serializer = BufferSerializer[edgrpc.HdlResponse](sys.stdout.buffer)

  print(stdin_deserializer.read())
