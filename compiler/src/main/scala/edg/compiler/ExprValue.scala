package edg.compiler

import edg.lit.lit
import scala.collection.mutable
import edg.ExprBuilder.Literal


// Base trait for expression values in edgir, should be consistent with init.proto and lit.proto
sealed trait ExprValue {
  def toLit: lit.ValueLit
  def toStringValue: String
}

object ExprValue {
  def fromLit(value: lit.ValueLit): ExprValue = value.`type` match {
    case lit.ValueLit.Type.Floating(value) => FloatValue(value.`val`)
    case lit.ValueLit.Type.Integer(value) => IntValue(value.`val`)
    case lit.ValueLit.Type.Boolean(value) => BooleanValue(value.`val`)
    case lit.ValueLit.Type.Range(value) =>
      RangeValue(value.getMinimum.getFloating.`val`, value.getMaximum.getFloating.`val`)
    case lit.ValueLit.Type.Text(value) => TextValue(value.`val`)
    case value => throw new IllegalArgumentException(s"unknown ValueLit $value")
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

object RangeValue {
  def apply(lower: Double, upper: Double): RangeValue = RangeValue(lower.toFloat, upper.toFloat)  // convenience method
  def empty: RangeValue = RangeValue(Float.NaN, Float.NaN)  // TODO proper null interval construct
}

case class RangeValue(lower: Float, upper: Float) extends ExprValue {
  require((lower <= upper) || isEmpty, s"malformed range ($lower, $upper)")

  def isEmpty: Boolean = lower.isNaN || upper.isNaN  // TODO better definition of empty range

  override def toLit: lit.ValueLit = Literal.Range(lower, upper)
  override def toStringValue: String = s"($lower, $upper)"
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

  def unapply[T <: ExprValue](vals: ArrayValue[T]): Option[Seq[T]] = {
    Some(vals.values)
  }

  object Empty {
    def unapply[T <: ExprValue](vals: ArrayValue[T]): Option[Unit] = {
      if (vals.values.isEmpty) {
        Some()
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
    def unapply[T <: ExprValue](vals: ArrayValue[T]): Option[(Seq[Float], Seq[Float])] = seqMapOption(vals.values) {
      case RangeValue(eltMin, eltMax) => (eltMin, eltMax)
    }.map(_.unzip)
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
  }
}

case class ArrayValue[T <: ExprValue](values: Seq[T]) extends ExprValue {
  override def toLit: lit.ValueLit = throw new NotImplementedError("Can't toLit on Array")
  override def toStringValue: String = {
    val valuesString = values.map{_.toStringValue}.mkString(", ")
    s"[$valuesString]"
  }
}
