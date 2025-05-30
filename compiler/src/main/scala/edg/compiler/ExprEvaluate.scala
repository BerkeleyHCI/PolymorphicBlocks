package edg.compiler

import edgir.expr.expr
import edgir.lit.lit
import edgir.ref.ref
import edg.wir.{DesignPath, IndirectDesignPath, IndirectStep}

class ExprEvaluateException(msg: String) extends Exception(msg)
class MissingValueException(path: IndirectDesignPath) extends ExprEvaluateException(s"Missing value $path")

/** Shared utilities to DRY evaluation of expressions
  */
object ExprEvaluate {
  def evalLiteral(literal: lit.ValueLit): ExprValue = ExprValue.fromValueLit(literal)

  def evalBinary(binary: expr.BinaryExpr, lhs: ExprValue, rhs: ExprValue): ExprValue = {
    import expr.BinaryExpr.Op
    binary.op match {
      // Note promotion rules: range takes precedence, then float, then int
      case Op.ADD => (lhs, rhs) match {
          case (RangeValue(lhsMin, lhsMax), RangeValue(rhsMin, rhsMax)) =>
            val all = Seq(lhsMin + rhsMin, lhsMin + rhsMax, lhsMax + rhsMin, lhsMax + rhsMax)
            RangeValue(all.min, all.max)
          case (RangeEmpty, RangeEmpty) => RangeEmpty
          case (lhs: RangeValue, RangeEmpty) => lhs
          case (RangeEmpty, rhs: RangeValue) => rhs
          case (RangeValue(lhsMin, lhsMax), FloatPromotable(rhs)) =>
            RangeValue(lhsMin + rhs, lhsMax + rhs)
          case (FloatPromotable(lhs), RangeValue(rhsMin, rhsMax)) =>
            RangeValue(lhs + rhsMin, lhs + rhsMax)
          case (FloatValue(lhs), FloatPromotable(rhs)) => FloatValue(lhs + rhs)
          case (FloatPromotable(lhs), FloatValue(rhs)) => FloatValue(lhs + rhs)
          case (IntValue(lhs), IntValue(rhs)) => IntValue(lhs + rhs)
          case (TextValue(lhs), TextValue(rhs)) => TextValue(lhs + rhs)
          case _ =>
            throw new ExprEvaluateException(s"Unknown binary operand types in $lhs ${binary.op} $rhs from $binary")
        }
      case Op.MULT => (lhs, rhs) match {
          case (RangeValue(lhsMin, lhsMax), RangeValue(rhsMin, rhsMax)) =>
            val all = Seq(lhsMin * rhsMin, lhsMin * rhsMax, lhsMax * rhsMin, lhsMax * rhsMax)
            RangeValue(all.min, all.max)
          case (RangeEmpty, RangeEmpty) => RangeEmpty
          case (lhs: RangeValue, RangeEmpty) => RangeEmpty
          case (RangeEmpty, rhs: RangeValue) => RangeEmpty
          case (RangeValue(lhsMin, lhsMax), FloatPromotable(rhs)) if rhs >= 0 =>
            RangeValue(lhsMin * rhs, lhsMax * rhs)
          case (RangeValue(lhsMin, lhsMax), FloatPromotable(rhs)) if rhs < 0 =>
            RangeValue(lhsMax * rhs, lhsMin * rhs)
          case (FloatPromotable(lhs), RangeValue(rhsMin, rhsMax)) if lhs >= 0 =>
            RangeValue(lhs * rhsMin, lhs * rhsMax)
          case (FloatPromotable(lhs), RangeValue(rhsMin, rhsMax)) if lhs < 0 =>
            RangeValue(lhs * rhsMax, lhs * rhsMin)
          case (FloatValue(lhs), FloatPromotable(rhs)) => FloatValue(lhs * rhs)
          case (FloatPromotable(lhs), FloatValue(rhs)) => FloatValue(lhs * rhs)
          case (IntValue(lhs), IntValue(rhs)) => IntValue(lhs * rhs)
          case _ =>
            throw new ExprEvaluateException(s"Unknown binary operand types in $lhs ${binary.op} $rhs from $binary")
        }
      case Op.SHRINK_MULT => (lhs, rhs) match {
          case (RangeValue(targetMin, targetMax), RangeValue(contribMin, contribMax)) =>
            val lower = contribMax * targetMin
            val upper = contribMin * targetMax
            if (lower > upper) {
              ErrorValue(s"shrink_mult($lhs, $rhs) produces empty range, target $lhs tighter tol than contrib $rhs")
            } else {
              RangeValue(lower, upper)
            }
          case (RangeEmpty, RangeEmpty) => RangeEmpty
          case (lhs: RangeValue, RangeEmpty) => RangeEmpty
          case (RangeEmpty, rhs: RangeValue) => RangeEmpty
          case _ =>
            throw new ExprEvaluateException(s"Unknown binary operand types in $lhs ${binary.op} $rhs from $binary")
        }

      case Op.AND => (lhs, rhs) match {
          case (BooleanValue(lhs), BooleanValue(rhs)) => BooleanValue(lhs && rhs)
          case _ =>
            throw new ExprEvaluateException(s"Unknown binary operand types in $lhs ${binary.op} $rhs from $binary")
        }
      case Op.OR => (lhs, rhs) match {
          case (BooleanValue(lhs), BooleanValue(rhs)) => BooleanValue(lhs || rhs)
          case _ =>
            throw new ExprEvaluateException(s"Unknown binary operand types in $lhs ${binary.op} $rhs from $binary")
        }
      case Op.XOR => (lhs, rhs) match {
          case (BooleanValue(lhs), BooleanValue(rhs)) => BooleanValue(lhs ^ rhs)
          case _ =>
            throw new ExprEvaluateException(s"Unknown binary operand types in $lhs ${binary.op} $rhs from $binary")
        }
      case Op.IMPLIES => (lhs, rhs) match {
          case (BooleanValue(lhs), BooleanValue(rhs)) => BooleanValue(!lhs || rhs)
          case _ =>
            throw new ExprEvaluateException(s"Unknown binary operand types in $lhs ${binary.op} $rhs from $binary")
        }

      case Op.EQ => (lhs, rhs) match {
          // TODO can optionally support Range <-> Float ops later if desired, it's a 'type error' now
          case (RangeValue(lhsMin, lhsMax), RangeValue(rhsMin, rhsMax)) =>
            BooleanValue(lhsMin == rhsMin && lhsMax == rhsMax)
          case (RangeEmpty, RangeEmpty) => BooleanValue(true)
          case (_: RangeType, _: RangeType) => BooleanValue(false) // type mismatch by priority
          case (IntValue(lhs), IntValue(rhs)) => BooleanValue(lhs == rhs) // prioritize int compare before promotion
          case (FloatPromotable(lhs), FloatPromotable(rhs)) => BooleanValue(lhs == rhs)
          case (BooleanValue(lhs), BooleanValue(rhs)) => BooleanValue(lhs == rhs)
          case (TextValue(lhs), TextValue(rhs)) => BooleanValue(lhs == rhs)
          case (ArrayValue(lhs), ArrayValue(rhs)) => BooleanValue(lhs == rhs)
          case _ =>
            throw new ExprEvaluateException(s"Unknown binary operand types in $lhs ${binary.op} $rhs from $binary")
        }
      // TODO dedup w/ above?
      case Op.NEQ => (lhs, rhs) match {
          // TODO can optionally support Range <-> Float ops later if desired, it's a 'type error' now
          case (RangeValue(lhsMin, lhsMax), RangeValue(rhsMin, rhsMax)) =>
            BooleanValue(lhsMin != rhsMin || lhsMax != rhsMax)
          case (RangeEmpty, RangeEmpty) => BooleanValue(false)
          case (_: RangeType, _: RangeType) => BooleanValue(true) // type mismatch by priority
          case (IntValue(lhs), IntValue(rhs)) => BooleanValue(lhs != rhs) // prioritize int compare before promotion
          case (FloatPromotable(lhs), FloatPromotable(rhs)) => BooleanValue(lhs != rhs)
          case (BooleanValue(lhs), BooleanValue(rhs)) => BooleanValue(lhs != rhs)
          case (TextValue(lhs), TextValue(rhs)) => BooleanValue(lhs != rhs)
          case (ArrayValue(lhs), ArrayValue(rhs)) => BooleanValue(lhs != rhs)
          case _ =>
            throw new ExprEvaluateException(s"Unknown binary operand types in $lhs ${binary.op} $rhs from $binary")
        }

      case Op.GT => (lhs, rhs) match {
          // TODO can optionally support Range <-> Float ops later if desired, it's a 'type error' now
          case (RangeValue(lhsMin, lhsMax), RangeValue(rhsMin, rhsMax)) => BooleanValue(lhsMin > rhsMax)
          case (IntValue(lhs), IntValue(rhs)) => BooleanValue(lhs > rhs) // prioritize int compare before promotion
          case (FloatPromotable(lhs), FloatPromotable(rhs)) => BooleanValue(lhs > rhs)
          case _ =>
            throw new ExprEvaluateException(s"Unknown binary operand types in $lhs ${binary.op} $rhs from $binary")
        }
      case Op.GTE => (lhs, rhs) match {
          // TODO can optionally support Range <-> Float ops later if desired, it's a 'type error' now
          case (RangeValue(lhsMin, lhsMax), RangeValue(rhsMin, rhsMax)) => BooleanValue(lhsMin >= rhsMax)
          case (IntValue(lhs), IntValue(rhs)) => BooleanValue(lhs >= rhs) // prioritize int compare before promotion
          case (FloatPromotable(lhs), FloatPromotable(rhs)) => BooleanValue(lhs >= rhs)
          case _ =>
            throw new ExprEvaluateException(s"Unknown binary operand types in $lhs ${binary.op} $rhs from $binary")
        }
      case Op.LT => (lhs, rhs) match {
          // TODO can optionally support Range <-> Float ops later if desired, it's a 'type error' now
          case (RangeValue(lhsMin, lhsMax), RangeValue(rhsMin, rhsMax)) => BooleanValue(lhsMax < rhsMin)
          case (IntValue(lhs), IntValue(rhs)) => BooleanValue(lhs < rhs) // prioritize int compare before promotion
          case (FloatPromotable(lhs), FloatPromotable(rhs)) => BooleanValue(lhs < rhs)
          case _ =>
            throw new ExprEvaluateException(s"Unknown binary operand types in $lhs ${binary.op} $rhs from $binary")
        }
      case Op.LTE => (lhs, rhs) match {
          // TODO can optionally support Range <-> Float ops later if desired, it's a 'type error' now
          case (RangeValue(lhsMin, lhsMax), RangeValue(rhsMin, rhsMax)) => BooleanValue(lhsMax <= rhsMin)
          case (IntValue(lhs), IntValue(rhs)) => BooleanValue(lhs <= rhs) // prioritize int compare before promotion
          case (FloatPromotable(lhs), FloatPromotable(rhs)) => BooleanValue(lhs <= rhs)
          case _ =>
            throw new ExprEvaluateException(s"Unknown binary operand types in $lhs ${binary.op} $rhs from $binary")
        }

      case Op.MAX => (lhs, rhs) match {
          case (IntValue(lhs), IntValue(rhs)) => IntValue(lhs.max(rhs)) // prioritize int compare before promotion
          case (FloatPromotable(lhs), FloatPromotable(rhs)) => FloatValue(math.max(lhs, rhs))
          case _ =>
            throw new ExprEvaluateException(s"Unknown binary operand types in $lhs ${binary.op} $rhs from $binary")
        }
      case Op.MIN => (lhs, rhs) match {
          case (IntValue(lhs), IntValue(rhs)) => IntValue(lhs.min(rhs)) // prioritize int compare before promotion
          case (FloatPromotable(lhs), FloatPromotable(rhs)) => FloatValue(math.min(lhs, rhs))
          case _ =>
            throw new ExprEvaluateException(s"Unknown binary operand types in $lhs ${binary.op} $rhs from $binary")
        }

      case Op.INTERSECTION => (lhs, rhs) match {
          case (RangeEmpty, _) => RangeEmpty // anything intersecting with empty is empty
          case (_, RangeEmpty) => RangeEmpty
          case (RangeValue(lhsMin, lhsMax), RangeValue(rhsMin, rhsMax)) =>
            val (minMax, maxMin) = (math.min(lhsMax, rhsMax), math.max(lhsMin, rhsMin))
            if (maxMin <= minMax) {
              RangeValue(maxMin, minMax)
            } else { // null set
              RangeEmpty
            }
          case _ =>
            throw new ExprEvaluateException(s"Unknown binary operand types in $lhs ${binary.op} $rhs from $binary")
        }
      case Op.HULL => (lhs, rhs) match {
          case (RangeEmpty, rhs: RangeValue) => rhs
          case (lhs: RangeValue, RangeEmpty) => lhs
          case (RangeValue(lhsMin, lhsMax), RangeValue(rhsMin, rhsMax)) =>
            RangeValue(math.min(lhsMin, rhsMin), math.max(lhsMax, rhsMax))
          case (RangeEmpty, RangeEmpty) => RangeEmpty
          case _ =>
            throw new ExprEvaluateException(s"Unknown binary operand types in $lhs ${binary.op} $rhs from $binary")
        }
      case Op.WITHIN => (lhs, rhs) match { // lhs contained within rhs
          case (RangeEmpty, _: RangeType) => BooleanValue(true) // empty contained within anything, even itself
          case (_: RangeValue, RangeEmpty) => BooleanValue(false) // empty contains nothing
          case (FloatPromotable(_), RangeEmpty) => BooleanValue(false) // empty contains nothing, not even single points
          case (RangeValue(lhsMin, lhsMax), RangeValue(rhsMin, rhsMax)) =>
            BooleanValue(rhsMin <= lhsMin && rhsMax >= lhsMax)
          case (FloatPromotable(lhs), RangeValue(rhsMin, rhsMax)) => BooleanValue(rhsMin <= lhs && rhsMax >= lhs)
          case _ =>
            throw new ExprEvaluateException(s"Unknown binary operands types in $lhs ${binary.op} $rhs from $binary")
        }

      case Op.RANGE => (lhs, rhs) match {
          case (FloatPromotable(lhs), FloatPromotable(rhs)) =>
            if (lhs.isNaN && rhs.isNaN) { // here, NaN is treated as empty and dispreferred (instead of NaN prop)
              RangeEmpty
            } else if (lhs.isNaN) {
              RangeValue(rhs, rhs)
            } else if (rhs.isNaN) {
              RangeValue(lhs, lhs)
            } else {
              RangeValue(math.min(lhs, rhs), math.max(lhs, rhs))
            }
          case _ =>
            throw new ExprEvaluateException(s"Unknown binary operands types in $lhs ${binary.op} $rhs from $binary")
        }

      case _ => throw new ExprEvaluateException(s"Unknown binary op in $lhs ${binary.op} $rhs from $binary")
    }
  }

