package edg.compiler

import edg.ExprBuilder._
import edg.wir.DesignPath
import org.scalatest._
import org.scalatest.flatspec.AnyFlatSpec
import org.scalatest.matchers.should.Matchers._


class ExprToStringTest extends AnyFlatSpec {
  behavior of "ExprToString"

  it should "handle literals" in {
    ExprToString(ValueExpr.Literal(Literal.Floating(2.0))) should equal("2.0")
    ExprToString(ValueExpr.Literal(Literal.Integer(42))) should equal("42")
    ExprToString(ValueExpr.Literal(Literal.Boolean(true))) should equal("true")
    ExprToString(ValueExpr.Literal(Literal.Text("test"))) should equal("test")
    ExprToString(ValueExpr.Literal(Literal.Range(-2, 4))) should equal("(-2.0, 4.0)")
  }

  it should "handle binary arithmetic ops" in {
    import edg.expr.expr.BinaryExpr.Op
    ExprToString(
      ValueExpr.BinOp(Op.ADD, ValueExpr.Literal(2.0), ValueExpr.Literal(3.0))
    ) should equal("2.0 + 3.0")
    ExprToString(
      ValueExpr.BinOp(Op.MAX, ValueExpr.Literal(2.0), ValueExpr.Literal(3.0))
    ) should equal("max(2.0, 3.0)")
  }

  it should "handle chained ops" in {
    import edg.expr.expr.BinaryExpr.Op
    ExprToString(ValueExpr.BinOp(Op.ADD,
      ValueExpr.BinOp(Op.SUB, ValueExpr.Literal(2.0), ValueExpr.Literal(-1)),
      ValueExpr.Literal(3.0)
    )) should equal("2.0 - -1 + 3.0")

    ExprToString(ValueExpr.BinOp(Op.AND,
      ValueExpr.BinOp(Op.OR, ValueExpr.Literal(true), ValueExpr.Literal(false)),
      ValueExpr.Literal(true)
    )) should equal("true || false && true")
  }

  it should "handle if then else" in {
    ExprToString(
      ValueExpr.IfThenElse(ValueExpr.Literal(true), ValueExpr.Literal(4), ValueExpr.Literal(3))
    ) should equal("true? 4 : 3")

    import edg.expr.expr.BinaryExpr.Op
    ExprToString(
      ValueExpr.IfThenElse(ValueExpr.BinOp(Op.AND, ValueExpr.Literal(true), ValueExpr.Literal(true)),
      ValueExpr.Literal(4), ValueExpr.Literal(3))
    ) should equal("true && true? 4 : 3")
  }
}
