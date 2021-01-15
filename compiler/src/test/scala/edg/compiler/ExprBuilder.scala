package edg.compiler

import edg.lit.lit
import edg.ref.ref
import edg.expr.expr


/** Convenience functions for building edg ir trees with less proto boilerplate
  */
object ExprBuilder {
  object ValueExpr {
    def Literal(literal: lit.ValueLit): expr.ValueExpr = expr.ValueExpr(expr=expr.ValueExpr.Expr.Literal(literal))
    def Literal(value: Float): expr.ValueExpr = Literal(ExprBuilder.Literal.Floating(value))
    def Literal(value: Double): expr.ValueExpr = Literal(value.toFloat)  // convenience
    def Literal(value: BigInt): expr.ValueExpr = Literal(ExprBuilder.Literal.Integer(value))
    def Literal(value: Boolean): expr.ValueExpr = Literal(ExprBuilder.Literal.Boolean(value))
    def Literal(value: String): expr.ValueExpr = Literal(ExprBuilder.Literal.Text(value))
    def Literal(valueMin: Float, valueMax: Float): expr.ValueExpr =
      Literal(ExprBuilder.Literal.Range(valueMin, valueMax))
    def Literal(valueMin: Double, valueMax: Double): expr.ValueExpr =  // convenience
      Literal(valueMin.toFloat, valueMax.toFloat)

    def BinOp(op: expr.BinaryExpr.Op, lhs: expr.ValueExpr, rhs: expr.ValueExpr): expr.ValueExpr = expr.ValueExpr(
      expr=expr.ValueExpr.Expr.Binary(expr.BinaryExpr(
        op=op, lhs=Some(lhs), rhs=Some(rhs)
      ))
    )
  }

  object Literal {
    def Floating(value: Float): lit.ValueLit = lit.ValueLit(`type`=lit.ValueLit.Type.Floating(lit.FloatLit(value)))
    def Integer(value: BigInt): lit.ValueLit = lit.ValueLit(`type`=lit.ValueLit.Type.Integer(lit.IntLit(value.toLong)))
    def Boolean(value: Boolean): lit.ValueLit = lit.ValueLit(`type`=lit.ValueLit.Type.Boolean(lit.BoolLit(value)))
    def Text(value: String): lit.ValueLit = lit.ValueLit(`type`=lit.ValueLit.Type.Text(lit.TextLit(value)))
    def Range(valueMin: Float, valueMax: Float): lit.ValueLit = {
      require(valueMin <= valueMax)
      lit.ValueLit(`type`=lit.ValueLit.Type.Range(lit.RangeLit(
        minimum=Some(Floating(valueMin)), maximum=Some(Floating(valueMax)))))
    }
  }
}