  def evalBinarySet(binarySet: expr.BinarySetExpr, lhs: ExprValue, rhs: ExprValue): ExprValue = {
    import expr.BinarySetExpr.Op
    binarySet.op match {
      // Note promotion rules: range takes precedence, then float, then int
      // TODO: can we deduplicate these cases to delegate them to evalBinary?
      case Op.ADD => (lhs, rhs) match {
          case (ArrayValue.ExtractRange(arrayElts), rhs: RangeType) =>
            val resultElts = arrayElts.map { arrayElt =>
              evalBinary(expr.BinaryExpr(op = expr.BinaryExpr.Op.ADD), arrayElt, rhs)
            }
            ArrayValue(resultElts)
          case _ => throw new ExprEvaluateException(
              s"Unknown binary set operand types in $lhs ${binarySet.op} $rhs from $binarySet"
            )
        }
      case Op.MULT => (lhs, rhs) match {
          case (ArrayValue.ExtractRange(arrayElts), rhs: RangeType) =>
            val resultElts = arrayElts.map { arrayElt =>
              evalBinary(expr.BinaryExpr(op = expr.BinaryExpr.Op.MULT), arrayElt, rhs)
            }
            ArrayValue(resultElts)
          case _ => throw new ExprEvaluateException(
              s"Unknown binary set operand types in $lhs ${binarySet.op} $rhs from $binarySet"
            )
        }
      case Op.CONCAT => (lhs, rhs) match {
          case (lhs: TextValue, ArrayValue.ExtractText(rhsElts)) =>
            ArrayValue(rhsElts.map { rhsElt => TextValue(lhs.value + rhsElt) })
          case (ArrayValue.ExtractText(lhsElts), rhs: TextValue) =>
            ArrayValue(lhsElts.map { lhsElt => TextValue(lhsElt + rhs.value) })
          case _ => throw new ExprEvaluateException(
              s"Unknown binary set operand types in $lhs ${binarySet.op} $rhs from $binarySet"
            )
        }

      case _ => throw new ExprEvaluateException(s"Unknown binary op in $lhs ${binarySet.op} $rhs from $binarySet")
    }
  }

