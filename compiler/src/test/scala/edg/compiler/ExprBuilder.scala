package edg.compiler

import edg.lit.lit
import edg.ref.ref
import edg.expr.expr


/** Convenience functions for building edg ir trees with less proto boilerplate
  */
object ExprBuilder {
  object ValueExpr {
    def Literal(literal: lit.ValueLit): expr.ValueExpr = expr.ValueExpr(expr=expr.ValueExpr.Expr.Literal(literal))
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
