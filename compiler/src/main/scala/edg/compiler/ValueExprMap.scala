package edg.compiler

import edgir.lit.lit
import edgir.ref.ref
import edgir.expr.expr

/** Generic map/reduce utility for ValueExpr, with user-defined methods to map each type. By default, types raise an
  * exception, and must be overridden to do something useful. May be called multiple times.
  */
trait ValueExprMap[OutputType] {
  def map(valueExpr: expr.ValueExpr): OutputType = {
    valueExpr.expr match {
      case expr.ValueExpr.Expr.Literal(valueExpr) => mapLiteral(valueExpr) // no recursion, so direct map call
      case expr.ValueExpr.Expr.Binary(valueExpr) => wrapBinary(valueExpr)
      case expr.ValueExpr.Expr.BinarySet(valueExpr) => wrapBinarySet(valueExpr)
      case expr.ValueExpr.Expr.Unary(valueExpr) => wrapUnary(valueExpr)
      case expr.ValueExpr.Expr.UnarySet(valueExpr) => wrapUnarySet(valueExpr)
      case expr.ValueExpr.Expr.Array(valueExpr) => wrapArray(valueExpr)
      case expr.ValueExpr.Expr.Struct(valueExpr) => wrapStruct(valueExpr)
      case expr.ValueExpr.Expr.Range(valueExpr) => wrapRange(valueExpr)
      case expr.ValueExpr.Expr.IfThenElse(valueExpr) => wrapIfThenElse(valueExpr)
      case expr.ValueExpr.Expr.Extract(valueExpr) => wrapExtract(valueExpr)
      case expr.ValueExpr.Expr.MapExtract(valueExpr) => wrapMapExtract(valueExpr)
      case expr.ValueExpr.Expr.Connected(valueExpr) => wrapConnected(valueExpr)
      case expr.ValueExpr.Expr.Exported(valueExpr) => wrapExported(valueExpr)
      case expr.ValueExpr.Expr.ConnectedArray(valueExpr) => wrapConnectedArray(valueExpr)
      case expr.ValueExpr.Expr.ExportedArray(valueExpr) => wrapExportedArray(valueExpr)
      case expr.ValueExpr.Expr.ExportedTunnel(valueExpr) => wrapExportedTunnel(valueExpr)
      case expr.ValueExpr.Expr.Assign(valueExpr) => wrapAssign(valueExpr)
      case expr.ValueExpr.Expr.AssignTunnel(valueExpr) => wrapAssignTunnel(valueExpr)
      case expr.ValueExpr.Expr.Ref(valueExpr) => mapRef(valueExpr)
      case _ => throw new NotImplementedError(s"Unknown valueExpr $valueExpr")
    }
  }

