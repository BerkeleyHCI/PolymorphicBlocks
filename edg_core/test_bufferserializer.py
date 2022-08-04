import unittest
import io
import edgir
from . import *


class BufferSerializerTestCase(unittest.TestCase):
  def test_serialize(self) -> None:
    pb1 = edgir.ValueLit()
    pb1.range.minimum.floating.val = 42
    pb1.range.maximum.floating.val = 127.8
    pb2 = edgir.ValueLit()
    pb2.text.val = "!" * 200

    buffer = io.BytesIO()
    serializer = BufferSerializer[edgir.ValueLit](buffer)
    serializer.write(pb1)
    serializer.write(pb2)

    # assume small enough so size is only one byte
    assert pb1.ByteSize() <= 127
    assert 127 < pb2.ByteSize() <= 255

    bytes = buffer.getbuffer().tobytes()
    self.assertEqual(len(bytes), 1 + 1 + len(pb1.SerializeToString()) + 1 + 2 + len(pb2.SerializeToString()))

    pb2pos = 2 + len(pb1.SerializeToString())
    pb2len = len(pb2.SerializeToString())
    self.assertEqual(bytes[0], 0xfe)
    self.assertEqual(bytes[1], len(pb1.SerializeToString()))
    self.assertEqual(bytes[2:pb2pos], pb1.SerializeToString())
    self.assertEqual(bytes[pb2pos], 0xfe)
    self.assertEqual(bytes[pb2pos + 1], pb2len & 0x7f | 0x80)
    self.assertEqual(bytes[pb2pos + 2], pb2len >> 7 & 0x7f)
    self.assertEqual(bytes[pb2pos + 3:], pb2.SerializeToString())


class BufferDeserializerTestCase(unittest.TestCase):
  def test_deserialize(self) -> None:
    pb1 = edgir.ValueLit()
    pb1.range.minimum.floating.val = 42
    pb1.range.maximum.floating.val = 127.8
    pb2 = edgir.ValueLit()
    pb2.text.val = "!" * 200

    # assume small enough so size is only one byte
    assert pb1.ByteSize() <= 127
    assert 127 < pb2.ByteSize() <= 255

    buffer = io.BytesIO(b'\x00' * (1 + 1 + len(pb1.SerializeToString()) + 1 + 2 + len(pb2.SerializeToString())))
    bytes = buffer.getbuffer()
    pb2pos = 1 + 1 + len(pb1.SerializeToString())
    pb2len = len(pb2.SerializeToString())
    bytes[0] = 0xfe
    bytes[1] = len(pb1.SerializeToString())
    bytes[2:pb2pos] = pb1.SerializeToString()
    bytes[pb2pos] = 0xfe
    bytes[pb2pos + 1] = pb2len & 0x7f | 0x80
    bytes[pb2pos + 2] = pb2len >> 7 & 0x7f
    bytes[pb2pos + 3:] = pb2.SerializeToString()

    deserializer = BufferDeserializer(edgir.ValueLit, buffer)
    pb_deserialized = deserializer.read()
    self.assertEqual(pb_deserialized, pb1)
    pb_deserialized = deserializer.read()
    self.assertEqual(pb_deserialized, pb2)
