from typing import TypeVar, Generic, Type, BinaryIO

import google.protobuf as protobuf
import struct


MessageType = TypeVar('MessageType', bound=protobuf.message.Message)
class BufferDeserializer(Generic[MessageType]):
  """
  Deserializes protobuf-serialized messages from a byte buffer and returns it one message at a time.
  Encapsulates binary protocol details (like the length prefix).
  """
  def __init__(self, message_type: Type[MessageType], buffer: BinaryIO):
    self.message_type = message_type
    self.buffer = buffer

  # Returns the next message from the buffer
  def read(self) -> MessageType:
    current = b''
    while len(current) < 4:
      current = current + self.buffer.read(4 - len(current))
    assert(len(current) == 4)
    size = struct.unpack('!I', current)[0]

    current = b''
    while len(current) < size:
      current = current + self.buffer.read(size - len(current))
    assert(len(current) == size)

    message = self.message_type()
    message.ParseFromString(current)

    return message


class BufferSerializer(Generic[MessageType]):
  """
  Serializes a protobuf message and writes it into the byte buffer.
  Encapsulates binary protocol details (like the length prefix).
  """
  def __init__(self, buffer: BinaryIO):
    self.buffer = buffer

  def write(self, message: MessageType) -> None:
    serialized = message.SerializeToString()
    self.buffer.write(struct.pack('!I', len(serialized)))
    self.buffer.write(serialized)
    self.buffer.flush()