  // These methods handle how nodes are processed must be overridden by the user where appropriate
  // (left default, they will exception out, which may be desired behavior on unexpected node types)
  def mapLiteral(literal: lit.ValueLit): OutputType =
    throw new NotImplementedError(s"Undefined mapLiteral for $literal")
  def mapBinary(binary: expr.BinaryExpr, lhs: OutputType, rhs: OutputType): OutputType =
    throw new NotImplementedError(s"Undefined mapBinary for $binary")
  def mapBinarySet(binarySet: expr.BinarySetExpr, lhsset: OutputType, rhs: OutputType): OutputType =
    throw new NotImplementedError(s"Undefined mapBinarySet for $binarySet")
  def mapUnary(unary: expr.UnaryExpr, `val`: OutputType): OutputType =
    throw new NotImplementedError(s"Undefined mapUnary for $unary")
  def mapUnarySet(unarySet: expr.UnarySetExpr, vals: OutputType): OutputType =
    throw new NotImplementedError(s"Undefined mapBinarySet for $unarySet")
  def mapArray(array: expr.ArrayExpr, vals: Seq[OutputType]): OutputType =
    throw new NotImplementedError(s"Undefined mapArray for $array")
  def mapStruct(struct: expr.StructExpr, vals: Map[String, OutputType]): OutputType =
    throw new NotImplementedError(s"Undefined mapStruct for $struct")
  def mapRange(range: expr.RangeExpr, minimum: OutputType, maximum: OutputType): OutputType =
    throw new NotImplementedError(s"Undefined mapRange for $range")
  def mapIfThenElse(ite: expr.IfThenElseExpr, cond: OutputType, tru: OutputType, fal: OutputType): OutputType =
    throw new NotImplementedError(s"Undefined mapIfThenElse for $ite")
  def mapExtract(extract: expr.ExtractExpr, container: OutputType, index: OutputType): OutputType =
    throw new NotImplementedError(s"Undefined mapExtract for $extract")
  def mapMapExtract(mapExtract: expr.MapExtractExpr): OutputType =
    throw new NotImplementedError(s"Undefined mapMapExtract for $mapExtract")
  // for non-array connect and export: expanded returns container if expanded is empty, recursively running once
  def mapConnected(
      connected: expr.ConnectedExpr,
      blockPort: OutputType,
      linkPort: OutputType,
      expandedBlockPort: OutputType,
      expandedLinkPort: OutputType
  ): OutputType =
    throw new NotImplementedError(s"Undefined mapConnected for $connected")
  def mapExported(
      exported: expr.ExportedExpr,
      exteriorPort: OutputType,
      internalBlockPort: OutputType,
      expandedExteriorPort: OutputType,
      expandedInternalBlockPort: OutputType
  ): OutputType =
    throw new NotImplementedError(s"Undefined mapExported for $exported")
  // for array connect and export: expanded is empty is expanded is empty
  def mapConnectedArray(
      connected: expr.ConnectedExpr,
      blockPort: OutputType,
      linkPort: OutputType,
      expandedBlockPort: Seq[OutputType],
      expandedLinkPort: Seq[OutputType]
  ): OutputType =
    throw new NotImplementedError(s"Undefined mapConnectedArray for $connected")
  def mapExportedArray(
      exported: expr.ExportedExpr,
      exteriorPort: OutputType,
      internalBlockPort: OutputType,
      expandedExteriorPort: Seq[OutputType],
      expandedInternalBlockPort: Seq[OutputType]
  ): OutputType =
    throw new NotImplementedError(s"Undefined mapExportedArray for $exported")
  def mapExportedTunnel(
      exported: expr.ExportedExpr,
      exteriorPort: OutputType,
      internalBlockPort: OutputType,
      expandedExteriorPort: OutputType,
      expandedInternalBlockPort: OutputType
  ): OutputType =
    throw new NotImplementedError(s"Undefined mapExportedTunnel for $exported")
  def mapAssign(assign: expr.AssignExpr, src: OutputType): OutputType =
    throw new NotImplementedError(s"Undefined mapAssign for $assign")
  def mapAssignTunnel(assign: expr.AssignExpr, src: OutputType): OutputType =
    throw new NotImplementedError(s"Undefined mapAssignTunnel for $assign")
  def mapRef(path: ref.LocalPath): OutputType =
    throw new NotImplementedError(s"Undefined mapRef for $path")

