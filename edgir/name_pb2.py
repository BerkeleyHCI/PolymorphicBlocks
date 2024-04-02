"""Generated protocol buffer code."""
from google.protobuf.internal import builder as _builder
from google.protobuf import descriptor as _descriptor
from google.protobuf import descriptor_pool as _descriptor_pool
from google.protobuf import symbol_database as _symbol_database
_sym_db = _symbol_database.Default()
from ..edgir import common_pb2 as edgir_dot_common__pb2
DESCRIPTOR = _descriptor_pool.Default().AddSerializedFile(b'\n\x10edgir/name.proto\x12\nedgir.name\x1a\x12edgir/common.proto"O\n\tNamespace\x12\x0f\n\x05basic\x18\x01 \x01(\tH\x00\x12$\n\x04meta\x18\x7f \x01(\x0b2\x16.edgir.common.MetadataB\x0b\n\tnamespace"A\n\x0bLibraryName\x12\x0c\n\x04name\x18\x02 \x01(\t\x12$\n\x04meta\x18\x7f \x01(\x0b2\x16.edgir.common.Metadatab\x06proto3')
_builder.BuildMessageAndEnumDescriptors(DESCRIPTOR, globals())
_builder.BuildTopDescriptorsAndMessages(DESCRIPTOR, 'edgir.name_pb2', globals())
if _descriptor._USE_C_DESCRIPTORS == False:
    DESCRIPTOR._options = None
    _NAMESPACE._serialized_start = 52
    _NAMESPACE._serialized_end = 131
    _LIBRARYNAME._serialized_start = 133
    _LIBRARYNAME._serialized_end = 198