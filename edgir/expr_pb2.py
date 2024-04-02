"""Generated protocol buffer code."""
from google.protobuf.internal import builder as _builder
from google.protobuf import descriptor as _descriptor
from google.protobuf import descriptor_pool as _descriptor_pool
from google.protobuf import symbol_database as _symbol_database
_sym_db = _symbol_database.Default()
from ..edgir import ref_pb2 as edgir_dot_ref__pb2
from ..edgir import common_pb2 as edgir_dot_common__pb2
from ..edgir import lit_pb2 as edgir_dot_lit__pb2
DESCRIPTOR = _descriptor_pool.Default().AddSerializedFile(b'\n\x10edgir/expr.proto\x12\nedgir.expr\x1a\x0fedgir/ref.proto\x1a\x12edgir/common.proto\x1a\x0fedgir/lit.proto"\xb4\x01\n\tUnaryExpr\x12$\n\x02op\x18\x01 \x01(\x0e2\x18.edgir.expr.UnaryExpr.Op\x12"\n\x03val\x18\x02 \x01(\x0b2\x15.edgir.expr.ValueExpr"]\n\x02Op\x12\r\n\tUNDEFINED\x10\x00\x12\n\n\x06NEGATE\x10\x01\x12\x07\n\x03NOT\x10\x02\x12\n\n\x06INVERT\x10\x03\x12\x07\n\x03MIN\x10\x04\x12\x07\n\x03MAX\x10\x05\x12\n\n\x06CENTER\x10\x06\x12\t\n\x05WIDTH\x10\x07"\x9f\x02\n\x0cUnarySetExpr\x12\'\n\x02op\x18\x01 \x01(\x0e2\x1b.edgir.expr.UnarySetExpr.Op\x12#\n\x04vals\x18\x04 \x01(\x0b2\x15.edgir.expr.ValueExpr"\xc0\x01\n\x02Op\x12\r\n\tUNDEFINED\x10\x00\x12\x07\n\x03SUM\x10\x01\x12\x0c\n\x08ALL_TRUE\x10\x02\x12\x0c\n\x08ANY_TRUE\x10\x03\x12\n\n\x06ALL_EQ\x10\x04\x12\x0e\n\nALL_UNIQUE\x10\x05\x12\x0b\n\x07MAXIMUM\x10\n\x12\x0b\n\x07MINIMUM\x10\x0b\x12\x0f\n\x0bSET_EXTRACT\x10\x0c\x12\x10\n\x0cINTERSECTION\x10\r\x12\x08\n\x04HULL\x10\x0e\x12\n\n\x06NEGATE\x10\x14\x12\n\n\x06INVERT\x10\x15\x12\x0b\n\x07FLATTEN\x10\x1e"\xc3\x02\n\nBinaryExpr\x12%\n\x02op\x18\x01 \x01(\x0e2\x19.edgir.expr.BinaryExpr.Op\x12"\n\x03lhs\x18\x02 \x01(\x0b2\x15.edgir.expr.ValueExpr\x12"\n\x03rhs\x18\x03 \x01(\x0b2\x15.edgir.expr.ValueExpr"\xc5\x01\n\x02Op\x12\r\n\tUNDEFINED\x10\x00\x12\x07\n\x03ADD\x10\n\x12\x08\n\x04MULT\x10\x0c\x12\x07\n\x03AND\x10\x14\x12\x06\n\x02OR\x10\x15\x12\x07\n\x03XOR\x10\x16\x12\x0b\n\x07IMPLIES\x10\x17\x12\x06\n\x02EQ\x10\x1e\x12\x07\n\x03NEQ\x10\x1f\x12\x06\n\x02GT\x10(\x12\x07\n\x03GTE\x10)\x12\x06\n\x02LT\x10*\x12\x07\n\x03LTE\x10,\x12\x07\n\x03MAX\x10-\x12\x07\n\x03MIN\x10.\x12\x10\n\x0cINTERSECTION\x103\x12\x08\n\x04HULL\x106\x12\n\n\x06WITHIN\x105\x12\t\n\x05RANGE\x10\x01"\xb7\x01\n\rBinarySetExpr\x12(\n\x02op\x18\x01 \x01(\x0e2\x1c.edgir.expr.BinarySetExpr.Op\x12$\n\x05lhset\x18\x02 \x01(\x0b2\x15.edgir.expr.ValueExpr\x12"\n\x03rhs\x18\x03 \x01(\x0b2\x15.edgir.expr.ValueExpr"2\n\x02Op\x12\r\n\tUNDEFINED\x10\x00\x12\x07\n\x03ADD\x10\n\x12\x08\n\x04MULT\x10\x0c\x12\n\n\x06CONCAT\x10\x14"0\n\tArrayExpr\x12#\n\x04vals\x18\x01 \x03(\x0b2\x15.edgir.expr.ValueExpr"[\n\tRangeExpr\x12&\n\x07minimum\x18\x01 \x01(\x0b2\x15.edgir.expr.ValueExpr\x12&\n\x07maximum\x18\x02 \x01(\x0b2\x15.edgir.expr.ValueExpr"\x80\x01\n\nStructExpr\x12.\n\x04vals\x18\x01 \x03(\x0b2 .edgir.expr.StructExpr.ValsEntry\x1aB\n\tValsEntry\x12\x0b\n\x03key\x18\x01 \x01(\t\x12$\n\x05value\x18\x02 \x01(\x0b2\x15.edgir.expr.ValueExpr:\x028\x01"\xa3\x01\n\x0eIfThenElseExpr\x12#\n\x04cond\x18\x01 \x01(\x0b2\x15.edgir.expr.ValueExpr\x12"\n\x03tru\x18\x02 \x01(\x0b2\x15.edgir.expr.ValueExpr\x12"\n\x03fal\x18\x03 \x01(\x0b2\x15.edgir.expr.ValueExpr\x12$\n\x04meta\x18\x7f \x01(\x0b2\x16.edgir.common.Metadata"]\n\x0bExtractExpr\x12(\n\tcontainer\x18\x01 \x01(\x0b2\x15.edgir.expr.ValueExpr\x12$\n\x05index\x18\x02 \x01(\x0b2\x15.edgir.expr.ValueExpr"^\n\x0eMapExtractExpr\x12(\n\tcontainer\x18\x01 \x01(\x0b2\x15.edgir.expr.ValueExpr\x12"\n\x04path\x18\x02 \x01(\x0b2\x14.edgir.ref.LocalPath"\x91\x01\n\rConnectedExpr\x12)\n\nblock_port\x18\x01 \x01(\x0b2\x15.edgir.expr.ValueExpr\x12(\n\tlink_port\x18\x02 \x01(\x0b2\x15.edgir.expr.ValueExpr\x12+\n\x08expanded\x18\x03 \x03(\x0b2\x19.edgir.expr.ConnectedExpr"\x9c\x01\n\x0cExportedExpr\x12,\n\rexterior_port\x18\x01 \x01(\x0b2\x15.edgir.expr.ValueExpr\x122\n\x13internal_block_port\x18\x02 \x01(\x0b2\x15.edgir.expr.ValueExpr\x12*\n\x08expanded\x18\x03 \x03(\x0b2\x18.edgir.expr.ExportedExpr"S\n\nAssignExpr\x12!\n\x03dst\x18\x01 \x01(\x0b2\x14.edgir.ref.LocalPath\x12"\n\x03src\x18\x02 \x01(\x0b2\x15.edgir.expr.ValueExpr"\x97\x07\n\tValueExpr\x12&\n\x07literal\x18\x01 \x01(\x0b2\x13.edgir.lit.ValueLitH\x00\x12(\n\x06binary\x18\x02 \x01(\x0b2\x16.edgir.expr.BinaryExprH\x00\x12/\n\nbinary_set\x18\x12 \x01(\x0b2\x19.edgir.expr.BinarySetExprH\x00\x12&\n\x05unary\x18\x03 \x01(\x0b2\x15.edgir.expr.UnaryExprH\x00\x12-\n\tunary_set\x18\x04 \x01(\x0b2\x18.edgir.expr.UnarySetExprH\x00\x12&\n\x05array\x18\x06 \x01(\x0b2\x15.edgir.expr.ArrayExprH\x00\x12(\n\x06struct\x18\x07 \x01(\x0b2\x16.edgir.expr.StructExprH\x00\x12&\n\x05range\x18\x08 \x01(\x0b2\x15.edgir.expr.RangeExprH\x00\x120\n\nifThenElse\x18\n \x01(\x0b2\x1a.edgir.expr.IfThenElseExprH\x00\x12*\n\x07extract\x18\x0c \x01(\x0b2\x17.edgir.expr.ExtractExprH\x00\x121\n\x0bmap_extract\x18\x0e \x01(\x0b2\x1a.edgir.expr.MapExtractExprH\x00\x12.\n\tconnected\x18\x0f \x01(\x0b2\x19.edgir.expr.ConnectedExprH\x00\x12,\n\x08exported\x18\x10 \x01(\x0b2\x18.edgir.expr.ExportedExprH\x00\x123\n\x0econnectedArray\x18\x13 \x01(\x0b2\x19.edgir.expr.ConnectedExprH\x00\x121\n\rexportedArray\x18\x14 \x01(\x0b2\x18.edgir.expr.ExportedExprH\x00\x12(\n\x06assign\x18\x11 \x01(\x0b2\x16.edgir.expr.AssignExprH\x00\x122\n\x0eexportedTunnel\x18\x15 \x01(\x0b2\x18.edgir.expr.ExportedExprH\x00\x12.\n\x0cassignTunnel\x18\x16 \x01(\x0b2\x16.edgir.expr.AssignExprH\x00\x12#\n\x03ref\x18c \x01(\x0b2\x14.edgir.ref.LocalPathH\x00\x12$\n\x04meta\x18\x7f \x01(\x0b2\x16.edgir.common.MetadataB\x06\n\x04exprb\x06proto3')
_builder.BuildMessageAndEnumDescriptors(DESCRIPTOR, globals())
_builder.BuildTopDescriptorsAndMessages(DESCRIPTOR, 'edgir.expr_pb2', globals())
if _descriptor._USE_C_DESCRIPTORS == False:
    DESCRIPTOR._options = None
    _STRUCTEXPR_VALSENTRY._options = None
    _STRUCTEXPR_VALSENTRY._serialized_options = b'8\x01'
    _UNARYEXPR._serialized_start = 87
    _UNARYEXPR._serialized_end = 267
    _UNARYEXPR_OP._serialized_start = 174
    _UNARYEXPR_OP._serialized_end = 267
    _UNARYSETEXPR._serialized_start = 270
    _UNARYSETEXPR._serialized_end = 557
    _UNARYSETEXPR_OP._serialized_start = 365
    _UNARYSETEXPR_OP._serialized_end = 557
    _BINARYEXPR._serialized_start = 560
    _BINARYEXPR._serialized_end = 883
    _BINARYEXPR_OP._serialized_start = 686
    _BINARYEXPR_OP._serialized_end = 883
    _BINARYSETEXPR._serialized_start = 886
    _BINARYSETEXPR._serialized_end = 1069
    _BINARYSETEXPR_OP._serialized_start = 1019
    _BINARYSETEXPR_OP._serialized_end = 1069
    _ARRAYEXPR._serialized_start = 1071
    _ARRAYEXPR._serialized_end = 1119
    _RANGEEXPR._serialized_start = 1121
    _RANGEEXPR._serialized_end = 1212
    _STRUCTEXPR._serialized_start = 1215
    _STRUCTEXPR._serialized_end = 1343
    _STRUCTEXPR_VALSENTRY._serialized_start = 1277
    _STRUCTEXPR_VALSENTRY._serialized_end = 1343
    _IFTHENELSEEXPR._serialized_start = 1346
    _IFTHENELSEEXPR._serialized_end = 1509
    _EXTRACTEXPR._serialized_start = 1511
    _EXTRACTEXPR._serialized_end = 1604
    _MAPEXTRACTEXPR._serialized_start = 1606
    _MAPEXTRACTEXPR._serialized_end = 1700
    _CONNECTEDEXPR._serialized_start = 1703
    _CONNECTEDEXPR._serialized_end = 1848
    _EXPORTEDEXPR._serialized_start = 1851
    _EXPORTEDEXPR._serialized_end = 2007
    _ASSIGNEXPR._serialized_start = 2009
    _ASSIGNEXPR._serialized_end = 2092
    _VALUEEXPR._serialized_start = 2095
    _VALUEEXPR._serialized_end = 3014