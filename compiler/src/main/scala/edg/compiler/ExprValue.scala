package edg.compiler

import edgir.lit.lit

import scala.collection.mutable
import edg.ExprBuilder.Literal
import edg.compiler.CompilerError.EmptyRange


// Base trait for expression values in edgir, should be consistent with init.proto and lit.proto
sealed trait ExprValue {
  def toLit: lit.ValueLit
  def toStringValue: String
}

object ExprValue {
  def fromValueLit(literal: lit.ValueLit): ExprValue = literal.`type` match {
    case lit.ValueLit.Type.Floating(literal) => FloatValue(literal.`val`.toFloat)
    case lit.ValueLit.Type.Integer(literal) => IntValue(literal.`val`)
    case lit.ValueLit.Type.Boolean(literal) => BooleanValue(literal.`val`)
    case lit.ValueLit.Type.Text(literal) => TextValue(literal.`val`)
    case lit.ValueLit.Type.Range(literal) => (literal.getMinimum.`type`, literal.getMaximum.`type`) match {
      case (lit.ValueLit.Type.Floating(literalMin), lit.ValueLit.Type.Floating(literalMax)) =>
        RangeValue(literalMin.`val`.toFloat, literalMax.`val`.toFloat)
      case _ => throw new IllegalArgumentException(s"Malformed range literal $literal")
    }
    case lit.ValueLit.Type.Array(arrayLiteral) =>
      ArrayValue(arrayLiteral.elts.map { lit => fromValueLit(lit) })
    case _ => throw new IllegalArgumentException(s"Unknown literal $literal")
  }
}

// These should be consistent with what is in init.proto
object FloatPromotable {
  def unapply(floatPromotable: FloatPromotable): Option[Float] = {
    Some(floatPromotable.toFloat)
  }
}

sealed trait FloatPromotable extends ExprValue {
  def toFloat: Float
}

object FloatValue {
  def apply(value: Double): FloatValue = FloatValue(value.toFloat)  // convenience method
}
case class FloatValue(value: Float) extends FloatPromotable {
  override def toFloat: Float = value
  override def toLit: lit.ValueLit = Literal.Floating(value)
  override def toStringValue: String = value.toString
}

case class IntValue(value: BigInt) extends FloatPromotable {
  override def toFloat: Float = value.toFloat  // note: potential loss of precision
  override def toLit: lit.ValueLit = Literal.Integer(value)
  override def toStringValue: String = value.toString
}

sealed trait RangeType extends ExprValue

object RangeValue {
  def apply(lower: Double, upper: Double): RangeType =
    RangeValue(lower.toFloat, upper.toFloat)  // convenience method
}

case class RangeValue(lower: Float, upper: Float) extends RangeType {
  require(lower <= upper, s"malformed range ($lower, $upper)")

  override def toLit: lit.ValueLit = Literal.Range(lower, upper)
  override def toStringValue: String = s"($lower, $upper)"
}

case object RangeEmpty extends RangeType {  // an empty range, analogous to an empty set
  override def toLit: lit.ValueLit = Literal.Range(Float.NaN, Float.NaN)
  override def toStringValue: String = s"(${Float.NaN}, ${Float.NaN})"
}

case class BooleanValue(value: Boolean) extends ExprValue {
  override def toLit: lit.ValueLit = Literal.Boolean(value)
  override def toStringValue: String = value.toString
}

case class TextValue(value: String) extends ExprValue {
  override def toLit: lit.ValueLit = Literal.Text(value)
  override def toStringValue: String = value
}

object ArrayValue {
  /** Maps a Seq using a PartialFunction. Returns the output map if all elements were mapped, otherwise returns None.
    * May short circuit evaluate on the first PartialFunction failure.
    */
  protected def seqMapOption[InType, OutType](seq: Seq[InType])(mapPartialFunc: PartialFunction[InType, OutType]):
  Option[Seq[OutType]] = {
    // TODO is this actually more performant than doing a collect, even assuming that most of the time this will fail?
    val builder = mutable.Buffer[OutType]()
    val mapLifted = mapPartialFunc.lift
    for (elt <- seq) {
      mapLifted(elt) match {
        case Some(eltMapped) => builder += eltMapped
        case None => return None
      }
    }
    Some(builder.toList)
  }

  object Empty {
    def unapply[T <: ExprValue](vals: ArrayValue[T]): Option[Unit] = {
      if (vals.values.isEmpty) {
        Some(())
      } else {
        None
      }
    }
  }

  object ExtractFloat {
    def unapply[T <: ExprValue](vals: ArrayValue[T]): Option[Seq[Float]] = seqMapOption(vals.values) {
      case FloatValue(elt) => elt
    }
  }

  object ExtractInt {
    def unapply[T <: ExprValue](vals: ArrayValue[T]): Option[Seq[BigInt]] = seqMapOption(vals.values) {
      case IntValue(elt) => elt
    }
  }

  object ExtractRange {
    def unapply[T <: ExprValue](vals: ArrayValue[T]): Option[Seq[RangeType]] = seqMapOption(vals.values) {
      case elt: RangeType => elt
    }
  }

  // Extracts the min and maxes from an array of ranges
  object UnpackRange {
    sealed trait UnpackedRange
    // Array of ranges with no empty values
    case class FullRange(mins: Seq[Float], maxs: Seq[Float]) extends UnpackedRange
    // Array of ranges with empty values and full values
    case class RangeWithEmpty(mins: Seq[Float], maxs: Seq[Float]) extends UnpackedRange
    // Array of ranges with only empty values
    case class EmptyRange() extends UnpackedRange
    // Empty input array (contains neither ranges nor empty ranges
    case class EmptyArray() extends UnpackedRange

    def unapply[T <: ExprValue](vals: ArrayValue[T]): Option[UnpackedRange] = seqMapOption(vals.values) {
      // the outer option returns None if it encounters a non-Range value
      case RangeValue(eltMin, eltMax) => Some((eltMin, eltMax))
      case RangeEmpty => None
    }.map { valueOpts =>
      val containsNone = valueOpts.contains(None)
      val containedRanges = valueOpts.flatten.unzip
      (containsNone, containedRanges) match {
        case (true, (Seq(), Seq())) => EmptyRange()
        case (false, (Seq(), Seq())) => EmptyArray()
        case (true, (mins, maxs)) => RangeWithEmpty(mins, maxs)
        case (false, (mins, maxs)) => FullRange(mins, maxs)
      }
    }
  }

  object ExtractBoolean {
    def unapply[T <: ExprValue](vals: ArrayValue[T]): Option[Seq[Boolean]] = seqMapOption(vals.values) {
      case BooleanValue(elt) => elt
    }
  }

  object ExtractText {
    def unapply[T <: ExprValue](vals: ArrayValue[T]): Option[Seq[String]] = seqMapOption(vals.values) {
      case TextValue(elt) => elt
    }
    def apply(vals: ExprValue): Seq[String] = vals match {
      case ArrayValue.ExtractText(values) => values
      case _ => throw new ClassCastException("expr was not array of text")
    }
  }

  object ExtractArray {
    def unapply[T <: ExprValue](vals: ArrayValue[T]): Option[Seq[Seq[ExprValue]]] = seqMapOption(vals.values) {
      case ArrayValue(elts) => elts
    }
  }
}

case class ArrayValue[T <: ExprValue](values: Seq[T]) extends ExprValue {
  override def toLit: lit.ValueLit = Literal.Array(values.map(_.toLit))
  override def toStringValue: String = {
    val valuesString = values.map{_.toStringValue}.mkString(", ")
    s"[$valuesString]"
  }
}
