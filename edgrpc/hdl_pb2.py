"""Generated protocol buffer code."""
from google.protobuf.internal import builder as _builder
from google.protobuf import descriptor as _descriptor
from google.protobuf import descriptor_pool as _descriptor_pool
from google.protobuf import symbol_database as _symbol_database
_sym_db = _symbol_database.Default()
from ..edgir import schema_pb2 as edgir_dot_schema__pb2
from ..edgir import ref_pb2 as edgir_dot_ref__pb2
from ..edgir import elem_pb2 as edgir_dot_elem__pb2
from ..edgir import lit_pb2 as edgir_dot_lit__pb2
DESCRIPTOR = _descriptor_pool.Default().AddSerializedFile(b'\n\x10edgrpc/hdl.proto\x12\nedgrpc.hdl\x1a\x12edgir/schema.proto\x1a\x0fedgir/ref.proto\x1a\x10edgir/elem.proto\x1a\x0fedgir/lit.proto"\xb6\x04\n\x0bRefinements\x124\n\nsubclasses\x18\x01 \x03(\x0b2 .edgrpc.hdl.Refinements.Subclass\x12-\n\x06values\x18\x02 \x03(\x0b2\x1d.edgrpc.hdl.Refinements.Value\x1a\x8e\x01\n\x08Subclass\x12$\n\x04path\x18\x01 \x01(\x0b2\x14.edgir.ref.LocalPathH\x00\x12%\n\x03cls\x18\x02 \x01(\x0b2\x16.edgir.ref.LibraryPathH\x00\x12+\n\x0breplacement\x18\x03 \x01(\x0b2\x16.edgir.ref.LibraryPathB\x08\n\x06source\x1a\xb0\x02\n\x05Value\x12$\n\x04path\x18\x01 \x01(\x0b2\x14.edgir.ref.LocalPathH\x00\x12A\n\tcls_param\x18\x02 \x01(\x0b2,.edgrpc.hdl.Refinements.Value.ClassParamPathH\x00\x12#\n\x04expr\x18\x03 \x01(\x0b2\x13.edgir.lit.ValueLitH\x01\x12%\n\x05param\x18\x04 \x01(\x0b2\x14.edgir.ref.LocalPathH\x01\x1a_\n\x0eClassParamPath\x12#\n\x03cls\x18\x01 \x01(\x0b2\x16.edgir.ref.LibraryPath\x12(\n\nparam_path\x18\x02 \x01(\x0b2\x14.edgir.ref.LocalPathB\x08\n\x06sourceB\x07\n\x05value"\x1a\n\nModuleName\x12\x0c\n\x04name\x18\x01 \x01(\t"8\n\rIndexResponse\x12\'\n\x07indexed\x18\x01 \x03(\x0b2\x16.edgir.ref.LibraryPath"9\n\x0eLibraryRequest\x12\'\n\x07element\x18\x02 \x01(\x0b2\x16.edgir.ref.LibraryPath"n\n\x0fLibraryResponse\x12-\n\x07element\x18\x01 \x01(\x0b2\x1c.edgir.schema.Library.NS.Val\x12,\n\x0brefinements\x18\x03 \x01(\x0b2\x17.edgrpc.hdl.Refinements"S\n\tExprValue\x12"\n\x04path\x18\x01 \x01(\x0b2\x14.edgir.ref.LocalPath\x12"\n\x05value\x18\x02 \x01(\x0b2\x13.edgir.lit.ValueLit"b\n\x10GeneratorRequest\x12\'\n\x07element\x18\x02 \x01(\x0b2\x16.edgir.ref.LibraryPath\x12%\n\x06values\x18\x04 \x03(\x0b2\x15.edgrpc.hdl.ExprValue"B\n\x11GeneratorResponse\x12-\n\tgenerated\x18\x01 \x01(\x0b2\x1a.edgir.elem.HierarchyBlock"\x97\x01\n\x11RefinementRequest\x12/\n\x0frefinement_pass\x18\x01 \x01(\x0b2\x16.edgir.ref.LibraryPath\x12$\n\x06design\x18\x02 \x01(\x0b2\x14.edgir.schema.Design\x12+\n\x0csolvedValues\x18\x03 \x03(\x0b2\x15.edgrpc.hdl.ExprValue">\n\x12RefinementResponse\x12(\n\tnewValues\x18\x01 \x03(\x0b2\x15.edgrpc.hdl.ExprValue"\xfc\x01\n\x0eBackendRequest\x12\'\n\x07backend\x18\x01 \x01(\x0b2\x16.edgir.ref.LibraryPath\x12$\n\x06design\x18\x02 \x01(\x0b2\x14.edgir.schema.Design\x12+\n\x0csolvedValues\x18\x03 \x03(\x0b2\x15.edgrpc.hdl.ExprValue\x12<\n\targuments\x18\x04 \x03(\x0b2).edgrpc.hdl.BackendRequest.ArgumentsEntry\x1a0\n\x0eArgumentsEntry\x12\x0b\n\x03key\x18\x01 \x01(\t\x12\r\n\x05value\x18\x02 \x01(\t:\x028\x01"\x8e\x01\n\x0fBackendResponse\x123\n\x07results\x18\x01 \x03(\x0b2".edgrpc.hdl.BackendResponse.Result\x1aF\n\x06Result\x12"\n\x04path\x18\x01 \x01(\x0b2\x14.edgir.ref.LocalPath\x12\x0e\n\x04text\x18\x02 \x01(\tH\x00B\x08\n\x06result"1\n\rErrorResponse\x12\r\n\x05error\x18\x01 \x01(\t\x12\x11\n\ttraceback\x18\x02 \x01(\t"\xc8\x02\n\nHdlRequest\x12.\n\x0cindex_module\x18\x01 \x01(\x0b2\x16.edgrpc.hdl.ModuleNameH\x00\x129\n\x13get_library_element\x18\x02 \x01(\x0b2\x1a.edgrpc.hdl.LibraryRequestH\x00\x12;\n\x13elaborate_generator\x18\x03 \x01(\x0b2\x1c.edgrpc.hdl.GeneratorRequestH\x00\x127\n\x0erun_refinement\x18\x05 \x01(\x0b2\x1d.edgrpc.hdl.RefinementRequestH\x00\x121\n\x0brun_backend\x18\x04 \x01(\x0b2\x1a.edgrpc.hdl.BackendRequestH\x00\x12\x1b\n\x11get_proto_version\x18Z \x01(\rH\x00B\t\n\x07request"\xfd\x02\n\x0bHdlResponse\x121\n\x0cindex_module\x18\x01 \x01(\x0b2\x19.edgrpc.hdl.IndexResponseH\x00\x12:\n\x13get_library_element\x18\x02 \x01(\x0b2\x1b.edgrpc.hdl.LibraryResponseH\x00\x12<\n\x13elaborate_generator\x18\x03 \x01(\x0b2\x1d.edgrpc.hdl.GeneratorResponseH\x00\x128\n\x0erun_refinement\x18\x05 \x01(\x0b2\x1e.edgrpc.hdl.RefinementResponseH\x00\x122\n\x0brun_backend\x18\x04 \x01(\x0b2\x1b.edgrpc.hdl.BackendResponseH\x00\x12\x1b\n\x11get_proto_version\x18Z \x01(\rH\x00\x12*\n\x05error\x18c \x01(\x0b2\x19.edgrpc.hdl.ErrorResponseH\x00B\n\n\x08responseb\x06proto3')
_builder.BuildMessageAndEnumDescriptors(DESCRIPTOR, globals())
_builder.BuildTopDescriptorsAndMessages(DESCRIPTOR, 'edgrpc.hdl_pb2', globals())
if _descriptor._USE_C_DESCRIPTORS == False:
    DESCRIPTOR._options = None
    _BACKENDREQUEST_ARGUMENTSENTRY._options = None
    _BACKENDREQUEST_ARGUMENTSENTRY._serialized_options = b'8\x01'
    _REFINEMENTS._serialized_start = 105
    _REFINEMENTS._serialized_end = 671
    _REFINEMENTS_SUBCLASS._serialized_start = 222
    _REFINEMENTS_SUBCLASS._serialized_end = 364
    _REFINEMENTS_VALUE._serialized_start = 367
    _REFINEMENTS_VALUE._serialized_end = 671
    _REFINEMENTS_VALUE_CLASSPARAMPATH._serialized_start = 557
    _REFINEMENTS_VALUE_CLASSPARAMPATH._serialized_end = 652
    _MODULENAME._serialized_start = 673
    _MODULENAME._serialized_end = 699
    _INDEXRESPONSE._serialized_start = 701
    _INDEXRESPONSE._serialized_end = 757
    _LIBRARYREQUEST._serialized_start = 759
    _LIBRARYREQUEST._serialized_end = 816
    _LIBRARYRESPONSE._serialized_start = 818
    _LIBRARYRESPONSE._serialized_end = 928
    _EXPRVALUE._serialized_start = 930
    _EXPRVALUE._serialized_end = 1013
    _GENERATORREQUEST._serialized_start = 1015
    _GENERATORREQUEST._serialized_end = 1113
    _GENERATORRESPONSE._serialized_start = 1115
    _GENERATORRESPONSE._serialized_end = 1181
    _REFINEMENTREQUEST._serialized_start = 1184
    _REFINEMENTREQUEST._serialized_end = 1335
    _REFINEMENTRESPONSE._serialized_start = 1337
    _REFINEMENTRESPONSE._serialized_end = 1399
    _BACKENDREQUEST._serialized_start = 1402
    _BACKENDREQUEST._serialized_end = 1654
    _BACKENDREQUEST_ARGUMENTSENTRY._serialized_start = 1606
    _BACKENDREQUEST_ARGUMENTSENTRY._serialized_end = 1654
    _BACKENDRESPONSE._serialized_start = 1657
    _BACKENDRESPONSE._serialized_end = 1799
    _BACKENDRESPONSE_RESULT._serialized_start = 1729
    _BACKENDRESPONSE_RESULT._serialized_end = 1799
    _ERRORRESPONSE._serialized_start = 1801
    _ERRORRESPONSE._serialized_end = 1850
    _HDLREQUEST._serialized_start = 1853
    _HDLREQUEST._serialized_end = 2181
    _HDLRESPONSE._serialized_start = 2184
    _HDLRESPONSE._serialized_end = 2565