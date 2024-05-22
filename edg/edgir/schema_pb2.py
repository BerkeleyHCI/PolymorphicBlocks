"""Generated protocol buffer code."""
from google.protobuf.internal import builder as _builder
from google.protobuf import descriptor as _descriptor
from google.protobuf import descriptor_pool as _descriptor_pool
from google.protobuf import symbol_database as _symbol_database
_sym_db = _symbol_database.Default()
from ..edgir import common_pb2 as edgir_dot_common__pb2
from ..edgir import elem_pb2 as edgir_dot_elem__pb2
DESCRIPTOR = _descriptor_pool.Default().AddSerializedFile(b'\n\x12edgir/schema.proto\x12\x0cedgir.schema\x1a\x12edgir/common.proto\x1a\x10edgir/elem.proto"\x9b\x04\n\x07Library\x12*\n\x02id\x18\x01 \x01(\x0b2\x1e.edgir.schema.Library.LibIdent\x12\x0f\n\x07imports\x18\x02 \x03(\t\x12&\n\x04root\x18\n \x01(\x0b2\x18.edgir.schema.Library.NS\x12$\n\x04meta\x18\x7f \x01(\x0b2\x16.edgir.common.Metadata\x1a\xea\x02\n\x02NS\x126\n\x07members\x18\x01 \x03(\x0b2%.edgir.schema.Library.NS.MembersEntry\x1a\xdd\x01\n\x03Val\x12 \n\x04port\x18\n \x01(\x0b2\x10.edgir.elem.PortH\x00\x12$\n\x06bundle\x18\x0b \x01(\x0b2\x12.edgir.elem.BundleH\x00\x125\n\x0fhierarchy_block\x18\r \x01(\x0b2\x1a.edgir.elem.HierarchyBlockH\x00\x12 \n\x04link\x18\x0e \x01(\x0b2\x10.edgir.elem.LinkH\x00\x12-\n\tnamespace\x18\x14 \x01(\x0b2\x18.edgir.schema.Library.NSH\x00B\x06\n\x04type\x1aL\n\x0cMembersEntry\x12\x0b\n\x03key\x18\x01 \x01(\t\x12+\n\x05value\x18\x02 \x01(\x0b2\x1c.edgir.schema.Library.NS.Val:\x028\x01\x1a\x18\n\x08LibIdent\x12\x0c\n\x04name\x18\x01 \x01(\t"6\n\x06Design\x12,\n\x08contents\x18\x02 \x01(\x0b2\x1a.edgir.elem.HierarchyBlockb\x06proto3')
_builder.BuildMessageAndEnumDescriptors(DESCRIPTOR, globals())
_builder.BuildTopDescriptorsAndMessages(DESCRIPTOR, 'edgir.schema_pb2', globals())
if _descriptor._USE_C_DESCRIPTORS == False:
    DESCRIPTOR._options = None
    _LIBRARY_NS_MEMBERSENTRY._options = None
    _LIBRARY_NS_MEMBERSENTRY._serialized_options = b'8\x01'
    _LIBRARY._serialized_start = 75
    _LIBRARY._serialized_end = 614
    _LIBRARY_NS._serialized_start = 226
    _LIBRARY_NS._serialized_end = 588
    _LIBRARY_NS_VAL._serialized_start = 289
    _LIBRARY_NS_VAL._serialized_end = 510
    _LIBRARY_NS_MEMBERSENTRY._serialized_start = 512
    _LIBRARY_NS_MEMBERSENTRY._serialized_end = 588
    _LIBRARY_LIBIDENT._serialized_start = 590
    _LIBRARY_LIBIDENT._serialized_end = 614
    _DESIGN._serialized_start = 616
    _DESIGN._serialized_end = 670