  def evalUnary(unary: expr.UnaryExpr, `val`: ExprValue): ExprValue = {
    import expr.UnaryExpr.Op
    (unary.op, `val`) match {
      case (Op.NEGATE, `val`) => `val` match {
          case RangeValue(valMin, valMax) =>
            RangeValue(-valMax, -valMin)
          case RangeEmpty => RangeEmpty
          case FloatValue(opVal) => FloatValue(-opVal)
          case IntValue(opVal) => IntValue(-opVal)
          case _ => throw new ExprEvaluateException(s"Unknown unary operand type in ${unary.op} ${`val`} from $unary")
        }
      case (Op.NOT, BooleanValue(opVal)) => BooleanValue(!opVal)
      case (Op.INVERT, `val`) => `val` match {
          case RangeValue(valMin, valMax) =>
            RangeValue(1.0 / valMax, 1.0 / valMin)
          case RangeEmpty => RangeEmpty
          case FloatValue(opVal) => FloatValue(1.0 / opVal)
          case IntValue(opVal) =>
            FloatValue(1.0 / opVal.floatValue) // follow Python convention of division promoting to float
          case _ => throw new ExprEvaluateException(s"Unknown unary operand type in ${unary.op} ${`val`} from $unary")
        }

      case (Op.MIN, RangeValue(valMin, _)) => FloatValue(valMin)
      case (Op.MAX, RangeValue(_, valMax)) => FloatValue(valMax)

      case (Op.MAX, RangeEmpty) => ErrorValue("max(RangeEmpty) is undefined")
      case (Op.MIN, RangeEmpty) => ErrorValue("min(RangeEmpty) is undefined")

      case (Op.CENTER, RangeValue(valMin, valMax)) => FloatValue((valMin + valMax) / 2)
      case (Op.WIDTH, RangeValue(valMin, valMax)) => FloatValue(math.abs(valMax - valMin))

      case _ => throw new ExprEvaluateException(s"Unknown unary op in ${unary.op} ${`val`} from $unary")
    }
  }

