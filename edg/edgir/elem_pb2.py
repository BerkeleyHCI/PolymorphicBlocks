"""Generated protocol buffer code."""
from google.protobuf.internal import builder as _builder
from google.protobuf import descriptor as _descriptor
from google.protobuf import descriptor_pool as _descriptor_pool
from google.protobuf import symbol_database as _symbol_database
_sym_db = _symbol_database.Default()
from ..edgir import common_pb2 as edgir_dot_common__pb2
from ..edgir import init_pb2 as edgir_dot_init__pb2
from ..edgir import expr_pb2 as edgir_dot_expr__pb2
from ..edgir import ref_pb2 as edgir_dot_ref__pb2
DESCRIPTOR = _descriptor_pool.Default().AddSerializedFile(b'\n\x10edgir/elem.proto\x12\nedgir.elem\x1a\x12edgir/common.proto\x1a\x10edgir/init.proto\x1a\x10edgir/expr.proto\x1a\x0fedgir/ref.proto"@\n\x0cNamedValInit\x12\x0c\n\x04name\x18\x01 \x01(\t\x12"\n\x05value\x18\x02 \x01(\x0b2\x13.edgir.init.ValInit"D\n\x0eNamedValueExpr\x12\x0c\n\x04name\x18\x01 \x01(\t\x12$\n\x05value\x18\x02 \x01(\x0b2\x15.edgir.expr.ValueExpr"B\n\rNamedPortLike\x12\x0c\n\x04name\x18\x01 \x01(\t\x12#\n\x05value\x18\x02 \x01(\x0b2\x14.edgir.elem.PortLike"D\n\x0eNamedBlockLike\x12\x0c\n\x04name\x18\x01 \x01(\t\x12$\n\x05value\x18\x02 \x01(\x0b2\x15.edgir.elem.BlockLike"B\n\rNamedLinkLike\x12\x0c\n\x04name\x18\x01 \x01(\t\x12#\n\x05value\x18\x02 \x01(\x0b2\x14.edgir.elem.LinkLike"\x95\x02\n\x04Port\x12(\n\x06params\x18( \x03(\x0b2\x18.edgir.elem.NamedValInit\x12/\n\x0bconstraints\x18) \x03(\x0b2\x1a.edgir.elem.NamedValueExpr\x12*\n\nself_class\x18\x14 \x01(\x0b2\x16.edgir.ref.LibraryPath\x12,\n\x0csuperclasses\x18\x15 \x03(\x0b2\x16.edgir.ref.LibraryPath\x122\n\x12super_superclasses\x18\x18 \x03(\x0b2\x16.edgir.ref.LibraryPath\x12$\n\x04meta\x18\x7f \x01(\x0b2\x16.edgir.common.Metadata"\xc1\x02\n\x06Bundle\x12(\n\x06params\x18( \x03(\x0b2\x18.edgir.elem.NamedValInit\x12(\n\x05ports\x18) \x03(\x0b2\x19.edgir.elem.NamedPortLike\x12/\n\x0bconstraints\x18* \x03(\x0b2\x1a.edgir.elem.NamedValueExpr\x12*\n\nself_class\x18\x14 \x01(\x0b2\x16.edgir.ref.LibraryPath\x12,\n\x0csuperclasses\x18\x15 \x03(\x0b2\x16.edgir.ref.LibraryPath\x122\n\x12super_superclasses\x18\x18 \x03(\x0b2\x16.edgir.ref.LibraryPath\x12$\n\x04meta\x18\x7f \x01(\x0b2\x16.edgir.common.Metadata"\xca\x01\n\tPortArray\x12*\n\nself_class\x18\x14 \x01(\x0b2\x16.edgir.ref.LibraryPath\x12,\n\x05ports\x18\x0e \x01(\x0b2\x1b.edgir.elem.PortArray.PortsH\x00\x12$\n\x04meta\x18\x7f \x01(\x0b2\x16.edgir.common.Metadata\x1a1\n\x05Ports\x12(\n\x05ports\x18( \x03(\x0b2\x19.edgir.elem.NamedPortLikeB\n\n\x08contains"\xd6\x01\n\x08PortLike\x12(\n\tundefined\x18\x01 \x01(\x0b2\x13.edgir.common.EmptyH\x00\x12*\n\x08lib_elem\x18\x02 \x01(\x0b2\x16.edgir.ref.LibraryPathH\x00\x12 \n\x04port\x18\x03 \x01(\x0b2\x10.edgir.elem.PortH\x00\x12&\n\x05array\x18\x04 \x01(\x0b2\x15.edgir.elem.PortArrayH\x00\x12$\n\x06bundle\x18\x06 \x01(\x0b2\x12.edgir.elem.BundleH\x00B\x04\n\x02is"=\n\tParameter\x12"\n\x04path\x18\x01 \x01(\x0b2\x14.edgir.ref.LocalPath\x12\x0c\n\x04unit\x18\x02 \x01(\t"a\n\x18StringDescriptionElement\x12\x0e\n\x04text\x18\x01 \x01(\tH\x00\x12&\n\x05param\x18\x02 \x01(\x0b2\x15.edgir.elem.ParameterH\x00B\r\n\x0bElementType"\xc4\x06\n\x0eHierarchyBlock\x12(\n\x06params\x18( \x03(\x0b2\x18.edgir.elem.NamedValInit\x12E\n\x0eparam_defaults\x18\x0f \x03(\x0b2-.edgir.elem.HierarchyBlock.ParamDefaultsEntry\x12(\n\x05ports\x18) \x03(\x0b2\x19.edgir.elem.NamedPortLike\x12*\n\x06blocks\x18* \x03(\x0b2\x1a.edgir.elem.NamedBlockLike\x12(\n\x05links\x18+ \x03(\x0b2\x19.edgir.elem.NamedLinkLike\x12/\n\x0bconstraints\x18, \x03(\x0b2\x1a.edgir.elem.NamedValueExpr\x12*\n\nself_class\x18\x17 \x01(\x0b2\x16.edgir.ref.LibraryPath\x12,\n\x0csuperclasses\x18\x14 \x03(\x0b2\x16.edgir.ref.LibraryPath\x122\n\x12super_superclasses\x18\x18 \x03(\x0b2\x16.edgir.ref.LibraryPath\x12/\n\x0fprerefine_class\x18\x15 \x01(\x0b2\x16.edgir.ref.LibraryPath\x120\n\x10prerefine_mixins\x18\x19 \x03(\x0b2\x16.edgir.ref.LibraryPath\x12(\n\tgenerator\x18\x16 \x01(\x0b2\x15.edgir.elem.Generator\x12\x13\n\x0bis_abstract\x18\x1e \x01(\x08\x122\n\x12default_refinement\x18\x1f \x01(\x0b2\x16.edgir.ref.LibraryPath\x12$\n\x04meta\x18\x7f \x01(\x0b2\x16.edgir.common.Metadata\x129\n\x0bdescription\x18\x01 \x03(\x0b2$.edgir.elem.StringDescriptionElement\x1aK\n\x12ParamDefaultsEntry\x12\x0b\n\x03key\x18\x01 \x01(\t\x12$\n\x05value\x18\x02 \x01(\x0b2\x15.edgir.expr.ValueExpr:\x028\x01":\n\tGenerator\x12-\n\x0frequired_params\x18\x02 \x03(\x0b2\x14.edgir.ref.LocalPath"\\\n\x0cBlockLibrary\x12$\n\x04base\x18\x02 \x01(\x0b2\x16.edgir.ref.LibraryPath\x12&\n\x06mixins\x18\x03 \x03(\x0b2\x16.edgir.ref.LibraryPath"\x9c\x01\n\tBlockLike\x12(\n\tundefined\x18\x01 \x01(\x0b2\x13.edgir.common.EmptyH\x00\x12,\n\x08lib_elem\x18\x05 \x01(\x0b2\x18.edgir.elem.BlockLibraryH\x00\x12/\n\thierarchy\x18\x04 \x01(\x0b2\x1a.edgir.elem.HierarchyBlockH\x00B\x06\n\x04type"\xa4\x03\n\x04Link\x12(\n\x06params\x18( \x03(\x0b2\x18.edgir.elem.NamedValInit\x12(\n\x05ports\x18) \x03(\x0b2\x19.edgir.elem.NamedPortLike\x12(\n\x05links\x18+ \x03(\x0b2\x19.edgir.elem.NamedLinkLike\x12/\n\x0bconstraints\x18* \x03(\x0b2\x1a.edgir.elem.NamedValueExpr\x12*\n\nself_class\x18\x14 \x01(\x0b2\x16.edgir.ref.LibraryPath\x12,\n\x0csuperclasses\x18\x15 \x03(\x0b2\x16.edgir.ref.LibraryPath\x122\n\x12super_superclasses\x18\x18 \x03(\x0b2\x16.edgir.ref.LibraryPath\x12$\n\x04meta\x18\x7f \x01(\x0b2\x16.edgir.common.Metadata\x129\n\x0bdescription\x18\x01 \x03(\x0b2$.edgir.elem.StringDescriptionElement"\xe2\x01\n\tLinkArray\x12*\n\nself_class\x18\x14 \x01(\x0b2\x16.edgir.ref.LibraryPath\x12(\n\x05ports\x18) \x03(\x0b2\x19.edgir.elem.NamedPortLike\x12/\n\x0bconstraints\x18* \x03(\x0b2\x1a.edgir.elem.NamedValueExpr\x12(\n\x05links\x18+ \x03(\x0b2\x19.edgir.elem.NamedLinkLike\x12$\n\x04meta\x18\x7f \x01(\x0b2\x16.edgir.common.Metadata"\xb2\x01\n\x08LinkLike\x12(\n\tundefined\x18\x01 \x01(\x0b2\x13.edgir.common.EmptyH\x00\x12*\n\x08lib_elem\x18\x02 \x01(\x0b2\x16.edgir.ref.LibraryPathH\x00\x12 \n\x04link\x18\x03 \x01(\x0b2\x10.edgir.elem.LinkH\x00\x12&\n\x05array\x18\x04 \x01(\x0b2\x15.edgir.elem.LinkArrayH\x00B\x06\n\x04typeb\x06proto3')
_builder.BuildMessageAndEnumDescriptors(DESCRIPTOR, globals())
_builder.BuildTopDescriptorsAndMessages(DESCRIPTOR, 'edgir.elem_pb2', globals())
if _descriptor._USE_C_DESCRIPTORS == False:
    DESCRIPTOR._options = None
    _HIERARCHYBLOCK_PARAMDEFAULTSENTRY._options = None
    _HIERARCHYBLOCK_PARAMDEFAULTSENTRY._serialized_options = b'8\x01'
    _NAMEDVALINIT._serialized_start = 105
    _NAMEDVALINIT._serialized_end = 169
    _NAMEDVALUEEXPR._serialized_start = 171
    _NAMEDVALUEEXPR._serialized_end = 239
    _NAMEDPORTLIKE._serialized_start = 241
    _NAMEDPORTLIKE._serialized_end = 307
    _NAMEDBLOCKLIKE._serialized_start = 309
    _NAMEDBLOCKLIKE._serialized_end = 377
    _NAMEDLINKLIKE._serialized_start = 379
    _NAMEDLINKLIKE._serialized_end = 445
    _PORT._serialized_start = 448
    _PORT._serialized_end = 725
    _BUNDLE._serialized_start = 728
    _BUNDLE._serialized_end = 1049
    _PORTARRAY._serialized_start = 1052
    _PORTARRAY._serialized_end = 1254
    _PORTARRAY_PORTS._serialized_start = 1193
    _PORTARRAY_PORTS._serialized_end = 1242
    _PORTLIKE._serialized_start = 1257
    _PORTLIKE._serialized_end = 1471
    _PARAMETER._serialized_start = 1473
    _PARAMETER._serialized_end = 1534
    _STRINGDESCRIPTIONELEMENT._serialized_start = 1536
    _STRINGDESCRIPTIONELEMENT._serialized_end = 1633
    _HIERARCHYBLOCK._serialized_start = 1636
    _HIERARCHYBLOCK._serialized_end = 2472
    _HIERARCHYBLOCK_PARAMDEFAULTSENTRY._serialized_start = 2397
    _HIERARCHYBLOCK_PARAMDEFAULTSENTRY._serialized_end = 2472
    _GENERATOR._serialized_start = 2474
    _GENERATOR._serialized_end = 2532
    _BLOCKLIBRARY._serialized_start = 2534
    _BLOCKLIBRARY._serialized_end = 2626
    _BLOCKLIKE._serialized_start = 2629
    _BLOCKLIKE._serialized_end = 2785
    _LINK._serialized_start = 2788
    _LINK._serialized_end = 3208
    _LINKARRAY._serialized_start = 3211
    _LINKARRAY._serialized_end = 3437
    _LINKLIKE._serialized_start = 3440
    _LINKLIKE._serialized_end = 3618