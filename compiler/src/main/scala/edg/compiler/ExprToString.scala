package edg.compiler

import edgir.expr.expr
import edgir.lit.lit
import edgir.ref.ref
import edg.wir.{DesignPath, IndirectDesignPath}

import scala.collection.Set

/** Convenience wrapper around ExprToString without needing to construct a new object each time.
  */
object ExprToString {
  private val instance = new ExprToString()

  def apply(item: expr.ValueExpr): String = instance.map(item)
  def apply(item: ref.LocalPath): String = instance.mapRef(item)
  def apply(item: lit.ValueLit): String = instance.mapLiteral(item)
}

/** Converts an Expr to a human-readable string
  */
class ExprToString() extends ValueExprMap[String] {
  override def mapLiteral(literal: lit.ValueLit): String = literal.`type` match {
    case lit.ValueLit.Type.Floating(literal) => literal.`val`.toString
    case lit.ValueLit.Type.Integer(literal) => literal.`val`.toString
    case lit.ValueLit.Type.Boolean(literal) => literal.`val`.toString
    case lit.ValueLit.Type.Text(literal) => literal.`val`
    case lit.ValueLit.Type.Range(literal) => s"(${mapLiteral(literal.getMinimum)}, ${mapLiteral(literal.getMaximum)})"
    case lit.ValueLit.Type.Array(array) =>
      val arrayElts = array.elts.map(mapLiteral)
      s"[${arrayElts.mkString(", ")}]"
    case lit.ValueLit.Type.Struct(_) => "unsupported struct"
    case lit.ValueLit.Type.Empty => "(empty)"
  }

  private object BinaryExprOp {
    import expr.BinaryExpr.Op
    object InfixOp {
      def unapply(op: Op): Option[String] = op match {
        case Op.ADD => Some("+")
        case Op.MULT => Some("×")
        case Op.SHRINK_MULT => Some("↓×")
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
        case Op.HULL => Some("h∪")
        case Op.WITHIN => Some("⊆")
        case Op.RANGE => None
        case Op.UNDEFINED | Op.Unrecognized(_) => None
      }
    }
    object PrefixOp {
      def unapply(op: Op): Option[String] = op match {
        case Op.ADD | Op.MULT | Op.SHRINK_MULT => None
        case Op.AND | Op.OR | Op.XOR | Op.IMPLIES | Op.EQ | Op.NEQ => None
        case Op.GT | Op.GTE | Op.LT | Op.LTE => None
        case Op.MAX => Some("max")
        case Op.MIN => Some("min")
        case Op.INTERSECTION | Op.HULL | Op.WITHIN => None
        case Op.RANGE => Some("range")
        case Op.UNDEFINED | Op.Unrecognized(_) => None
      }
    }
  }

  override def mapBinary(binary: expr.BinaryExpr, lhs: String, rhs: String): String = binary.op match {
    case BinaryExprOp.InfixOp(op) => s"($lhs $op $rhs)"
    case BinaryExprOp.PrefixOp(op) => s"$op($lhs, $rhs)"
    case op => s"unknown[$op]($lhs, $rhs)"
  }

  private object BinarySetExprOp {
    import expr.BinarySetExpr.Op
    object InfixOp {
      def unapply(op: Op): Option[String] = op match {
        case Op.ADD => Some("+")
        case Op.MULT => Some("×")
        case Op.CONCAT => None
        case Op.UNDEFINED | Op.Unrecognized(_) => None
      }
    }
    object PrefixOp {
      def unapply(op: Op): Option[String] = op match {
        case Op.CONCAT => Some("concat")
        case Op.ADD | Op.MULT => None
        case Op.UNDEFINED | Op.Unrecognized(_) => None
      }
    }
  }

  override def mapBinarySet(binarySet: expr.BinarySetExpr, lhsset: String, rhs: String): String = binarySet.op match {
    case BinarySetExprOp.InfixOp(op) => s"($lhsset $op $rhs)"
    case BinarySetExprOp.PrefixOp(op) => s"$op($lhsset, $rhs)"
    case op => s"unknown[$op]($lhsset, $rhs)"
  }

  private object UnaryExprOp {
    import expr.UnaryExpr.Op
    def unapply(op: Op): Option[String] = op match {
      case Op.NEGATE => Some("negate")
      case Op.NOT => Some("not")
      case Op.INVERT => Some("invert")
      case Op.MIN => Some("min")
      case Op.MAX => Some("max")
      case Op.CENTER => Some("center")
      case Op.WIDTH => Some("width")
      case Op.UNDEFINED | Op.Unrecognized(_) => None
    }
  }

  override def mapUnary(unary: expr.UnaryExpr, `val`: String): String = unary.op match {
    case UnaryExprOp(op) => s"$op(${`val`})"
    case op => s"unknown[$op](${`val`})"
  }

