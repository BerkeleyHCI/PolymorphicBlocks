package edg.compiler

import edgir.expr.expr
import edgir.lit.lit
import edgir.ref.ref
import edg.wir.{DesignPath, IndirectDesignPath, IndirectStep}


sealed trait ExprResult

object ExprResult {
  case class Result(value: ExprValue) extends ExprResult
  case class Missing(refs: Set[IndirectDesignPath]) extends ExprResult
}


class ExprEvaluatePartial(refs: ConstProp, root: DesignPath) extends ValueExprMap[ExprResult] {
  override def mapLiteral(literal: lit.ValueLit): ExprResult =
    ExprResult.Result(ExprEvaluate.evalLiteral(literal))

  override def mapBinary(binary: expr.BinaryExpr,
                         lhs: ExprResult, rhs: ExprResult): ExprResult = (lhs, rhs) match {
    case (ExprResult.Missing(lhs), ExprResult.Missing(rhs)) => ExprResult.Missing(lhs ++ rhs)
    case (lhs @ ExprResult.Missing(_), ExprResult.Result(_)) => lhs
    case (ExprResult.Result(_), rhs @ ExprResult.Missing(_)) => rhs
    case (ExprResult.Result(lhs), ExprResult.Result(rhs)) =>
      ExprResult.Result(ExprEvaluate.evalBinary(binary, lhs, rhs))
  }

  override def mapBinarySet(binarySet: expr.BinarySetExpr,
                            lhsset: ExprResult, rhs: ExprResult): ExprResult = (lhsset, rhs) match {
    case (ExprResult.Missing(lhsset), ExprResult.Missing(rhs)) => ExprResult.Missing(lhsset ++ rhs)
    case (lhsset @ ExprResult.Missing(_), ExprResult.Result(_)) => lhsset
    case (ExprResult.Result(_), rhs @ ExprResult.Missing(_)) => rhs
    case (ExprResult.Result(lhsset), ExprResult.Result(rhs)) =>
      ExprResult.Result(ExprEvaluate.evalBinarySet(binarySet, lhsset, rhs))
  }

  override def mapUnary(unary: expr.UnaryExpr, `val`: ExprResult): ExprResult = `val` match {
    case `val` @ ExprResult.Missing(_) => `val`
    case ExprResult.Result(resVal) => ExprResult.Result(ExprEvaluate.evalUnary(unary, resVal))
  }

  override def mapUnarySet(unarySet: expr.UnarySetExpr, vals: ExprResult): ExprResult = vals match {
    case vals @ ExprResult.Missing(_) => vals
    case ExprResult.Result(vals) => ExprResult.Result(ExprEvaluate.evalUnarySet(unarySet, vals))
  }

  override def mapStruct(struct: expr.StructExpr, vals: Map[String, ExprResult]): ExprResult =
    ???

  override def mapRange(range: expr.RangeExpr,
                        minimum: ExprResult, maximum: ExprResult): ExprResult = (minimum, maximum) match {
    case (ExprResult.Missing(minimum), ExprResult.Missing(maximum)) => ExprResult.Missing(minimum ++ maximum)
    case (minimum @ ExprResult.Missing(_), ExprResult.Result(_)) => minimum
    case (ExprResult.Result(_), maximum @ ExprResult.Missing(_)) => maximum
    case (ExprResult.Result(minimum), ExprResult.Result(maximum)) =>
      ExprResult.Result(ExprEvaluate.evalRange(range, minimum, maximum))
  }

  override def mapIfThenElse(ite: expr.IfThenElseExpr, cond: ExprResult,
                             tru: ExprResult, fal: ExprResult): ExprResult = (cond, tru, fal) match {
    case (cond @ ExprResult.Missing(_), _, _) => cond  // only report condition missing
      // For If-Then-Else, don't depend on or require the untaken branch
    case (ExprResult.Result(cond @ BooleanValue(true)), tru, _) => tru match {
      case tru @ ExprResult.Missing(_) => tru
      case ExprResult.Result(tru) => ExprResult.Result(ExprEvaluate.evalIfThenElse(ite, cond, tru, tru))
    }
    case (ExprResult.Result(cond @ BooleanValue(false)), _, fal) => fal match {
      case fal @ ExprResult.Missing(_) => fal
      case ExprResult.Result(fal) => ExprResult.Result(ExprEvaluate.evalIfThenElse(ite, cond, fal, fal))
    }
    case (ExprResult.Result(cond), _, _) =>
      throw new ExprEvaluateException(s"Unknown condition $cond for $ite")
  }

  override def mapExtract(extract: expr.ExtractExpr,
                          container: ExprResult, index: ExprResult): ExprResult = (container, index) match {
    case (ExprResult.Missing(container), ExprResult.Missing(index)) => ExprResult.Missing(container ++ index)
    case (container @ ExprResult.Missing(_), ExprResult.Result(_)) => container
    case (ExprResult.Result(_), index @ ExprResult.Missing(_)) => index
    case (ExprResult.Result(container), ExprResult.Result(index)) =>
      ExprResult.Result(ExprEvaluate.evalExtract(extract, container, index))
  }

  override def mapMapExtract(mapExtract: expr.MapExtractExpr): ExprResult = {
    // TODO dedup w/ ExprEvaluate
    val container = mapExtract.getContainer.expr.ref.getOrElse(  // TODO restrict allowed types in proto
      throw new ExprEvaluateException(s"Non-ref container type in mapExtract $mapExtract")
    )
    val containerPath = root ++ container
    refs.getValue(containerPath.asIndirect + IndirectStep.Elements) match {
      case Some(paramValue) =>
        val eltsVals = ArrayValue.ExtractText(paramValue).map { elt =>
          val eltPath = containerPath.asIndirect + elt ++ mapExtract.getPath
          refs.getValue(eltPath) match {
            case Some(value) => ExprResult.Result(value)
            case None => ExprResult.Missing(Set(eltPath))
        }}
        if (eltsVals.forall(_.isInstanceOf[ExprResult.Result])) {
          val values = eltsVals.map { _.asInstanceOf[ExprResult.Result].value }
          ExprResult.Result(ArrayValue(values))
        } else {
          val missings = eltsVals.collect { case ExprResult.Missing(refs) => refs }
          ExprResult.Missing(missings.flatten.toSet)
        }
      case None => ExprResult.Missing(Set(containerPath.asIndirect + IndirectStep.Elements))
    }
  }

  // connected and exported not overridden and to fail noisily
  // assign also not overridden and to fail noisily

  override def mapRef(path: ref.LocalPath): ExprResult = {
    val refPath = root.asIndirect ++ path
    refs.getValue(refPath) match {
      case Some(value) => ExprResult.Result(value)
      case None => ExprResult.Missing(Set(refPath))
    }
  }
}
