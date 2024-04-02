"""Generated protocol buffer code."""
from google.protobuf.internal import builder as _builder
from google.protobuf import descriptor as _descriptor
from google.protobuf import descriptor_pool as _descriptor_pool
from google.protobuf import symbol_database as _symbol_database
_sym_db = _symbol_database.Default()
from ..edgir import common_pb2 as edgir_dot_common__pb2
DESCRIPTOR = _descriptor_pool.Default().AddSerializedFile(b'\n\x10edgir/impl.proto\x12\nedgir.impl\x1a\x12edgir/common.proto"1\n\tBlockImpl\x12$\n\x04meta\x18\x7f \x01(\x0b2\x16.edgir.common.Metadata"0\n\x08PortImpl\x12$\n\x04meta\x18\x7f \x01(\x0b2\x16.edgir.common.Metadata"0\n\x08LinkImpl\x12$\n\x04meta\x18\x7f \x01(\x0b2\x16.edgir.common.Metadata"7\n\x0fEnvironmentImpl\x12$\n\x04meta\x18\x7f \x01(\x0b2\x16.edgir.common.Metadatab\x06proto3')
_builder.BuildMessageAndEnumDescriptors(DESCRIPTOR, globals())
_builder.BuildTopDescriptorsAndMessages(DESCRIPTOR, 'edgir.impl_pb2', globals())
if _descriptor._USE_C_DESCRIPTORS == False:
    DESCRIPTOR._options = None
    _BLOCKIMPL._serialized_start = 52
    _BLOCKIMPL._serialized_end = 101
    _PORTIMPL._serialized_start = 103
    _PORTIMPL._serialized_end = 151
    _LINKIMPL._serialized_start = 153
    _LINKIMPL._serialized_end = 201
    _ENVIRONMENTIMPL._serialized_start = 203
    _ENVIRONMENTIMPL._serialized_end = 258