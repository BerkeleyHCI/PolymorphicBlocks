package edg.compiler

import edg.expr.expr
import edg.lit.lit
import edg.ref.ref
import edg.wir.{DesignPath, IndirectDesignPath}

import scala.collection.Set


/**
  * Convenience wrapper around ExprToString without needing to construct a new object each time.
  */
object ExprToString {
  private val instance = new ExprToString()

  def apply(item: expr.ValueExpr): String = instance.map(item)
}


/**
  * Converts an Expr to a human-readable string
  */
class ExprToString() extends ValueExprMap[String] {
  override def mapLiteral(literal: lit.ValueLit): String = literal.`type` match {
    case lit.ValueLit.Type.Floating(literal) => literal.`val`.toString
    case lit.ValueLit.Type.Integer(literal) => literal.`val`.toString
    case lit.ValueLit.Type.Boolean(literal) => literal.`val`.toString
    case lit.ValueLit.Type.Text(literal) => literal.`val`
    case lit.ValueLit.Type.Range(literal) => s"(${mapLiteral(literal.getMinimum)}, ${mapLiteral(literal.getMaximum)})"
    case literal => throw new ExprEvaluateException(s"(unknown literal $literal)")
  }

  private object BinaryExprOp {
    import expr.BinaryExpr.Op
    object InfixOp {
      def unapply(op: Op): Option[String] = op match {
        case Op.ADD => Some("+")
        case Op.SUB => Some("-")
        case Op.MULT => Some("×")
        case Op.DIV => Some("÷")
        case Op.AND => Some("&&")
        case Op.OR => Some("||")
        case Op.XOR => Some("^")
        case Op.IMPLIES => Some("⇒")
        case Op.EQ => Some("==")
        case Op.NEQ => Some("≠")
        case Op.GT => Some(">")
        case Op.GTE => Some("≥")
        case Op.LT => Some("<")
        case Op.LTE => Some("≤")
        case Op.MAX | Op.MIN => None
        case Op.INTERSECTION => Some("∩")
        case Op.SUBSET => Some("⊆")
        case Op.RANGE => None
        case Op.UNDEFINED | Op.Unrecognized(_) => None
      }
    }
    object PrefixOp {
      def unapply(op: Op): Option[String] = op match {
        case Op.ADD | Op.SUB | Op.MULT | Op.DIV => None
        case Op.AND | Op.OR | Op.XOR | Op.IMPLIES | Op.EQ | Op.NEQ => None
        case Op.GT | Op.GTE | Op.LT | Op.LTE => None
        case Op.MAX => Some("max")
        case Op.MIN => Some("min")
        case Op.INTERSECTION | Op.SUBSET => None
        case Op.RANGE => Some("range")
        case Op.UNDEFINED | Op.Unrecognized(_) => None
      }
    }
  }

  override def mapBinary(binary: expr.BinaryExpr,
                         lhs: String, rhs: String): String = binary.op match {
    case BinaryExprOp.InfixOp(op) => s"$lhs $op $rhs"
    case BinaryExprOp.PrefixOp(op) => s"$op($lhs, $rhs)"
    case op => s"unknown[$op]($lhs, $rhs)"
  }

  private object ReductionExprOp {
    import expr.ReductionExpr.Op
    def unapply(op: Op): Option[String] = op match {
      case Op.SUM => Some("sum")
      case Op.ALL_TRUE => Some("allTrue")
      case Op.ALL_EQ => Some("allEqual")
      case Op.ALL_UNIQUE => Some("allUnique")
      case Op.MAXIMUM => Some("max")
      case Op.MINIMUM => Some("min")
      case Op.SET_EXTRACT => Some("setExtract")
      case Op.INTERSECTION => Some("intersection")
      case Op.UNDEFINED => None
    }
  }

  override def mapReduce(reduce: expr.ReductionExpr, vals: String): String = reduce.op match {
    case ReductionExprOp(op) => s"$op(${vals.mkString(", ")})"
    case op => s"unknown[$op](${vals.mkString(", ")})"
  }

  override def mapStruct(struct: expr.StructExpr, vals: Map[String, String]): String = {
    val valsStr = vals.map { case (k, v) => s"$k: $v" }
    s"struct(${valsStr.mkString(", ")})"
  }

  override def mapRange(range: expr.RangeExpr,
                        minimum: String, maximum: String): String = {
    s"range($minimum, $maximum)"
  }

  override def mapIfThenElse(ite: expr.IfThenElseExpr, cond: String,
                             tru: String, fal: String): String = {
    s"$cond? $tru : $fal"
  }

  override def mapExtract(extract: expr.ExtractExpr,
                          container: String, index: String): String = {
    s"$container[$index]"
  }

  override def mapMapExtract(mapExtract: expr.MapExtractExpr): String = {
    s"${map(mapExtract.getContainer)}[∀ ${mapRef(mapExtract.getPath)}]"
  }

  override def mapConnected(connected: expr.ConnectedExpr, blockPort: String, linkPort: String): String = {
    s"connected($blockPort, $linkPort)"
  }

  override def mapExported(exported: expr.ExportedExpr, exteriorPort: String, internalBlockPort: String): String = {
    s"exported($exteriorPort, $internalBlockPort)"
  }

  override def mapAssign(assign: expr.AssignExpr, src: String): String =
    s"${mapRef(assign.getDst)} ⇐ $src"

  override def mapRef(path: ref.LocalPath): String = {
    path.steps.map { _.step match {
      case ref.LocalStep.Step.Name(name) => name
      case ref.LocalStep.Step.ReservedParam(ref.Reserved.UNDEFINED) => "undefined"
      case ref.LocalStep.Step.ReservedParam(ref.Reserved.CONNECTED_LINK) => "connectedLink"
      case ref.LocalStep.Step.ReservedParam(ref.Reserved.IS_CONNECTED) => "isConnected"
      case ref.LocalStep.Step.ReservedParam(ref.Reserved.LENGTH) => "length"
      case ref.LocalStep.Step.ReservedParam(ref.Reserved.ALLOCATE) => "allocate"
      case ref.LocalStep.Step.ReservedParam(ref.Reserved.Unrecognized(op)) => s"unrecognized[$op]"
    } }.mkString(".")
  }
}
