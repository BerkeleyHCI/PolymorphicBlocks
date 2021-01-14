package edg.compiler

import edg.lit.lit
import edg.ref.ref
import edg.expr.expr


class UnimplementedValueExprNode(message: String) extends Exception(message)


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
      case expr.ValueExpr.Expr.Reduce(valueExpr) => wrapReduce(valueExpr)
      case expr.ValueExpr.Expr.Struct(valueExpr) => wrapStruct(valueExpr)
      case expr.ValueExpr.Expr.Range(valueExpr) => wrapRange(valueExpr)
      case expr.ValueExpr.Expr.IfThenElse(valueExpr) => wrapIfThenElse(valueExpr)
      case expr.ValueExpr.Expr.Extract(valueExpr) => wrapExtract(valueExpr)
      case expr.ValueExpr.Expr.MapExtract(valueExpr) => wrapMapExtract(valueExpr)
      case expr.ValueExpr.Expr.Connected(valueExpr) => wrapConnected(valueExpr)
      case expr.ValueExpr.Expr.Exported(valueExpr) => wrapExported(valueExpr)
      case expr.ValueExpr.Expr.Assign(valueExpr) => wrapAssign(valueExpr)
      case expr.ValueExpr.Expr.Ref(valueExpr) => mapRef(valueExpr)
    }
  }

  // These methods handle how nodes are processed must be overridden by the user where appropriate
  // (left default, they will exception out, which may be desired behavior on unexpected node types)
  def mapLiteral(literal: lit.ValueLit): OutputType =
    throw new UnimplementedValueExprNode(s"Undefined mapLiteral for $literal")
  def mapBinary(binary: expr.BinaryExpr, lhs: OutputType, rhs: OutputType): OutputType =
    throw new UnimplementedValueExprNode(s"Undefined mapBinary for $binary")
  def mapReduce(reduce: expr.ReductionExpr, vals: OutputType): OutputType =
    throw new UnimplementedValueExprNode(s"Undefined mapReduce for $reduce")
  def mapStruct(struct: expr.StructExpr, vals: Map[String, OutputType]): OutputType =
    throw new UnimplementedValueExprNode(s"Undefined mapStruct for $struct")
  def mapRange(range: expr.RangeExpr, minimum: OutputType, maximum: OutputType): OutputType =
    throw new UnimplementedValueExprNode(s"Undefined mapRange for $range")
  def mapIfThenElse(ite: expr.IfThenElseExpr, cond: OutputType, tru: OutputType, fal: OutputType): OutputType =
    throw new UnimplementedValueExprNode(s"Undefined mapIfThenElse for $ite")
  def mapExtract(extract: expr.ExtractExpr, container: OutputType, index: OutputType): OutputType =
    throw new UnimplementedValueExprNode(s"Undefined mapExtract for $extract")
  def mapMapExtract(mapExtract: expr.MapExtractExpr): OutputType =
    throw new UnimplementedValueExprNode(s"Undefined mapMapExtract for $mapExtract")
  def mapConnected(connected: expr.ConnectedExpr, blockPort: OutputType, linkPort: OutputType): OutputType =
    throw new UnimplementedValueExprNode(s"Undefined mapConnected for $connected")
  def mapExported(exported: expr.ExportedExpr, exteriorPort: OutputType, internalBlockPort: OutputType): OutputType =
    throw new UnimplementedValueExprNode(s"Undefined mapExported for $exported")
  def mapAssign(assign: expr.AssignExpr, src: OutputType): OutputType =
    throw new UnimplementedValueExprNode(s"Undefined mapAssign for $assign")
  def mapRef(path: ref.LocalPath): OutputType =
    throw new UnimplementedValueExprNode(s"Undefined mapRef for $path")

  // These methods provide default recursive processing functionality for child ValueExprs, and may be overridden.
  def wrapBinary(binary: expr.BinaryExpr): OutputType = {
    mapBinary(binary, map(binary.lhs.get), map(binary.rhs.get))
  }
  def wrapReduce(reduce: expr.ReductionExpr): OutputType = {
    mapReduce(reduce, map(reduce.vals.get))
  }
  def wrapStruct(struct: expr.StructExpr): OutputType = {
    mapStruct(struct, struct.vals.mapValues(value => map(value)))
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
