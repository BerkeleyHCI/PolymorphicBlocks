"""Generated protocol buffer code."""
from google.protobuf.internal import builder as _builder
from google.protobuf import descriptor as _descriptor
from google.protobuf import descriptor_pool as _descriptor_pool
from google.protobuf import symbol_database as _symbol_database
_sym_db = _symbol_database.Default()
from ..edgir import common_pb2 as edgir_dot_common__pb2
DESCRIPTOR = _descriptor_pool.Default().AddSerializedFile(b'\n\x10edgir/init.proto\x12\nedgir.init\x1a\x12edgir/common.proto"\xeb\x02\n\x07ValInit\x12\'\n\x08floating\x18\x01 \x01(\x0b2\x13.edgir.common.EmptyH\x00\x12&\n\x07integer\x18\x02 \x01(\x0b2\x13.edgir.common.EmptyH\x00\x12&\n\x07boolean\x18\x03 \x01(\x0b2\x13.edgir.common.EmptyH\x00\x12#\n\x04text\x18\x04 \x01(\x0b2\x13.edgir.common.EmptyH\x00\x12"\n\x03set\x18\x08 \x01(\x0b2\x13.edgir.common.EmptyH\x00\x12%\n\x06struct\x18\t \x01(\x0b2\x13.edgir.common.EmptyH\x00\x12$\n\x05range\x18\n \x01(\x0b2\x13.edgir.common.EmptyH\x00\x12$\n\x05array\x18\x0b \x01(\x0b2\x13.edgir.init.ValInitH\x00\x12$\n\x04meta\x18\x7f \x01(\x0b2\x16.edgir.common.MetadataB\x05\n\x03valb\x06proto3')
_builder.BuildMessageAndEnumDescriptors(DESCRIPTOR, globals())
_builder.BuildTopDescriptorsAndMessages(DESCRIPTOR, 'edgir.init_pb2', globals())
if _descriptor._USE_C_DESCRIPTORS == False:
    DESCRIPTOR._options = None
    _VALINIT._serialized_start = 53
    _VALINIT._serialized_end = 416