"""Generated protocol buffer code."""
from google.protobuf.internal import builder as _builder
from google.protobuf import descriptor as _descriptor
from google.protobuf import descriptor_pool as _descriptor_pool
from google.protobuf import symbol_database as _symbol_database
_sym_db = _symbol_database.Default()
from ..edgir import schema_pb2 as edgir_dot_schema__pb2
from ..edgir import ref_pb2 as edgir_dot_ref__pb2
from ..edgir import lit_pb2 as edgir_dot_lit__pb2
from ..edgrpc import hdl_pb2 as edgrpc_dot_hdl__pb2
DESCRIPTOR = _descriptor_pool.Default().AddSerializedFile(b'\n\x15edgrpc/compiler.proto\x12\x0fedgrpc.compiler\x1a\x12edgir/schema.proto\x1a\x0fedgir/ref.proto\x1a\x0fedgir/lit.proto\x1a\x10edgrpc/hdl.proto"^\n\x0bErrorRecord\x12"\n\x04path\x18\x01 \x01(\x0b2\x14.edgir.ref.LocalPath\x12\x0c\n\x04kind\x18\x02 \x01(\t\x12\x0c\n\x04name\x18\x03 \x01(\t\x12\x0f\n\x07details\x18\x04 \x01(\t"e\n\x0fCompilerRequest\x12$\n\x06design\x18\x02 \x01(\x0b2\x14.edgir.schema.Design\x12,\n\x0brefinements\x18\x03 \x01(\x0b2\x17.edgrpc.hdl.Refinements"\xf2\x01\n\x0eCompilerResult\x12$\n\x06design\x18\x01 \x01(\x0b2\x14.edgir.schema.Design\x12,\n\x06errors\x18\x04 \x03(\x0b2\x1c.edgrpc.compiler.ErrorRecord\x12;\n\x0csolvedValues\x18\x02 \x03(\x0b2%.edgrpc.compiler.CompilerResult.Value\x1aO\n\x05Value\x12"\n\x04path\x18\x01 \x01(\x0b2\x14.edgir.ref.LocalPath\x12"\n\x05value\x18\x02 \x01(\x0b2\x13.edgir.lit.ValueLitb\x06proto3')
_builder.BuildMessageAndEnumDescriptors(DESCRIPTOR, globals())
_builder.BuildTopDescriptorsAndMessages(DESCRIPTOR, 'edgrpc.compiler_pb2', globals())
if _descriptor._USE_C_DESCRIPTORS == False:
    DESCRIPTOR._options = None
    _ERRORRECORD._serialized_start = 114
    _ERRORRECORD._serialized_end = 208
    _COMPILERREQUEST._serialized_start = 210
    _COMPILERREQUEST._serialized_end = 311
    _COMPILERRESULT._serialized_start = 314
    _COMPILERRESULT._serialized_end = 556
    _COMPILERRESULT_VALUE._serialized_start = 477
    _COMPILERRESULT_VALUE._serialized_end = 556