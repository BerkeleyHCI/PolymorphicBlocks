import unittest
import io
from . import *


class BufferSerializerTestCase(unittest.TestCase):
  def test_serialize(self) -> None:
    pb1 = edgir.ValueLit()
    pb1.range.minimum.floating.val = 42
    pb1.range.maximum.floating.val = 127.8
    pb2 = edgir.ValueLit()
    pb2.range.minimum.floating.val = -42.2
    pb2.range.maximum.floating.val = 0

    buffer = io.BytesIO()
    serializer = BufferSerializer(buffer)
    serializer.write(pb1)
    serializer.write(pb2)

    bytes = buffer.getbuffer().tobytes()
    self.assertEqual(len(bytes), 4 + len(pb1.SerializeToString()) + 4 + len(pb2.SerializeToString()))

    pb2pos = 4 + len(pb1.SerializeToString())
    self.assertEqual(bytes[0:3], b'\x00\x00\x00')
    self.assertEqual(bytes[3], len(pb1.SerializeToString()))
    self.assertEqual(bytes[4:pb2pos], pb1.SerializeToString())
    self.assertEqual(bytes[pb2pos:pb2pos + 3], b'\x00\x00\x00')
    self.assertEqual(bytes[pb2pos + 3], len(pb2.SerializeToString()))
    self.assertEqual(bytes[pb2pos + 4:], pb2.SerializeToString())


class BufferDeserializerTestCase(unittest.TestCase):
  def test_deserialize(self) -> None:
    pb1 = edgir.ValueLit()
    pb1.range.minimum.floating.val = 42
    pb1.range.maximum.floating.val = 127.8
    pb2 = edgir.ValueLit()
    pb2.range.minimum.floating.val = -42.2
    pb2.range.maximum.floating.val = 0

    buffer = io.BytesIO(b'\x00' * (4 + len(pb1.SerializeToString()) + 4 + len(pb2.SerializeToString())))
    bytes = buffer.getbuffer()
    pb2pos = 4 + len(pb1.SerializeToString())
    bytes[3] = len(pb1.SerializeToString())
    bytes[4:pb2pos] = pb1.SerializeToString()
    bytes[pb2pos + 3] = len(pb2.SerializeToString())
    bytes[pb2pos + 4:] = pb2.SerializeToString()

    deserializer = BufferDeserializer(edgir.ValueLit, buffer)
    pb_deserialized = deserializer.read()
    self.assertEqual(pb_deserialized, pb1)
    pb_deserialized = deserializer.read()
    self.assertEqual(pb_deserialized, pb2)
