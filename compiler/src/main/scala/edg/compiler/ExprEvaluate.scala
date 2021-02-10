package edg.compiler

import edg.expr.expr
import edg.lit.lit
import edg.ref.ref
import edg.wir.{DesignPath, IndirectDesignPath}


class ExprEvaluateException(msg: String) extends Exception(msg)
class MissingValueException(path: IndirectDesignPath) extends ExprEvaluateException(s"Missing value $path")


/** Shared utilities to DRY evaluation of expressions
  */
object ExprEvaluate {
  def evalLiteral(literal: lit.ValueLit): ExprValue = literal.`type` match {
    case lit.ValueLit.Type.Floating(literal) => FloatValue(literal.`val`.toFloat)
    case lit.ValueLit.Type.Integer(literal) => IntValue(literal.`val`)
    case lit.ValueLit.Type.Boolean(literal) => BooleanValue(literal.`val`)
    case lit.ValueLit.Type.Text(literal) => TextValue(literal.`val`)
    case lit.ValueLit.Type.Range(literal) => (literal..getMinimum.`type`, literal.getMaximum.`type`) match {
      case (lit.ValueLit.Type.Floating(literalMin), lit.ValueLit.Type.Floating(literalMax)) =>
        RangeValue(literalMin.`val`.toFloat, literalMax.`val`.toFloat)
      case _ => throw new ExprEvaluateException(s"Malformed range literal $literal")
    }
    case _ => throw new ExprEvaluateException(s"Unknown literal $literal")
  }