  def evalUnarySet(unarySet: expr.UnarySetExpr, vals: ExprValue): ExprValue = {
    import expr.UnarySetExpr.Op
    (unarySet.op, vals) match {
      // In this case we don't do numeric promotion
      case (Op.SUM, ArrayValue.Empty(_)) => FloatValue(0) // TODO type needs to be dynamic
      case (Op.SUM, ArrayValue.ExtractFloat(vals)) => FloatValue(vals.sum)
      case (Op.SUM, ArrayValue.ExtractInt(vals)) => IntValue(vals.sum)
      case (Op.SUM, ArrayValue.ExtractBoolean(vals)) => IntValue(vals.count(_ == true))
      case (Op.SUM, ArrayValue.UnpackRange(extracted)) => extracted match {
          case ArrayValue.UnpackRange.FullRange(valMins, valMaxs) => RangeValue(valMins.sum, valMaxs.sum)
          case _ => ErrorValue("unpack_range(empty) is undefined")
        }

      case (Op.ALL_TRUE, ArrayValue.Empty(_)) => BooleanValue(true)
      case (Op.ALL_TRUE, ArrayValue.ExtractBoolean(vals)) => BooleanValue(vals.forall(_ == true))
      case (Op.ANY_TRUE, ArrayValue.Empty(_)) => BooleanValue(false)
      case (Op.ANY_TRUE, ArrayValue.ExtractBoolean(vals)) => BooleanValue(vals.contains(true))

      // TODO better support for empty arrays?
      case (Op.ALL_EQ, ArrayValue(vals)) => BooleanValue(vals.forall(_ == vals.head))

      case (Op.ALL_UNIQUE, ArrayValue(vals)) => BooleanValue(vals.size == vals.toSet.size)

      case (Op.MAXIMUM, ArrayValue.ExtractFloat(vals)) => FloatValue(vals.max)
      case (Op.MAXIMUM, ArrayValue.ExtractInt(vals)) => IntValue(vals.max)

      case (Op.MINIMUM, ArrayValue.ExtractFloat(vals)) => FloatValue(vals.min)
      case (Op.MINIMUM, ArrayValue.ExtractInt(vals)) => IntValue(vals.min)

      case (Op.SET_EXTRACT, ArrayValue.Empty(_)) => ErrorValue("set_extract(empty) is undefined")
      case (Op.SET_EXTRACT, ArrayValue(vals)) => if (vals.forall(_ == vals.head)) {
          vals.head
        } else {
          ErrorValue(f"set_extract($vals) with non-equal values")
        }

      // Any empty value means the expression result is empty
      case (Op.INTERSECTION, ArrayValue.UnpackRange(extracted)) => extracted match {
          case ArrayValue.UnpackRange.FullRange(valMins, valMaxs) =>
            val (minMax, maxMin) = (valMaxs.min, valMins.max)
            if (maxMin <= minMax) {
              RangeValue(maxMin, minMax)
            } else { // does not intersect, null set
              ErrorValue(f"intersection($extracted) produces empty set")
            }
          // The implicit initial value of intersect is the full range
          // TODO are these good semantics?
          case ArrayValue.UnpackRange.EmptyArray() => RangeValue(Float.NegativeInfinity, Float.PositiveInfinity)
          case _ => ErrorValue(f"intersection($vals) is undefined")
        }

      // Any value is used (empty effectively discarded)
      case (Op.HULL, ArrayValue.UnpackRange(extracted)) => extracted match {
          case ArrayValue.UnpackRange.FullRange(valMins, valMaxs) => RangeValue(valMins.min, valMaxs.max)
          case ArrayValue.UnpackRange.RangeWithEmpty(valMins, valMaxs) => RangeValue(valMins.min, valMaxs.max)
          case ArrayValue.UnpackRange.EmptyArray() => RangeEmpty // TODO: should this be an error?
          case ArrayValue.UnpackRange.EmptyRange() => RangeEmpty
        }
      case (Op.HULL, ArrayValue.ExtractFloat(vals)) => RangeValue(vals.min, vals.max)

      case (Op.NEGATE, vals) => vals match {
          case ArrayValue.ExtractRange(arrayElts) =>
            val resultElts = arrayElts.map { arrayElt =>
              evalUnary(expr.UnaryExpr(op = expr.UnaryExpr.Op.NEGATE), arrayElt)
            }
            ArrayValue(resultElts)
          case _ => throw new ExprEvaluateException(s"Unknown unary set operand in ${unarySet.op} $vals from $unarySet")
        }

      case (Op.INVERT, vals) => vals match {
          case ArrayValue.ExtractRange(arrayElts) =>
            val resultElts = arrayElts.map { arrayElt =>
              evalUnary(expr.UnaryExpr(op = expr.UnaryExpr.Op.INVERT), arrayElt)
            }
            ArrayValue(resultElts)
          case _ => throw new ExprEvaluateException(s"Unknown unary set operand in ${unarySet.op} $vals from $unarySet")
        }

      case (Op.FLATTEN, vals) => vals match {
          case ArrayValue.Empty(_) => ArrayValue(Seq())
          case ArrayValue.ExtractArray(arrayElts) =>
            val flatElts = arrayElts.flatten
            require(flatElts.forall(_.getClass == flatElts.head.getClass))
            ArrayValue(flatElts)
          case _ => throw new ExprEvaluateException(s"Unknown unary set operand in ${unarySet.op} $vals from $unarySet")
        }

      case _ => throw new ExprEvaluateException(s"Unknown unary set op in ${unarySet.op} $vals from $unarySet")
    }
  }