  // These methods provide default recursive processing functionality for child ValueExprs, and may be overridden.
  def wrapBinary(binary: expr.BinaryExpr): OutputType = {
    mapBinary(binary, map(binary.lhs.get), map(binary.rhs.get))
  }
  def wrapBinarySet(binarySet: expr.BinarySetExpr): OutputType = {
    mapBinarySet(binarySet, map(binarySet.lhset.get), map(binarySet.rhs.get))
  }
  def wrapUnary(unary: expr.UnaryExpr): OutputType = {
    mapUnary(unary, map(unary.`val`.get))
  }
  def wrapUnarySet(unarySet: expr.UnarySetExpr): OutputType = {
    mapUnarySet(unarySet, map(unarySet.vals.get))
  }
  def wrapArray(array: expr.ArrayExpr): OutputType = {
    mapArray(array, array.vals.map(value => map(value)))
  }
  def wrapStruct(struct: expr.StructExpr): OutputType = {
    mapStruct(struct, struct.vals.view.mapValues(value => map(value)).toMap)
  }
  def wrapRange(range: expr.RangeExpr): OutputType = {
    mapRange(range, map(range.minimum.get), map(range.maximum.get))
  }
  def wrapIfThenElse(ite: expr.IfThenElseExpr): OutputType = {
    mapIfThenElse(ite, map(ite.cond.get), map(ite.tru.get), map(ite.fal.get))
  }
  def wrapExtract(extract: expr.ExtractExpr): OutputType = {
    mapExtract(extract, map(extract.container.get), map(extract.index.get))
  }
  def wrapMapExtract(mapExtract: expr.MapExtractExpr): OutputType = {
    mapMapExtract(mapExtract)
  }
  def wrapConnected(connected: expr.ConnectedExpr): OutputType = {
    val containerBlockValue = map(connected.blockPort.get)
    val containerLinkValue = map(connected.linkPort.get)
    val expandedBlockValue = connected.expanded match {
      case Seq() => containerBlockValue
      case Seq(expanded) => map(expanded.getBlockPort)
      case _ => throw new IllegalArgumentException
    }
    val expandedLinkValue = connected.expanded match {
      case Seq() => containerLinkValue
      case Seq(expanded) => map(expanded.getLinkPort)
      case _ => throw new IllegalArgumentException
    }
    mapConnected(connected, containerBlockValue, containerLinkValue, expandedBlockValue, expandedLinkValue)
  }
  def wrapExported(exported: expr.ExportedExpr): OutputType = {
    val containerExteriorValue = map(exported.exteriorPort.get)
    val containerInteriorValue = map(exported.internalBlockPort.get)
    val expandedExteriorValue = exported.expanded match {
      case Seq() => containerExteriorValue
      case Seq(expanded) => map(expanded.getExteriorPort)
      case _ => throw new IllegalArgumentException
    }
    val expandedInteriorValue = exported.expanded match {
      case Seq() => containerInteriorValue
      case Seq(expanded) => map(expanded.getInternalBlockPort)
      case _ => throw new IllegalArgumentException
    }
    mapExported(exported, containerExteriorValue, containerInteriorValue, expandedExteriorValue, expandedInteriorValue)
  }
  def wrapConnectedArray(connected: expr.ConnectedExpr): OutputType = {
    mapConnectedArray(
      connected,
      map(connected.blockPort.get),
      map(connected.linkPort.get),
      connected.expanded.map(expanded => map(expanded.getBlockPort)),
      connected.expanded.map(expanded => map(expanded.getLinkPort))
    )
  }
  def wrapExportedArray(exported: expr.ExportedExpr): OutputType = {
    mapExportedArray(
      exported,
      map(exported.exteriorPort.get),
      map(exported.internalBlockPort.get),
      exported.expanded.map(expanded => map(expanded.getExteriorPort)),
      exported.expanded.map(expanded => map(expanded.getInternalBlockPort))
    )
  }
  def wrapExportedTunnel(exported: expr.ExportedExpr): OutputType = {
    val containerExteriorValue = map(exported.exteriorPort.get)
    val containerInteriorValue = map(exported.internalBlockPort.get)
    val expandedExteriorValue = exported.expanded match {
      case Seq() => containerExteriorValue
      case Seq(expanded) => map(expanded.getExteriorPort)
      case _ => throw new IllegalArgumentException
    }
    val expandedInteriorValue = exported.expanded match {
      case Seq() => containerInteriorValue
      case Seq(expanded) => map(expanded.getInternalBlockPort)
      case _ => throw new IllegalArgumentException
    }
    mapExportedTunnel(
      exported,
      containerExteriorValue,
      containerInteriorValue,
      expandedExteriorValue,
      expandedInteriorValue
    )
  }
  def wrapAssign(assign: expr.AssignExpr): OutputType = {
    mapAssign(assign, map(assign.src.get))
  }
  def wrapAssignTunnel(assign: expr.AssignExpr): OutputType = {
    mapAssign(assign, map(assign.src.get))
  }
}
