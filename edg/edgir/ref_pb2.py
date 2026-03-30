"""Generated protocol buffer code."""
from google.protobuf.internal import builder as _builder
from google.protobuf import descriptor as _descriptor
from google.protobuf import descriptor_pool as _descriptor_pool
from google.protobuf import symbol_database as _symbol_database
_sym_db = _symbol_database.Default()
from ..edgir import common_pb2 as edgir_dot_common__pb2
from ..edgir import name_pb2 as edgir_dot_name__pb2
DESCRIPTOR = _descriptor_pool.Default().AddSerializedFile(b'\n\x0fedgir/ref.proto\x12\tedgir.ref\x1a\x12edgir/common.proto\x1a\x10edgir/name.proto"f\n\tLocalStep\x12-\n\x0ereserved_param\x18\x01 \x01(\x0e2\x13.edgir.ref.ReservedH\x00\x12\x12\n\x08allocate\x18\x02 \x01(\tH\x00\x12\x0e\n\x04name\x18\x03 \x01(\tH\x00B\x06\n\x04step"W\n\tLocalPath\x12#\n\x05steps\x18\x01 \x03(\x0b2\x14.edgir.ref.LocalStep\x12%\n\x04meta\x18\xff\x01 \x01(\x0b2\x16.edgir.common.Metadata"\xa8\x01\n\x0bLibraryPath\x12&\n\x05start\x18\x01 \x01(\x0b2\x17.edgir.name.LibraryName\x12$\n\x05steps\x18\x02 \x03(\x0b2\x15.edgir.name.Namespace\x12$\n\x06target\x18\x03 \x01(\x0b2\x14.edgir.ref.LocalStep\x12%\n\x04meta\x18\xff\x01 \x01(\x0b2\x16.edgir.common.Metadata*r\n\x08Reserved\x12\r\n\tUNDEFINED\x10\x00\x12\x12\n\x0eCONNECTED_LINK\x10\x01\x12\x10\n\x0cIS_CONNECTED\x10(\x12\n\n\x06LENGTH\x10*\x12\x08\n\x04NAME\x10,\x12\x0c\n\x08ELEMENTS\x10-\x12\r\n\tALLOCATED\x10.b\x06proto3')
_builder.BuildMessageAndEnumDescriptors(DESCRIPTOR, globals())
_builder.BuildTopDescriptorsAndMessages(DESCRIPTOR, 'edgir.ref_pb2', globals())
if _descriptor._USE_C_DESCRIPTORS == False:
    DESCRIPTOR._options = None
    _RESERVED._serialized_start = 432
    _RESERVED._serialized_end = 546
    _LOCALSTEP._serialized_start = 68
    _LOCALSTEP._serialized_end = 170
    _LOCALPATH._serialized_start = 172
    _LOCALPATH._serialized_end = 259
    _LIBRARYPATH._serialized_start = 262
    _LIBRARYPATH._serialized_end = 430