  def evalArray(array: expr.ArrayExpr, vals: Seq[ExprValue]): ExprValue = ArrayValue(vals)

  def evalStruct(struct: expr.StructExpr, vals: Map[String, ExprValue]): ExprValue = ???

  def evalRange(range: expr.RangeExpr, minimum: ExprValue, maximum: ExprValue): ExprValue = (minimum, maximum) match {
    case (FloatPromotable(lhs), FloatPromotable(rhs)) => if (lhs <= rhs) {
        RangeValue(lhs, rhs)
      } else {
        ErrorValue(s"range($minimum, $maximum) is malformed, $minimum > $maximum")
      }
    case _ => throw new ExprEvaluateException(s"Unknown range operands types $minimum $maximum from $range")
  }

  def evalIfThenElse(ite: expr.IfThenElseExpr, cond: ExprValue, tru: ExprValue, fal: ExprValue): ExprValue =
    cond match {
      case BooleanValue(true) => tru
      case BooleanValue(false) => fal
      case _ => throw new ExprEvaluateException(s"Unknown condition types if $cond then $tru else $fal from $ite")
    }

  def evalExtract(extract: expr.ExtractExpr, container: ExprValue, index: ExprValue): ExprValue =
    (container, index) match {
      case (ArrayValue(container), IntValue(index)) => container(index.toInt)
      case _ => throw new ExprEvaluateException(
          s"Unknown operand types for extract element $index from $container from $extract"
        )
    }
}