  def evalBinary(binary: expr.BinaryExpr, lhs: ExprValue, rhs: ExprValue): ExprValue = binary.op match {
    // Note promotion rules: range takes precedence, then float, then int
    case expr.BinaryExpr.Op.ADD => (lhs, rhs) match {
      case (RangeValue(lhsMin, lhsMax), RangeValue(rhsMin, rhsMax)) =>
        val all = Seq(lhsMin + rhsMin, lhsMin + rhsMax, lhsMax + rhsMin, lhsMax + rhsMax)
        RangeValue(all.min, all.max)
      case (RangeValue(lhsMin, lhsMax), FloatPromotable(rhs)) =>
        RangeValue(lhsMin + rhs, lhsMax + rhs)
      case (FloatPromotable(lhs), RangeValue(rhsMin, rhsMax)) =>
        RangeValue(lhs + rhsMin, lhs + rhsMax)
      case (FloatValue(lhs), FloatPromotable(rhs)) => FloatValue(lhs + rhs)
      case (FloatPromotable(lhs), FloatValue(rhs)) => FloatValue(lhs + rhs)
      case (IntValue(lhs), IntValue(rhs)) => IntValue(lhs + rhs)
      case _ => throw new ExprEvaluateException(s"Unknown binary operand types in $lhs ${binary.op} $rhs from $binary")
    }
    case expr.BinaryExpr.Op.SUB => (lhs, rhs) match {
      case (RangeValue(lhsMin, lhsMax), RangeValue(rhsMin, rhsMax)) =>
        val all = Seq(lhsMin - rhsMin, lhsMin - rhsMax, lhsMax - rhsMin, lhsMax - rhsMax)
        RangeValue(all.min, all.max)
      case (RangeValue(lhsMin, lhsMax), FloatPromotable(rhs)) =>
        RangeValue(lhsMin - rhs, lhsMax - rhs)
      case (FloatPromotable(lhs), RangeValue(rhsMin, rhsMax)) =>
        RangeValue(lhs - rhsMin, lhs - rhsMax)
      case (FloatValue(lhs), FloatPromotable(rhs)) => FloatValue(lhs - rhs)
      case (FloatPromotable(lhs), FloatValue(rhs)) => FloatValue(lhs - rhs)
      case (IntValue(lhs), IntValue(rhs)) => IntValue(lhs - rhs)
      case _ => throw new ExprEvaluateException(s"Unknown binary operand types in $lhs ${binary.op} $rhs from $binary")
    }
    case expr.BinaryExpr.Op.MULT => (lhs, rhs) match {
      case (RangeValue(lhsMin, lhsMax), RangeValue(rhsMin, rhsMax)) =>
        val all = Seq(lhsMin * rhsMin, lhsMin * rhsMax, lhsMax * rhsMin, lhsMax * rhsMax)
        RangeValue(all.min, all.max)
      case (RangeValue(lhsMin, lhsMax), FloatPromotable(rhs)) =>
        RangeValue(lhsMin * rhs, lhsMax * rhs)
      case (FloatPromotable(lhs), RangeValue(rhsMin, rhsMax)) =>
        RangeValue(lhs * rhsMin, lhs * rhsMax)
      case (FloatValue(lhs), FloatPromotable(rhs)) => FloatValue(lhs * rhs)
      case (FloatPromotable(lhs), FloatValue(rhs)) => FloatValue(lhs * rhs)
      case (IntValue(lhs), IntValue(rhs)) => IntValue(lhs * rhs)
      case _ => throw new ExprEvaluateException(s"Unknown binary operand types in $lhs ${binary.op} $rhs from $binary")
    }
    case expr.BinaryExpr.Op.DIV => (lhs, rhs) match {
      case (RangeValue(lhsMin, lhsMax), RangeValue(rhsMin, rhsMax)) =>
        val all = Seq(lhsMin / rhsMin, lhsMin / rhsMax, lhsMax / rhsMin, lhsMax / rhsMax)
        RangeValue(all.min, all.max)
      case (RangeValue(lhsMin, lhsMax), FloatPromotable(rhs)) =>
        RangeValue(lhsMin / rhs, lhsMax / rhs)
      case (FloatPromotable(lhs), RangeValue(rhsMin, rhsMax)) =>
        RangeValue(lhs / rhsMin, lhs / rhsMax)
      case (FloatValue(lhs), FloatPromotable(rhs)) => FloatValue(lhs / rhs)
      case (FloatPromotable(lhs), FloatValue(rhs)) => FloatValue(lhs / rhs)
      case (IntValue(lhs), IntValue(rhs)) => IntValue(lhs / rhs)
      case _ => throw new ExprEvaluateException(s"Unknown binary operand types in $lhs ${binary.op} $rhs from $binary")
    }

    case expr.BinaryExpr.Op.AND => (lhs, rhs) match {
      case (BooleanValue(lhs), BooleanValue(rhs)) => BooleanValue(lhs && rhs)
      case _ => throw new ExprEvaluateException(s"Unknown binary operand types in $lhs ${binary.op} $rhs from $binary")
    }
    case expr.BinaryExpr.Op.OR => (lhs, rhs) match {
      case (BooleanValue(lhs), BooleanValue(rhs)) => BooleanValue(lhs || rhs)
      case _ => throw new ExprEvaluateException(s"Unknown binary operand types in $lhs ${binary.op} $rhs from $binary")
    }
    case expr.BinaryExpr.Op.XOR => (lhs, rhs) match {
      case (BooleanValue(lhs), BooleanValue(rhs)) => BooleanValue(lhs ^ rhs)
      case _ => throw new ExprEvaluateException(s"Unknown binary operand types in $lhs ${binary.op} $rhs from $binary")
    }
    case expr.BinaryExpr.Op.IMPLIES => (lhs, rhs) match {
      case (BooleanValue(lhs), BooleanValue(rhs)) => BooleanValue(!lhs || rhs)
      case _ => throw new ExprEvaluateException(s"Unknown binary operand types in $lhs ${binary.op} $rhs from $binary")
    }

    case expr.BinaryExpr.Op.EQ => (lhs, rhs) match {
      // TODO can optionally support Range <-> Float ops later if desired, it's a 'type error' now
      case (RangeValue(lhsMin, lhsMax), RangeValue(rhsMin, rhsMax)) =>
        BooleanValue(lhsMin == rhsMin && lhsMax == rhsMax)
      case (IntValue(lhs), IntValue(rhs)) => BooleanValue(lhs == rhs)  // prioritize int compare before promotion
      case (FloatPromotable(lhs), FloatPromotable(rhs)) => BooleanValue(lhs == rhs)
      case (BooleanValue(lhs), BooleanValue(rhs)) => BooleanValue(lhs == rhs)
      case (TextValue(lhs), TextValue(rhs)) => BooleanValue(lhs == rhs)
      case _ => throw new ExprEvaluateException(s"Unknown binary operand types in $lhs ${binary.op} $rhs from $binary")
    }
    case expr.BinaryExpr.Op.NEQ => (lhs, rhs) match {
      // TODO can optionally support Range <-> Float ops later if desired, it's a 'type error' now
      case (RangeValue(lhsMin, lhsMax), RangeValue(rhsMin, rhsMax)) =>
        BooleanValue(lhsMin != rhsMin || lhsMax != rhsMax)
      case (IntValue(lhs), IntValue(rhs)) => BooleanValue(lhs != rhs)  // prioritize int compare before promotion
      case (FloatPromotable(lhs), FloatPromotable(rhs)) => BooleanValue(lhs != rhs)
      case (BooleanValue(lhs), BooleanValue(rhs)) => BooleanValue(lhs != rhs)
      case (TextValue(lhs), TextValue(rhs)) => BooleanValue(lhs != rhs)
      case _ => throw new ExprEvaluateException(s"Unknown binary operand types in $lhs ${binary.op} $rhs from $binary")
    }

    case expr.BinaryExpr.Op.GT => (lhs, rhs) match {
      // TODO can optionally support Range <-> Float ops later if desired, it's a 'type error' now
      case (RangeValue(lhsMin, lhsMax), RangeValue(rhsMin, rhsMax)) => BooleanValue(lhsMin > rhsMax)
      case (IntValue(lhs), IntValue(rhs)) => BooleanValue(lhs > rhs) // prioritize int compare before promotion
      case (FloatPromotable(lhs), FloatPromotable(rhs)) => BooleanValue(lhs > rhs)
      case _ => throw new ExprEvaluateException(s"Unknown binary operand types in $lhs ${binary.op} $rhs from $binary")
    }
    case expr.BinaryExpr.Op.GTE => (lhs, rhs) match {
      // TODO can optionally support Range <-> Float ops later if desired, it's a 'type error' now
      case (RangeValue(lhsMin, lhsMax), RangeValue(rhsMin, rhsMax)) => BooleanValue(lhsMin >= rhsMax)
      case (IntValue(lhs), IntValue(rhs)) => BooleanValue(lhs >= rhs) // prioritize int compare before promotion
      case (FloatPromotable(lhs), FloatPromotable(rhs)) => BooleanValue(lhs >= rhs)
      case _ => throw new ExprEvaluateException(s"Unknown binary operand types in $lhs ${binary.op} $rhs from $binary")
    }
    case expr.BinaryExpr.Op.LT => (lhs, rhs) match {
      // TODO can optionally support Range <-> Float ops later if desired, it's a 'type error' now
      case (RangeValue(lhsMin, lhsMax), RangeValue(rhsMin, rhsMax)) => BooleanValue(lhsMax < rhsMin)
      case (IntValue(lhs), IntValue(rhs)) => BooleanValue(lhs < rhs) // prioritize int compare before promotion
      case (FloatPromotable(lhs), FloatPromotable(rhs)) => BooleanValue(lhs < rhs)
      case _ => throw new ExprEvaluateException(s"Unknown binary operand types in $lhs ${binary.op} $rhs from $binary")
    }
    case expr.BinaryExpr.Op.LTE => (lhs, rhs) match {
      // TODO can optionally support Range <-> Float ops later if desired, it's a 'type error' now
      case (RangeValue(lhsMin, lhsMax), RangeValue(rhsMin, rhsMax)) => BooleanValue(lhsMax <= rhsMin)
      case (IntValue(lhs), IntValue(rhs)) => BooleanValue(lhs <= rhs) // prioritize int compare before promotion
      case (FloatPromotable(lhs), FloatPromotable(rhs)) => BooleanValue(lhs <= rhs)
      case _ => throw new ExprEvaluateException(s"Unknown binary operand types in $lhs ${binary.op} $rhs from $binary")
    }

    case expr.BinaryExpr.Op.MAX => (lhs, rhs) match {
      case (IntValue(lhs), IntValue(rhs)) => IntValue(lhs.max(rhs)) // prioritize int compare before promotion
      case (FloatPromotable(lhs), FloatPromotable(rhs)) => FloatValue(math.max(lhs, rhs))
      case _ => throw new ExprEvaluateException(s"Unknown binary operand types in $lhs ${binary.op} $rhs from $binary")
    }
    case expr.BinaryExpr.Op.MIN => (lhs, rhs) match {
      case (IntValue(lhs), IntValue(rhs)) => IntValue(lhs.min(rhs)) // prioritize int compare before promotion
      case (FloatPromotable(lhs), FloatPromotable(rhs)) => FloatValue(math.min(lhs, rhs))
      case _ => throw new ExprEvaluateException(s"Unknown binary operand types in $lhs ${binary.op} $rhs from $binary")
    }

    case expr.BinaryExpr.Op.INTERSECTION => (lhs, rhs) match {
      case (RangeValue(lhsMin, lhsMax), RangeValue(rhsMin, rhsMax)) =>
        val (minMax, maxMin) = (math.min(lhsMax, rhsMax), math.max(lhsMin, rhsMin))
        if (maxMin <= minMax) {
          RangeValue(maxMin, minMax)
        } else {  // null set
          RangeValue.empty
        }
      case _ => throw new ExprEvaluateException(s"Unknown binary operand types in $lhs ${binary.op} $rhs from $binary")
    }
    case expr.BinaryExpr.Op.SUBSET => (lhs, rhs) match {  // lhs contained within rhs
      case (RangeValue(lhsMin, lhsMax), RangeValue(rhsMin, rhsMax)) =>
        BooleanValue(rhsMin <= lhsMin && rhsMax >= lhsMax)
      case (FloatPromotable(lhs), RangeValue(rhsMin, rhsMax)) =>BooleanValue(rhsMin <= lhs && rhsMax >= lhs)
      case _ => throw new ExprEvaluateException(s"Unknown binary operands types in $lhs ${binary.op} $rhs from $binary")
    }

    case expr.BinaryExpr.Op.RANGE => (lhs, rhs) match {
      case (FloatPromotable(lhs), FloatPromotable(rhs)) => RangeValue(math.min(lhs, rhs), math.max(lhs, rhs))
      case _ => throw new ExprEvaluateException(s"Unknown binary operands types in $lhs ${binary.op} $rhs from $binary")
    }

    case _ => throw new ExprEvaluateException(s"Unknown binary op in $lhs ${binary.op} $rhs from $binary")
  }

