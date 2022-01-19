package edg.compiler

import edgir.lit.lit
import edgir.ref.ref
import edgir.expr.expr


/**
  * Generic map/reduce utility for ValueExpr, with user-defined methods to map each type.
  * By default, types raise an exception, and must be overridden to do something useful.
  * May be called multiple times.
  */
trait ValueExprMap[OutputType] {
  def map(valueExpr: expr.ValueExpr): OutputType = {
    valueExpr.expr match {
      case expr.ValueExpr.Expr.Literal(valueExpr) => mapLiteral(valueExpr)  // no recursion, so direct map call
      case expr.ValueExpr.Expr.Binary(valueExpr) => wrapBinary(valueExpr)
      case expr.ValueExpr.Expr.BinarySet(valueExpr) => wrapBinarySet(valueExpr)
      case expr.ValueExpr.Expr.Unary(valueExpr) => wrapUnary(valueExpr)
      case expr.ValueExpr.Expr.UnarySet(valueExpr) => wrapUnarySet(valueExpr)
      case expr.ValueExpr.Expr.Struct(valueExpr) => wrapStruct(valueExpr)
      case expr.ValueExpr.Expr.Range(valueExpr) => wrapRange(valueExpr)
      case expr.ValueExpr.Expr.IfThenElse(valueExpr) => wrapIfThenElse(valueExpr)
      case expr.ValueExpr.Expr.Extract(valueExpr) => wrapExtract(valueExpr)
      case expr.ValueExpr.Expr.MapExtract(valueExpr) => wrapMapExtract(valueExpr)
      case expr.ValueExpr.Expr.Connected(valueExpr) => wrapConnected(valueExpr)
      case expr.ValueExpr.Expr.Exported(valueExpr) => wrapExported(valueExpr)
      case expr.ValueExpr.Expr.Assign(valueExpr) => wrapAssign(valueExpr)
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
  def mapConnected(connected: expr.ConnectedExpr, blockPort: OutputType, linkPort: OutputType): OutputType =
    throw new NotImplementedError(s"Undefined mapConnected for $connected")
  def mapExported(exported: expr.ExportedExpr, exteriorPort: OutputType, internalBlockPort: OutputType): OutputType =
    throw new NotImplementedError(s"Undefined mapExported for $exported")
  def mapAssign(assign: expr.AssignExpr, src: OutputType): OutputType =
    throw new NotImplementedError(s"Undefined mapAssign for $assign")
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
    mapConnected(connected, map(connected.blockPort.get), map(connected.linkPort.get))
  }
  def wrapExported(exported: expr.ExportedExpr): OutputType = {
    mapExported(exported, map(exported.exteriorPort.get), map(exported.internalBlockPort.get))
  }
  def wrapAssign(assign: expr.AssignExpr): OutputType = {
    mapAssign(assign, map(assign.src.get))
  }
}