class ExprEvaluate(refs: ConstProp, root: DesignPath) extends ValueExprMap[ExprValue] {
  override def mapLiteral(literal: lit.ValueLit): ExprValue =
    ExprEvaluate.evalLiteral(literal)

  override def mapBinary(binary: expr.BinaryExpr, lhs: ExprValue, rhs: ExprValue): ExprValue =
    ExprEvaluate.evalBinary(binary, lhs, rhs)

  override def mapBinarySet(binarySet: expr.BinarySetExpr, lhsset: ExprValue, rhs: ExprValue): ExprValue =
    ExprEvaluate.evalBinarySet(binarySet, lhsset, rhs)

  override def mapUnary(unary: expr.UnaryExpr, `val`: ExprValue): ExprValue =
    ExprEvaluate.evalUnary(unary, `val`)

  override def mapUnarySet(unarySet: expr.UnarySetExpr, vals: ExprValue): ExprValue =
    ExprEvaluate.evalUnarySet(unarySet, vals)

  override def mapArray(array: expr.ArrayExpr, vals: Seq[ExprValue]): ExprValue =
    ExprEvaluate.evalArray(array, vals)

  override def mapStruct(struct: expr.StructExpr, vals: Map[String, ExprValue]): ExprValue =
    ExprEvaluate.evalStruct(struct, vals)

  override def mapRange(range: expr.RangeExpr, minimum: ExprValue, maximum: ExprValue): ExprValue =
    ExprEvaluate.evalRange(range, minimum, maximum)

  override def mapIfThenElse(ite: expr.IfThenElseExpr, cond: ExprValue, tru: ExprValue, fal: ExprValue): ExprValue =
    ExprEvaluate.evalIfThenElse(ite, cond, tru, fal)

  override def mapExtract(extract: expr.ExtractExpr, container: ExprValue, index: ExprValue): ExprValue =
    ExprEvaluate.evalExtract(extract, container, index)

  override def mapMapExtract(mapExtract: expr.MapExtractExpr): ExprValue = {
    val container = mapExtract.getContainer.expr.ref.getOrElse( // TODO restrict allowed types in proto
      throw new ExprEvaluateException(s"Non-ref container type in mapExtract $mapExtract"))
    val containerPath = root ++ container
    val elts = ArrayValue.ExtractText(refs.getValue(containerPath.asIndirect + IndirectStep.Elements).get)
    val values = elts.toSeq.map { elt => // TODO should delegate to mapRef? - but needs path concat
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