  def evalReduce(reduce: expr.ReductionExpr, vals: ExprValue): ExprValue = (reduce.op, vals) match {
    // In this case we don't do numeric promotion
    case (expr.ReductionExpr.Op.SUM, ArrayValue.ExtractFloat(vals)) => FloatValue(vals.sum)
    case (expr.ReductionExpr.Op.SUM, ArrayValue.ExtractInt(vals)) => IntValue(vals.sum)
    case (expr.ReductionExpr.Op.SUM, ArrayValue.ExtractRange(valMins, valMaxs)) => RangeValue(valMins.sum, valMaxs.sum)

    case (expr.ReductionExpr.Op.ALL_TRUE, ArrayValue.ExtractBoolean(vals)) => BooleanValue(vals.forall(_ == true))
    case (expr.ReductionExpr.Op.ANY_TRUE, ArrayValue.ExtractBoolean(vals)) => BooleanValue(vals.contains(true))

    // TODO better support for empty arrays?
    case (expr.ReductionExpr.Op.ALL_EQ, ArrayValue(vals)) => BooleanValue(vals.forall(_ == vals.head))

    case (expr.ReductionExpr.Op.ALL_UNIQUE, ArrayValue(vals)) => BooleanValue(vals.size == vals.toSet.size)

    // TODO max / min on Array[Range] is a bit of a hack (but kinda makes sense?) - perhaps should be removed
    case (expr.ReductionExpr.Op.MAXIMUM, ArrayValue.ExtractRange(valMins, valMaxs)) => FloatValue(valMaxs.max)
    case (expr.ReductionExpr.Op.MINIMUM, ArrayValue.ExtractRange(valMins, valMaxs)) => FloatValue(valMins.min)

    case (expr.ReductionExpr.Op.MAXIMUM, ArrayValue.ExtractFloat(vals)) => FloatValue(vals.max)
    case (expr.ReductionExpr.Op.MAXIMUM, ArrayValue.ExtractInt(vals)) => IntValue(vals.max)

    case (expr.ReductionExpr.Op.MINIMUM, ArrayValue.ExtractFloat(vals)) => FloatValue(vals.min)
    case (expr.ReductionExpr.Op.MINIMUM, ArrayValue.ExtractInt(vals)) => IntValue(vals.min)

    // TODO this should be a user-level assertion instead of a compiler error
    case (expr.ReductionExpr.Op.SET_EXTRACT, ArrayValue(vals)) => if (vals.forall(_ == vals.head)) {
      vals.head
    } else {
      throw new ExprEvaluateException(s"SetExtract with non-equal values $vals from $reduce")
    }

    case (expr.ReductionExpr.Op.INTERSECTION, ArrayValue.ExtractRange(valMins, valMaxs)) =>
      val (minMax, maxMin) = (valMaxs.min, valMins.max)
      if (maxMin <= minMax) {
        RangeValue(maxMin, minMax)
      } else {  // null set
        RangeValue.empty
      }

    case _ => throw new ExprEvaluateException(s"Unknown reduce op in ${reduce.op} $vals from $reduce")
  }

