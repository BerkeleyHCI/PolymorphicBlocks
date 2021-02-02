package edg.compiler

import edg.expr.expr
import edg.lit.lit
import edg.ref.ref
import edg.wir.{DesignPath, IndirectDesignPath}

import scala.collection.Set


/**
  * ValueExpr transform that returns the parameter (ref) dependencies.
  */
class ExprRefDependencies(refs: ConstProp, root: DesignPath) extends ValueExprMap[Set[IndirectDesignPath]] {
  override def mapLiteral(literal: lit.ValueLit): Set[IndirectDesignPath] = Set()

  override def mapBinary(binary: expr.BinaryExpr,
                         lhs: Set[IndirectDesignPath], rhs: Set[IndirectDesignPath]): Set[IndirectDesignPath] =
    lhs ++ rhs

  override def mapReduce(reduce: expr.ReductionExpr, vals: Set[IndirectDesignPath]): Set[IndirectDesignPath] = vals

  override def mapStruct(struct: expr.StructExpr, vals: Map[String, Set[IndirectDesignPath]]): Set[IndirectDesignPath] =
    vals.values.flatten.toSet

  override def mapRange(range: expr.RangeExpr,
                        minimum: Set[IndirectDesignPath], maximum: Set[IndirectDesignPath]): Set[IndirectDesignPath] =
    minimum ++ maximum

  override def mapIfThenElse(ite: expr.IfThenElseExpr, cond: Set[IndirectDesignPath],
                             tru: Set[IndirectDesignPath], fal: Set[IndirectDesignPath]): Set[IndirectDesignPath] =
    cond ++ tru ++ fal

  override def mapExtract(extract: expr.ExtractExpr,
                          container: Set[IndirectDesignPath], index: Set[IndirectDesignPath]): Set[IndirectDesignPath] =
    container ++ index

  override def mapMapExtract(mapExtract: expr.MapExtractExpr): Set[IndirectDesignPath] = {
    val container = mapExtract.container.get.expr.ref.getOrElse(  // TODO restrict allowed types in proto
      throw new ExprEvaluateException(s"Non-ref container type in mapExtract $mapExtract")
    )
    val containerPath = root ++ container
    val elts = refs.getArrayElts(containerPath).getOrElse(
      throw new ExprEvaluateException(s"Array elts not known for $container from $mapExtract")
    )
    elts.map { elt =>
      IndirectDesignPath.fromDesignPath(containerPath) + elt ++ mapExtract.path.get
    }.toSet
  }

  // connected and exported not overridden and to fail noisily
  // assign also not overridden and to fail noisily

  override def mapRef(path: ref.LocalPath): Set[IndirectDesignPath] = {
    Set(IndirectDesignPath.fromDesignPath(root) ++ path)
  }
}

/**
  * ValueExpr transform that returns the array dependencies.
  */
class ExprArrayDependencies(root: DesignPath) extends ValueExprMap[Set[DesignPath]] {
  override def mapLiteral(literal: lit.ValueLit): Set[DesignPath] = Set()

  override def mapBinary(binary: expr.BinaryExpr,
                         lhs: Set[DesignPath], rhs: Set[DesignPath]): Set[DesignPath] =
    lhs ++ rhs

  override def mapReduce(reduce: expr.ReductionExpr, vals: Set[DesignPath]): Set[DesignPath] = vals

  override def mapStruct(struct: expr.StructExpr, vals: Map[String, Set[DesignPath]]): Set[DesignPath] =
    vals.values.flatten.toSet

  override def mapRange(range: expr.RangeExpr,
                        minimum: Set[DesignPath], maximum: Set[DesignPath]): Set[DesignPath] =
    minimum ++ maximum

  override def mapIfThenElse(ite: expr.IfThenElseExpr, cond: Set[DesignPath],
                             tru: Set[DesignPath], fal: Set[DesignPath]): Set[DesignPath] =
    cond ++ tru ++ fal

  override def mapExtract(extract: expr.ExtractExpr,
                          container: Set[DesignPath], index: Set[DesignPath]): Set[DesignPath] =
    container ++ index

  override def mapMapExtract(mapExtract: expr.MapExtractExpr): Set[DesignPath] = {
    Set(root ++ mapExtract.container.get.expr.ref.get)
  }

  // connected and exported not overridden and to fail noisily
  // assign also not overridden and to fail noisily

  override def mapRef(path: ref.LocalPath): Set[DesignPath] = Set()
}
