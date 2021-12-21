package edg.compiler

import edgir.expr.expr
import edgir.lit.lit
import edgir.ref.ref
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
    case lit.ValueLit.Type.Range(literal) => (literal.getMinimum.`type`, literal.getMaximum.`type`) match {
      case (lit.ValueLit.Type.Floating(literalMin), lit.ValueLit.Type.Floating(literalMax)) =>
        RangeValue(literalMin.`val`.toFloat, literalMax.`val`.toFloat)
      case _ => throw new ExprEvaluateException(s"Malformed range literal $literal")
    }
    case _ => throw new ExprEvaluateException(s"Unknown literal $literal")
  }

  def evalBinary(binary: expr.BinaryExpr, lhs: ExprValue, rhs: ExprValue): ExprValue = {
    import expr.BinaryExpr.Op
    binary.op match {
      // Note promotion rules: range takes precedence, then float, then int
      case Op.ADD => (lhs, rhs) match {
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
      case Op.SUB => (lhs, rhs) match {
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
      case Op.MULT => (lhs, rhs) match {
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
      case Op.DIV => (lhs, rhs) match {
        // Floating divide-by-zero takes Scala semantics: goes to positive or negative infinity.
        // Int divide by zero is not supported.
        case (RangeValue(lhsMin, lhsMax), RangeValue(rhsMin, rhsMax)) =>
          // TODO should RHS crossing zero blow up to infinity instead?
          require((rhsMin <= 0 && rhsMax <= 0) || (rhsMin >= 0 && rhsMax >= 0),
            s"division by range crossing 0: ${lhs} ${binary.op} ${rhs} from $binary")
          val all = Seq(lhsMin / rhsMin, lhsMin / rhsMax, lhsMax / rhsMin, lhsMax / rhsMax)
          RangeValue(all.min, all.max)
        case (RangeValue(lhsMin, lhsMax), FloatPromotable(rhs)) =>
          RangeValue(lhsMin / rhs, lhsMax / rhs)
        case (FloatPromotable(lhs), RangeValue(rhsMin, rhsMax)) =>
          // TODO should RHS crossing zero blow up to infinity instead?
          require((rhsMin <= 0 && rhsMax <= 0) || (rhsMin >= 0 && rhsMax >= 0),
            s"division by range including 0: ${lhs} ${binary.op} ${rhs} from $binary")
          RangeValue(lhs / rhsMin, lhs / rhsMax)
        case (FloatValue(lhs), FloatPromotable(rhs)) =>
          FloatValue(lhs / rhs)
        case (FloatPromotable(lhs), FloatValue(rhs)) =>
          FloatValue(lhs / rhs)
        case (IntValue(lhs), IntValue(rhs)) =>
          // div 0 caught by integer semantics
          IntValue(lhs / rhs)
        case (RangeValue(lhsMin, lhsMax), ArrayValue.ExtractRange(extracted)) => extracted match {
          case ArrayValue.ExtractRange.FullRange(valMins, valMaxs) =>
            val resultElements = (valMins zip valMaxs) map { case (rhsMin, rhsMax) =>
              val all = Seq(lhsMin / rhsMin, lhsMin / rhsMax, lhsMax / rhsMin, lhsMax / rhsMax)
              RangeValue(all.min, all.max)  // TODO dedup w/ range / range case?
            }
            ArrayValue(resultElements)
          case ArrayValue.ExtractRange.EmptyArray() => ArrayValue(Seq())
          case _ => throw new ExprEvaluateException(s"Unknown binary operand types in $lhs ${binary.op} $rhs from $binary")
        }
        case _ => throw new ExprEvaluateException(s"Unknown binary operand types in $lhs ${binary.op} $rhs from $binary")
      }

      case Op.AND => (lhs, rhs) match {
        case (BooleanValue(lhs), BooleanValue(rhs)) => BooleanValue(lhs && rhs)
        case _ => throw new ExprEvaluateException(s"Unknown binary operand types in $lhs ${binary.op} $rhs from $binary")
      }
      case Op.OR => (lhs, rhs) match {
        case (BooleanValue(lhs), BooleanValue(rhs)) => BooleanValue(lhs || rhs)
        case _ => throw new ExprEvaluateException(s"Unknown binary operand types in $lhs ${binary.op} $rhs from $binary")
      }
      case Op.XOR => (lhs, rhs) match {
        case (BooleanValue(lhs), BooleanValue(rhs)) => BooleanValue(lhs ^ rhs)
        case _ => throw new ExprEvaluateException(s"Unknown binary operand types in $lhs ${binary.op} $rhs from $binary")
      }
      case Op.IMPLIES => (lhs, rhs) match {
        case (BooleanValue(lhs), BooleanValue(rhs)) => BooleanValue(!lhs || rhs)
        case _ => throw new ExprEvaluateException(s"Unknown binary operand types in $lhs ${binary.op} $rhs from $binary")
      }

      case Op.EQ => (lhs, rhs) match {
        // TODO can optionally support Range <-> Float ops later if desired, it's a 'type error' now
        case (RangeValue(lhsMin, lhsMax), RangeValue(rhsMin, rhsMax)) =>
          BooleanValue(lhsMin == rhsMin && lhsMax == rhsMax)
        case (RangeEmpty, RangeEmpty) => BooleanValue(true)
        case (_: RangeType, _: RangeType) => BooleanValue(false)  // type mismatch by priority
        case (IntValue(lhs), IntValue(rhs)) => BooleanValue(lhs == rhs)  // prioritize int compare before promotion
        case (FloatPromotable(lhs), FloatPromotable(rhs)) => BooleanValue(lhs == rhs)
        case (BooleanValue(lhs), BooleanValue(rhs)) => BooleanValue(lhs == rhs)
        case (TextValue(lhs), TextValue(rhs)) => BooleanValue(lhs == rhs)
        case _ => throw new ExprEvaluateException(s"Unknown binary operand types in $lhs ${binary.op} $rhs from $binary")
      }
      // TODO dedup w/ above?
      case Op.NEQ => (lhs, rhs) match {
        // TODO can optionally support Range <-> Float ops later if desired, it's a 'type error' now
        case (RangeValue(lhsMin, lhsMax), RangeValue(rhsMin, rhsMax)) =>
          BooleanValue(lhsMin != rhsMin || lhsMax != rhsMax)
        case (RangeEmpty, RangeEmpty) => BooleanValue(false)
        case (_: RangeType, _: RangeType) => BooleanValue(true)  // type mismatch by priority
        case (IntValue(lhs), IntValue(rhs)) => BooleanValue(lhs != rhs)  // prioritize int compare before promotion
        case (FloatPromotable(lhs), FloatPromotable(rhs)) => BooleanValue(lhs != rhs)
        case (BooleanValue(lhs), BooleanValue(rhs)) => BooleanValue(lhs != rhs)
        case (TextValue(lhs), TextValue(rhs)) => BooleanValue(lhs != rhs)
        case _ => throw new ExprEvaluateException(s"Unknown binary operand types in $lhs ${binary.op} $rhs from $binary")
      }

      case Op.GT => (lhs, rhs) match {
        // TODO can optionally support Range <-> Float ops later if desired, it's a 'type error' now
        case (RangeValue(lhsMin, lhsMax), RangeValue(rhsMin, rhsMax)) => BooleanValue(lhsMin > rhsMax)
        case (IntValue(lhs), IntValue(rhs)) => BooleanValue(lhs > rhs) // prioritize int compare before promotion
        case (FloatPromotable(lhs), FloatPromotable(rhs)) => BooleanValue(lhs > rhs)
        case _ => throw new ExprEvaluateException(s"Unknown binary operand types in $lhs ${binary.op} $rhs from $binary")
      }
      case Op.GTE => (lhs, rhs) match {
        // TODO can optionally support Range <-> Float ops later if desired, it's a 'type error' now
        case (RangeValue(lhsMin, lhsMax), RangeValue(rhsMin, rhsMax)) => BooleanValue(lhsMin >= rhsMax)
        case (IntValue(lhs), IntValue(rhs)) => BooleanValue(lhs >= rhs) // prioritize int compare before promotion
        case (FloatPromotable(lhs), FloatPromotable(rhs)) => BooleanValue(lhs >= rhs)
        case _ => throw new ExprEvaluateException(s"Unknown binary operand types in $lhs ${binary.op} $rhs from $binary")
      }
      case Op.LT => (lhs, rhs) match {
        // TODO can optionally support Range <-> Float ops later if desired, it's a 'type error' now
        case (RangeValue(lhsMin, lhsMax), RangeValue(rhsMin, rhsMax)) => BooleanValue(lhsMax < rhsMin)
        case (IntValue(lhs), IntValue(rhs)) => BooleanValue(lhs < rhs) // prioritize int compare before promotion
        case (FloatPromotable(lhs), FloatPromotable(rhs)) => BooleanValue(lhs < rhs)
        case _ => throw new ExprEvaluateException(s"Unknown binary operand types in $lhs ${binary.op} $rhs from $binary")
      }
      case Op.LTE => (lhs, rhs) match {
        // TODO can optionally support Range <-> Float ops later if desired, it's a 'type error' now
        case (RangeValue(lhsMin, lhsMax), RangeValue(rhsMin, rhsMax)) => BooleanValue(lhsMax <= rhsMin)
        case (IntValue(lhs), IntValue(rhs)) => BooleanValue(lhs <= rhs) // prioritize int compare before promotion
        case (FloatPromotable(lhs), FloatPromotable(rhs)) => BooleanValue(lhs <= rhs)
        case _ => throw new ExprEvaluateException(s"Unknown binary operand types in $lhs ${binary.op} $rhs from $binary")
      }

      case Op.MAX => (lhs, rhs) match {
        case (IntValue(lhs), IntValue(rhs)) => IntValue(lhs.max(rhs)) // prioritize int compare before promotion
        case (FloatPromotable(lhs), FloatPromotable(rhs)) => FloatValue(math.max(lhs, rhs))
        case _ => throw new ExprEvaluateException(s"Unknown binary operand types in $lhs ${binary.op} $rhs from $binary")
      }
      case Op.MIN => (lhs, rhs) match {
        case (IntValue(lhs), IntValue(rhs)) => IntValue(lhs.min(rhs)) // prioritize int compare before promotion
        case (FloatPromotable(lhs), FloatPromotable(rhs)) => FloatValue(math.min(lhs, rhs))
        case _ => throw new ExprEvaluateException(s"Unknown binary operand types in $lhs ${binary.op} $rhs from $binary")
      }

      case Op.INTERSECTION => (lhs, rhs) match {
        case (RangeEmpty, _) => RangeEmpty  // anything intersecting with empty is empty
        case (_, RangeEmpty) => RangeEmpty
        case (RangeValue(lhsMin, lhsMax), RangeValue(rhsMin, rhsMax)) =>
          val (minMax, maxMin) = (math.min(lhsMax, rhsMax), math.max(lhsMin, rhsMin))
          if (maxMin <= minMax) {
            RangeValue(maxMin, minMax)
          } else {  // null set
            RangeEmpty
          }
        case _ => throw new ExprEvaluateException(s"Unknown binary operand types in $lhs ${binary.op} $rhs from $binary")
      }
      case Op.HULL => (lhs, rhs) match {
        case (RangeEmpty, rhs: RangeValue) => rhs
        case (lhs: RangeValue, RangeEmpty) => lhs
        case (RangeValue(lhsMin, lhsMax), RangeValue(rhsMin, rhsMax)) =>
          RangeValue(math.min(lhsMin, rhsMin), math.max(lhsMax, rhsMax))
        case (RangeEmpty, RangeEmpty) => RangeEmpty
        case _ => throw new ExprEvaluateException(s"Unknown binary operand types in $lhs ${binary.op} $rhs from $binary")
      }
      case Op.WITHIN => (lhs, rhs) match {  // lhs contained within rhs
        case (RangeEmpty, _: RangeValue) => BooleanValue(true)  // empty contained within anything
        case (_: RangeValue, RangeEmpty) => BooleanValue(false)  // empty contains nothing
        case (FloatPromotable(_), RangeEmpty) => BooleanValue(false)  // empty contains nothing, not even single points
        case (RangeValue(lhsMin, lhsMax), RangeValue(rhsMin, rhsMax)) =>
          BooleanValue(rhsMin <= lhsMin && rhsMax >= lhsMax)
        case (FloatPromotable(lhs), RangeValue(rhsMin, rhsMax)) => BooleanValue(rhsMin <= lhs && rhsMax >= lhs)
        case _ => throw new ExprEvaluateException(s"Unknown binary operands types in $lhs ${binary.op} $rhs from $binary")
      }

      case Op.RANGE => (lhs, rhs) match {
        case (FloatPromotable(lhs), FloatPromotable(rhs)) => RangeValue(math.min(lhs, rhs), math.max(lhs, rhs))
        case _ => throw new ExprEvaluateException(s"Unknown binary operands types in $lhs ${binary.op} $rhs from $binary")
      }

      case _ => throw new ExprEvaluateException(s"Unknown binary op in $lhs ${binary.op} $rhs from $binary")
    }
  }

  def evalBinarySet(binarySet: expr.BinarySetExpr, lhsset: ExprValue, rhs: ExprValue): ExprValue = {
    import expr.BinarySetExpr.Op
    binarySet.op match {
      // Note promotion rules: range takes precedence, then float, then int
      case Op.ADD => (lhs, rhs) match {
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
      case Op.SUB => (lhs, rhs) match {
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
      case Op.MULT => (lhs, rhs) match {
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
      case Op.DIV => (lhs, rhs) match {
        // Floating divide-by-zero takes Scala semantics: goes to positive or negative infinity.
        // Int divide by zero is not supported.
        case (RangeValue(lhsMin, lhsMax), RangeValue(rhsMin, rhsMax)) =>
          // TODO should RHS crossing zero blow up to infinity instead?
          require((rhsMin <= 0 && rhsMax <= 0) || (rhsMin >= 0 && rhsMax >= 0),
            s"division by range crossing 0: ${lhs} ${binary.op} ${rhs} from $binary")
          val all = Seq(lhsMin / rhsMin, lhsMin / rhsMax, lhsMax / rhsMin, lhsMax / rhsMax)
          RangeValue(all.min, all.max)
        case (RangeValue(lhsMin, lhsMax), FloatPromotable(rhs)) =>
          RangeValue(lhsMin / rhs, lhsMax / rhs)
        case (FloatPromotable(lhs), RangeValue(rhsMin, rhsMax)) =>
          // TODO should RHS crossing zero blow up to infinity instead?
          require((rhsMin <= 0 && rhsMax <= 0) || (rhsMin >= 0 && rhsMax >= 0),
            s"division by range including 0: ${lhs} ${binary.op} ${rhs} from $binary")
          RangeValue(lhs / rhsMin, lhs / rhsMax)
        case (FloatValue(lhs), FloatPromotable(rhs)) =>
          FloatValue(lhs / rhs)
        case (FloatPromotable(lhs), FloatValue(rhs)) =>
          FloatValue(lhs / rhs)
        case (IntValue(lhs), IntValue(rhs)) =>
          // div 0 caught by integer semantics
          IntValue(lhs / rhs)
        case (RangeValue(lhsMin, lhsMax), ArrayValue.ExtractRange(extracted)) => extracted match {
          case ArrayValue.ExtractRange.FullRange(valMins, valMaxs) =>
            val resultElements = (valMins zip valMaxs) map { case (rhsMin, rhsMax) =>
              val all = Seq(lhsMin / rhsMin, lhsMin / rhsMax, lhsMax / rhsMin, lhsMax / rhsMax)
              RangeValue(all.min, all.max)  // TODO dedup w/ range / range case?
            }
            ArrayValue(resultElements)
          case ArrayValue.ExtractRange.EmptyArray() => ArrayValue(Seq())
          case _ => throw new ExprEvaluateException(s"Unknown binary operand types in $lhs ${binary.op} $rhs from $binary")
        }
        case _ => throw new ExprEvaluateException(s"Unknown binary operand types in $lhs ${binary.op} $rhs from $binary")
      }

      case Op.AND => (lhs, rhs) match {
        case (BooleanValue(lhs), BooleanValue(rhs)) => BooleanValue(lhs && rhs)
        case _ => throw new ExprEvaluateException(s"Unknown binary operand types in $lhs ${binary.op} $rhs from $binary")
      }
      case Op.OR => (lhs, rhs) match {
        case (BooleanValue(lhs), BooleanValue(rhs)) => BooleanValue(lhs || rhs)
        case _ => throw new ExprEvaluateException(s"Unknown binary operand types in $lhs ${binary.op} $rhs from $binary")
      }
      case Op.XOR => (lhs, rhs) match {
        case (BooleanValue(lhs), BooleanValue(rhs)) => BooleanValue(lhs ^ rhs)
        case _ => throw new ExprEvaluateException(s"Unknown binary operand types in $lhs ${binary.op} $rhs from $binary")
      }
      case Op.IMPLIES => (lhs, rhs) match {
        case (BooleanValue(lhs), BooleanValue(rhs)) => BooleanValue(!lhs || rhs)
        case _ => throw new ExprEvaluateException(s"Unknown binary operand types in $lhs ${binary.op} $rhs from $binary")
      }

      case Op.EQ => (lhs, rhs) match {
        // TODO can optionally support Range <-> Float ops later if desired, it's a 'type error' now
        case (RangeValue(lhsMin, lhsMax), RangeValue(rhsMin, rhsMax)) =>
          BooleanValue(lhsMin == rhsMin && lhsMax == rhsMax)
        case (RangeEmpty, RangeEmpty) => BooleanValue(true)
        case (_: RangeType, _: RangeType) => BooleanValue(false)  // type mismatch by priority
        case (IntValue(lhs), IntValue(rhs)) => BooleanValue(lhs == rhs)  // prioritize int compare before promotion
        case (FloatPromotable(lhs), FloatPromotable(rhs)) => BooleanValue(lhs == rhs)
        case (BooleanValue(lhs), BooleanValue(rhs)) => BooleanValue(lhs == rhs)
        case (TextValue(lhs), TextValue(rhs)) => BooleanValue(lhs == rhs)
        case _ => throw new ExprEvaluateException(s"Unknown binary operand types in $lhs ${binary.op} $rhs from $binary")
      }
      // TODO dedup w/ above?
      case Op.NEQ => (lhs, rhs) match {
        // TODO can optionally support Range <-> Float ops later if desired, it's a 'type error' now
        case (RangeValue(lhsMin, lhsMax), RangeValue(rhsMin, rhsMax)) =>
          BooleanValue(lhsMin != rhsMin || lhsMax != rhsMax)
        case (RangeEmpty, RangeEmpty) => BooleanValue(false)
        case (_: RangeType, _: RangeType) => BooleanValue(true)  // type mismatch by priority
        case (IntValue(lhs), IntValue(rhs)) => BooleanValue(lhs != rhs)  // prioritize int compare before promotion
        case (FloatPromotable(lhs), FloatPromotable(rhs)) => BooleanValue(lhs != rhs)
        case (BooleanValue(lhs), BooleanValue(rhs)) => BooleanValue(lhs != rhs)
        case (TextValue(lhs), TextValue(rhs)) => BooleanValue(lhs != rhs)
        case _ => throw new ExprEvaluateException(s"Unknown binary operand types in $lhs ${binary.op} $rhs from $binary")
      }

      case Op.GT => (lhs, rhs) match {
        // TODO can optionally support Range <-> Float ops later if desired, it's a 'type error' now
        case (RangeValue(lhsMin, lhsMax), RangeValue(rhsMin, rhsMax)) => BooleanValue(lhsMin > rhsMax)
        case (IntValue(lhs), IntValue(rhs)) => BooleanValue(lhs > rhs) // prioritize int compare before promotion
        case (FloatPromotable(lhs), FloatPromotable(rhs)) => BooleanValue(lhs > rhs)
        case _ => throw new ExprEvaluateException(s"Unknown binary operand types in $lhs ${binary.op} $rhs from $binary")
      }
      case Op.GTE => (lhs, rhs) match {
        // TODO can optionally support Range <-> Float ops later if desired, it's a 'type error' now
        case (RangeValue(lhsMin, lhsMax), RangeValue(rhsMin, rhsMax)) => BooleanValue(lhsMin >= rhsMax)
        case (IntValue(lhs), IntValue(rhs)) => BooleanValue(lhs >= rhs) // prioritize int compare before promotion
        case (FloatPromotable(lhs), FloatPromotable(rhs)) => BooleanValue(lhs >= rhs)
        case _ => throw new ExprEvaluateException(s"Unknown binary operand types in $lhs ${binary.op} $rhs from $binary")
      }
      case Op.LT => (lhs, rhs) match {
        // TODO can optionally support Range <-> Float ops later if desired, it's a 'type error' now
        case (RangeValue(lhsMin, lhsMax), RangeValue(rhsMin, rhsMax)) => BooleanValue(lhsMax < rhsMin)
        case (IntValue(lhs), IntValue(rhs)) => BooleanValue(lhs < rhs) // prioritize int compare before promotion
        case (FloatPromotable(lhs), FloatPromotable(rhs)) => BooleanValue(lhs < rhs)
        case _ => throw new ExprEvaluateException(s"Unknown binary operand types in $lhs ${binary.op} $rhs from $binary")
      }
      case Op.LTE => (lhs, rhs) match {
        // TODO can optionally support Range <-> Float ops later if desired, it's a 'type error' now
        case (RangeValue(lhsMin, lhsMax), RangeValue(rhsMin, rhsMax)) => BooleanValue(lhsMax <= rhsMin)
        case (IntValue(lhs), IntValue(rhs)) => BooleanValue(lhs <= rhs) // prioritize int compare before promotion
        case (FloatPromotable(lhs), FloatPromotable(rhs)) => BooleanValue(lhs <= rhs)
        case _ => throw new ExprEvaluateException(s"Unknown binary operand types in $lhs ${binary.op} $rhs from $binary")
      }

      case Op.MAX => (lhs, rhs) match {
        case (IntValue(lhs), IntValue(rhs)) => IntValue(lhs.max(rhs)) // prioritize int compare before promotion
        case (FloatPromotable(lhs), FloatPromotable(rhs)) => FloatValue(math.max(lhs, rhs))
        case _ => throw new ExprEvaluateException(s"Unknown binary operand types in $lhs ${binary.op} $rhs from $binary")
      }
      case Op.MIN => (lhs, rhs) match {
        case (IntValue(lhs), IntValue(rhs)) => IntValue(lhs.min(rhs)) // prioritize int compare before promotion
        case (FloatPromotable(lhs), FloatPromotable(rhs)) => FloatValue(math.min(lhs, rhs))
        case _ => throw new ExprEvaluateException(s"Unknown binary operand types in $lhs ${binary.op} $rhs from $binary")
      }

      case Op.INTERSECTION => (lhs, rhs) match {
        case (RangeEmpty, _) => RangeEmpty  // anything intersecting with empty is empty
        case (_, RangeEmpty) => RangeEmpty
        case (RangeValue(lhsMin, lhsMax), RangeValue(rhsMin, rhsMax)) =>
          val (minMax, maxMin) = (math.min(lhsMax, rhsMax), math.max(lhsMin, rhsMin))
          if (maxMin <= minMax) {
            RangeValue(maxMin, minMax)
          } else {  // null set
            RangeEmpty
          }
        case _ => throw new ExprEvaluateException(s"Unknown binary operand types in $lhs ${binary.op} $rhs from $binary")
      }
      case Op.HULL => (lhs, rhs) match {
        case (RangeEmpty, rhs: RangeValue) => rhs
        case (lhs: RangeValue, RangeEmpty) => lhs
        case (RangeValue(lhsMin, lhsMax), RangeValue(rhsMin, rhsMax)) =>
          RangeValue(math.min(lhsMin, rhsMin), math.max(lhsMax, rhsMax))
        case (RangeEmpty, RangeEmpty) => RangeEmpty
        case _ => throw new ExprEvaluateException(s"Unknown binary operand types in $lhs ${binary.op} $rhs from $binary")
      }
      case Op.WITHIN => (lhs, rhs) match {  // lhs contained within rhs
        case (RangeEmpty, _: RangeValue) => BooleanValue(true)  // empty contained within anything
        case (_: RangeValue, RangeEmpty) => BooleanValue(false)  // empty contains nothing
        case (FloatPromotable(_), RangeEmpty) => BooleanValue(false)  // empty contains nothing, not even single points
        case (RangeValue(lhsMin, lhsMax), RangeValue(rhsMin, rhsMax)) =>
          BooleanValue(rhsMin <= lhsMin && rhsMax >= lhsMax)
        case (FloatPromotable(lhs), RangeValue(rhsMin, rhsMax)) => BooleanValue(rhsMin <= lhs && rhsMax >= lhs)
        case _ => throw new ExprEvaluateException(s"Unknown binary operands types in $lhs ${binary.op} $rhs from $binary")
      }

      case Op.RANGE => (lhs, rhs) match {
        case (FloatPromotable(lhs), FloatPromotable(rhs)) => RangeValue(math.min(lhs, rhs), math.max(lhs, rhs))
        case _ => throw new ExprEvaluateException(s"Unknown binary operands types in $lhs ${binary.op} $rhs from $binary")
      }

      case _ => throw new ExprEvaluateException(s"Unknown binary op in $lhs ${binary.op} $rhs from $binary")
    }
  }

  def evalUnary(unary: expr.UnaryExpr, `val`: ExprValue): ExprValue = {
    import expr.UnaryExpr.Op
    (unary.op, `val`) match {
      // In this case we don't do numeric promotion
      case (Op.SUM, ArrayValue.Empty(_)) => FloatValue(0)  // TODO type needs to be dynamic
      case (Op.SUM, ArrayValue.ExtractFloat(vals)) => FloatValue(vals.sum)
      case (Op.SUM, ArrayValue.ExtractInt(vals)) => IntValue(vals.sum)
      case (Op.SUM, ArrayValue.ExtractRange(extracted)) => extracted match {
        case ArrayValue.ExtractRange.FullRange(valMins, valMaxs) => RangeValue(valMins.sum, valMaxs.sum)
        case _ => RangeEmpty  // TODO how should sum behave on empty ranges?
      }

      case (Op.ANY_TRUE, ArrayValue.Empty(_)) => BooleanValue(true)
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

      // TODO this is definitely a hack in the absence of a proper range extractor
      case (Op.MAXIMUM, RangeValue(lower, upper)) => FloatValue(upper)
      case (Op.MINIMUM, RangeValue(lower, upper)) => FloatValue(lower)

      // TODO can we have stricter semantics to avoid min(RangeEmpty) and max(RangeEmpty)?
      // This just NaNs out so at least it propagates
      case (Op.MAXIMUM, RangeEmpty) => FloatValue(Float.NaN)
      case (Op.MINIMUM, RangeEmpty) => FloatValue(Float.NaN)

      // TODO this should be a user-level assertion instead of a compiler error
      case (Op.SET_EXTRACT, ArrayValue.Empty(_)) =>
        throw new ExprEvaluateException(s"SetExtract with empty values from $reduce")
      case (Op.SET_EXTRACT, ArrayValue(vals)) => if (vals.forall(_ == vals.head)) {
        vals.head
      } else {
        throw new ExprEvaluateException(s"SetExtract with non-equal values $vals from $reduce")
      }

      // Any empty value means the expression result is empty
      case (Op.INTERSECTION, ArrayValue.ExtractRange(extracted)) => extracted match {
        case ArrayValue.ExtractRange.FullRange(valMins, valMaxs) =>
          val (minMax, maxMin) = (valMaxs.min, valMins.max)
          if (maxMin <= minMax) {
            RangeValue(maxMin, minMax)
          } else {  // does not intersect, null set
            RangeEmpty
          }
        // The implicit initial value of intersect is the full range
        // TODO are these good semantics?
        case ArrayValue.ExtractRange.EmptyArray() => RangeValue(Float.NegativeInfinity, Float.PositiveInfinity)
        case _ => RangeEmpty
      }

      // Any value is used (empty effectively discarded)
      case (Op.HULL, ArrayValue.ExtractRange(extracted)) => extracted match {
        case ArrayValue.ExtractRange.FullRange(valMins, valMaxs) => RangeValue(valMins.min, valMaxs.max)
        case ArrayValue.ExtractRange.RangeWithEmpty(valMins, valMaxs) => RangeValue(valMins.min, valMaxs.max)
        case _ => RangeEmpty
      }

      case _ => throw new ExprEvaluateException(s"Unknown reduce op in ${unarySet.op} $vals from $reduce")
    }
  }

  def evalUnarySet(unarySet: expr.UnarySetExpr, vals: ExprValue): ExprValue = {
    import expr.UnarySetExpr.Op
    (unarySet.op, vals) match {
      // In this case we don't do numeric promotion
      case (Op.SUM, ArrayValue.Empty(_)) => FloatValue(0)  // TODO type needs to be dynamic
      case (Op.SUM, ArrayValue.ExtractFloat(vals)) => FloatValue(vals.sum)
      case (Op.SUM, ArrayValue.ExtractInt(vals)) => IntValue(vals.sum)
      case (Op.SUM, ArrayValue.ExtractRange(extracted)) => extracted match {
        case ArrayValue.ExtractRange.FullRange(valMins, valMaxs) => RangeValue(valMins.sum, valMaxs.sum)
        case _ => RangeEmpty  // TODO how should sum behave on empty ranges?
      }

      case (Op.ANY_TRUE, ArrayValue.Empty(_)) => BooleanValue(true)
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

      // TODO this is definitely a hack in the absence of a proper range extractor
      case (Op.MAXIMUM, RangeValue(lower, upper)) => FloatValue(upper)
      case (Op.MINIMUM, RangeValue(lower, upper)) => FloatValue(lower)

      // TODO can we have stricter semantics to avoid min(RangeEmpty) and max(RangeEmpty)?
      // This just NaNs out so at least it propagates
      case (Op.MAXIMUM, RangeEmpty) => FloatValue(Float.NaN)
      case (Op.MINIMUM, RangeEmpty) => FloatValue(Float.NaN)

      // TODO this should be a user-level assertion instead of a compiler error
      case (Op.SET_EXTRACT, ArrayValue.Empty(_)) =>
        throw new ExprEvaluateException(s"SetExtract with empty values from $reduce")
      case (Op.SET_EXTRACT, ArrayValue(vals)) => if (vals.forall(_ == vals.head)) {
        vals.head
      } else {
        throw new ExprEvaluateException(s"SetExtract with non-equal values $vals from $reduce")
      }

      // Any empty value means the expression result is empty
      case (Op.INTERSECTION, ArrayValue.ExtractRange(extracted)) => extracted match {
        case ArrayValue.ExtractRange.FullRange(valMins, valMaxs) =>
          val (minMax, maxMin) = (valMaxs.min, valMins.max)
          if (maxMin <= minMax) {
            RangeValue(maxMin, minMax)
          } else {  // does not intersect, null set
            RangeEmpty
          }
        // The implicit initial value of intersect is the full range
        // TODO are these good semantics?
        case ArrayValue.ExtractRange.EmptyArray() => RangeValue(Float.NegativeInfinity, Float.PositiveInfinity)
        case _ => RangeEmpty
      }

      // Any value is used (empty effectively discarded)
      case (Op.HULL, ArrayValue.ExtractRange(extracted)) => extracted match {
        case ArrayValue.ExtractRange.FullRange(valMins, valMaxs) => RangeValue(valMins.min, valMaxs.max)
        case ArrayValue.ExtractRange.RangeWithEmpty(valMins, valMaxs) => RangeValue(valMins.min, valMaxs.max)
        case _ => RangeEmpty
      }

      case _ => throw new ExprEvaluateException(s"Unknown reduce op in ${unarySet.op} $vals from $reduce")
    }
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

  override def mapBinarySet(binarySet: expr.BinarySetExpr, lhsset: ExprValue, rhs: ExprValue): ExprValue =
    ExprEvaluate.evalBinarySet(binarySet, lhsset, rhs)

  override def mapUnary(unary: expr.UnaryExpr, `val`: ExprValue): ExprValue =
    ExprEvaluate.evalUnary(unary, `val`)

  override def mapUnarySet(unarySet: expr.UnarySetExpr, vals: ExprValue): ExprValue =
    ExprEvaluate.evalUnarySet(unarySet, vals)

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