  def evalStruct(struct: expr.StructExpr, vals: Map[String, ExprValue]): ExprValue = ???

  def evalRange(range: expr.RangeExpr, minimum: ExprValue, maximum: ExprValue): ExprValue = (minimum, maximum) match {
    case (FloatPromotable(lhs), FloatPromotable(rhs)) => if (lhs <= rhs) {
      RangeValue(lhs, rhs)
    } else {
      throw new ExprEvaluateException(s"Range with min $minimum not <= max $maximum from $range")
    }
    case _ => throw new ExprEvaluateException(s"Unknown range operands types $minimum $maximum from $range")
  }

  def evalIfThenElse(ite: expr.IfThenElseExpr, cond: ExprValue,
                     tru: ExprValue, fal: ExprValue): ExprValue = cond match {
    case BooleanValue(true) => tru
    case BooleanValue(false) => fal
    case _ => throw new ExprEvaluateException(s"Unknown condition types if $cond then $tru else $fal from $ite")
  }

  def evalExtract(extract: expr.ExtractExpr,
                  container: ExprValue, index: ExprValue): ExprValue = (container, index) match {
    case (ArrayValue(container), IntValue(index)) => container(index.toInt)
    case _ => throw new ExprEvaluateException(s"Unknown operand types for extract element $index from $container from $extract")
  }
}