  private object UnarySetExprOp {
    import expr.UnarySetExpr.Op
    def unapply(op: Op): Option[String] = op match {
      case Op.SUM => Some("sum")
      case Op.ALL_TRUE => Some("allTrue")
      case Op.ANY_TRUE => Some("anyTrue")
      case Op.ALL_EQ => Some("allEqual")
      case Op.ALL_UNIQUE => Some("allUnique")
      case Op.MAXIMUM => Some("max")
      case Op.MINIMUM => Some("min")
      case Op.SET_EXTRACT => Some("setExtract")
      case Op.INTERSECTION => Some("intersection")
      case Op.HULL => Some("hull")
      case Op.NEGATE => Some("negate")
      case Op.INVERT => Some("invert")
      case Op.FLATTEN => Some("flatten")
      case Op.UNDEFINED | Op.Unrecognized(_) => None
    }
  }

  override def mapUnarySet(unarySet: expr.UnarySetExpr, vals: String): String = unarySet.op match {
    case UnarySetExprOp(op) => s"$op(${vals})"
    case op => s"unknown[$op](${vals})"
  }

  override def mapArray(array: expr.ArrayExpr, vals: Seq[String]): String = {
    s"array(${vals.mkString(", ")})"
  }

  override def mapStruct(struct: expr.StructExpr, vals: Map[String, String]): String = {
    val valsStr = vals.map { case (k, v) => s"$k: $v" }
    s"struct(${valsStr.mkString(", ")})"
  }

  override def mapRange(range: expr.RangeExpr, minimum: String, maximum: String): String = {
    s"range($minimum, $maximum)"
  }

  override def mapIfThenElse(ite: expr.IfThenElseExpr, cond: String, tru: String, fal: String): String = {
    s"($cond? $tru : $fal)"
  }

  override def mapExtract(extract: expr.ExtractExpr, container: String, index: String): String = {
    s"$container[$index]"
  }

  override def mapMapExtract(mapExtract: expr.MapExtractExpr): String = {
    s"${map(mapExtract.getContainer)}[∀ ${mapRef(mapExtract.getPath)}]"
  }

  override def mapConnected(
      connected: expr.ConnectedExpr,
      blockPort: String,
      linkPort: String,
      expandedBlockPort: String,
      expandedLinkPort: String
  ): String = {
    s"connected($blockPort, $linkPort)"
  }

  override def mapExported(
      exported: expr.ExportedExpr,
      exteriorPort: String,
      internalBlockPort: String,
      expandedExteriorPort: String,
      expandedInterorPort: String
  ): String = {
    s"exported($exteriorPort, $internalBlockPort)"
  }

  override def mapExportedTunnel(
      exported: expr.ExportedExpr,
      exteriorPort: String,
      internalBlockPort: String,
      expandedExteriorPort: String,
      expandedInterorPort: String
  ): String = {
    s"exportedTunnel($exteriorPort, $internalBlockPort)"
  }

  override def mapConnectedArray(
      connected: expr.ConnectedExpr,
      blockPort: String,
      linkPort: String,
      expandedBlockPort: Seq[String],
      expandedLinkPort: Seq[String]
  ): String = {
    s"connectedArray($blockPort, $linkPort)"
  }

  override def mapExportedArray(
      exported: expr.ExportedExpr,
      exteriorPort: String,
      internalBlockPort: String,
      expandedExteriorPort: Seq[String],
      expandedInterorPort: Seq[String]
  ): String = {
    s"exportedArray($exteriorPort, $internalBlockPort)"
  }

  override def mapAssign(assign: expr.AssignExpr, src: String): String =
    s"${mapRef(assign.getDst)} ⇐ $src"

  override def mapAssignTunnel(assign: expr.AssignExpr, src: String): String =
    s"${mapRef(assign.getDst)} ⇐() $src"

  override def mapRef(path: ref.LocalPath): String = {
    path.steps.map {
      _.step match {
        case ref.LocalStep.Step.Name(name) => name
        case ref.LocalStep.Step.Allocate("") => "(allocate)"
        case ref.LocalStep.Step.Allocate(suggestedName) => s"(allocate: $suggestedName)"
        case ref.LocalStep.Step.Empty => "(empty)"
        case ref.LocalStep.Step.ReservedParam(ref.Reserved.UNDEFINED) => "(undefined)"
        case ref.LocalStep.Step.ReservedParam(ref.Reserved.CONNECTED_LINK) => "(connectedLink)"
        case ref.LocalStep.Step.ReservedParam(ref.Reserved.IS_CONNECTED) => "(isConnected)"
        case ref.LocalStep.Step.ReservedParam(ref.Reserved.LENGTH) => "(length)"
        case ref.LocalStep.Step.ReservedParam(ref.Reserved.ELEMENTS) => "(elements)"
        case ref.LocalStep.Step.ReservedParam(ref.Reserved.ALLOCATED) => "(allocated)"
        case ref.LocalStep.Step.ReservedParam(ref.Reserved.NAME) => "(name)"
        case ref.LocalStep.Step.ReservedParam(ref.Reserved.Unrecognized(op)) => s"(unrecognized[$op])"
      }
    }.mkString(".")
  }
}
