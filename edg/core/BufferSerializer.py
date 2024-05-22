from typing import TypeVar, Generic, Type, BinaryIO, Optional, IO

import google.protobuf as protobuf
import struct


MessageType = TypeVar('MessageType', bound=protobuf.message.Message)
kHeaderMagicByte = b'\xfe'


class BufferSerializer(Generic[MessageType]):
  """
  Serializes a protobuf message and writes it into the byte buffer,
  using a delimited framing consistent with the Java implementation.
  """
  def __init__(self, buffer: IO[bytes]):
    self.buffer = buffer

  def write(self, message: MessageType) -> None:
    from google.protobuf.internal.encoder import _VarintBytes  # type: ignore
    # from https://cwiki.apache.org/confluence/display/GEODE/Delimiting+Protobuf+Messages
    serialized = message.SerializeToString()
    self.buffer.write(kHeaderMagicByte)
    self.buffer.write(_VarintBytes(len(serialized)))
    self.buffer.write(serialized)
    self.buffer.flush()


class BufferDeserializer(Generic[MessageType]):
  """
  Deserializes protobuf-serialized messages from a byte buffer and returns it one message at a time,
  using a delimited framing consistent with the Java implementation.
  """
  def __init__(self, message_type: Type[MessageType], buffer: IO[bytes]):
    self.message_type = message_type
    self.buffer = buffer
    self.stdout_buffer = b''

  # Returns the next message from the buffer
  def read(self) -> Optional[MessageType]:
    while True:
      new = self.buffer.read(1)
      if not new:
        return None
      elif new == kHeaderMagicByte:
        break
      else:
        self.stdout_buffer += new

    from google.protobuf.internal.decoder import _DecodeVarint32  # type: ignore
    # from https://cwiki.apache.org/confluence/display/GEODE/Delimiting+Protobuf+Messages
    current = b''
    while len(current) == 0 or current[-1] & 0x80 == 0x80:
      new = self.buffer.read(1)
      if not new:
        return None
      current = current + new
    size, new_pos = _DecodeVarint32(current, 0)
    assert new_pos == len(current)

    current = b''
    while len(current) < size:
      new = self.buffer.read(size - len(current))
      if not new:
        return None
      current = current + new
    assert(len(current) == size)

    message = self.message_type()
    message.ParseFromString(current)

    return message

  def read_stdout(self) -> bytes:
    old_buffer = self.stdout_buffer
    self.stdout_buffer = b''
    return old_buffer