class ExprEvaluate(refs: ConstProp, root: DesignPath) extends ValueExprMap[ExprValue] {
  override def mapLiteral(literal: lit.ValueLit): ExprValue =
    ExprEvaluate.evalLiteral(literal)

  override def mapBinary(binary: expr.BinaryExpr, lhs: ExprValue, rhs: ExprValue): ExprValue =
    ExprEvaluate.evalBinary(binary, lhs, rhs)

  override def mapReduce(reduce: expr.ReductionExpr, vals: ExprValue): ExprValue =
    ExprEvaluate.evalReduce(reduce, vals)

  override def mapStruct(struct: expr.StructExpr, vals: Map[String, ExprValue]): ExprValue =
    ExprEvaluate.evalStruct(struct, vals)

  override def mapRange(range: expr.RangeExpr, minimum: ExprValue, maximum: ExprValue): ExprValue =
    ExprEvaluate.evalRange(range, minimum, maximum)

  override def mapIfThenElse(ite: expr.IfThenElseExpr, cond: ExprValue,
                             tru: ExprValue, fal: ExprValue): ExprValue =
    ExprEvaluate.evalIfThenElse(ite, cond, tru, fal)

  override def mapExtract(extract: expr.ExtractExpr,
                          container: ExprValue, index: ExprValue): ExprValue =
    ExprEvaluate.evalExtract(extract, container, index)

  override def mapMapExtract(mapExtract: expr.MapExtractExpr): ExprValue = {
    val container = mapExtract.getContainer.expr.ref.getOrElse(  // TODO restrict allowed types in proto
      throw new ExprEvaluateException(s"Non-ref container type in mapExtract $mapExtract")
    )
    val containerPath = root ++ container
    val elts = refs.getArrayElts(containerPath).getOrElse(
      throw new ExprEvaluateException(s"Array elts not known for $container from $mapExtract")
    )
    val values = elts.toSeq.map { elt =>  // TODO should delegate to mapRef? - but needs path concat
      val refPath = containerPath + elt ++ mapExtract.path.get
      refs.getValue(refPath).getOrElse(
        throw new ExprEvaluateException(s"No value for $refPath from $mapExtract")
      )
    }
    ArrayValue(values)
  }

  // connected and exported not overridden and to fail noisily
  // assign also not overridden and to fail noisily

  override def mapRef(path: ref.LocalPath): ExprValue = {
    refs.getValue(root.asIndirect ++ path).getOrElse(
      throw new MissingValueException(root.asIndirect ++ path)
    )
  }

}
