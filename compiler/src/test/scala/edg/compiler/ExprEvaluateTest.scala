package edg.compiler

import org.scalatest._
import org.scalatest.flatspec.AnyFlatSpec
import matchers.should.Matchers._
import edg.wir.IndirectDesignPath
import edg.ExprBuilder._


class ExprEvaluateTest extends AnyFlatSpec {
  "ExprEvaluate" should "evaluate properly"

  val constProp = new ConstProp()
  val evalTest = new ExprEvaluate(constProp, IndirectDesignPath.root)

  // TODO: add array tests once there is an array literal

  it should "handle literals" in {
    evalTest.map(ValueExpr.Literal(Literal.Floating(2.0f))) should equal(FloatValue(2.0f))
    evalTest.map(ValueExpr.Literal(Literal.Integer(42))) should equal(IntValue(42))
    evalTest.map(ValueExpr.Literal(Literal.Boolean(true))) should equal(BooleanValue(true))
    evalTest.map(ValueExpr.Literal(Literal.Text("test"))) should equal(TextValue("test"))
    evalTest.map(ValueExpr.Literal(Literal.Range(-2, 4))) should equal(RangeValue(-2, 4))
  }

  it should "handle binary arithmetic ops" in {
    import edg.expr.expr.BinaryExpr.Op
    evalTest.map(
      ValueExpr.BinOp(Op.ADD, ValueExpr.Literal(2.0), ValueExpr.Literal(3.0))
    ) should equal(FloatValue(5.0f))
    evalTest.map(
      ValueExpr.BinOp(Op.SUB, ValueExpr.Literal(2.0), ValueExpr.Literal(3.0))
    ) should equal(FloatValue(-1.0f))
    evalTest.map(
      ValueExpr.BinOp(Op.MULT, ValueExpr.Literal(2.0), ValueExpr.Literal(3.0))
    ) should equal(FloatValue(6.0f))
    evalTest.map(
      ValueExpr.BinOp(Op.DIV, ValueExpr.Literal(2.0), ValueExpr.Literal(4.0))
    ) should equal(FloatValue(0.5f))

    evalTest.map(
      ValueExpr.BinOp(Op.MAX, ValueExpr.Literal(2.0), ValueExpr.Literal(3.0))
    ) should equal(FloatValue(3.0f))
    evalTest.map(
      ValueExpr.BinOp(Op.MAX, ValueExpr.Literal(3.0), ValueExpr.Literal(2.0))
    ) should equal(FloatValue(3.0f))
    evalTest.map(
      ValueExpr.BinOp(Op.MIN, ValueExpr.Literal(2.0), ValueExpr.Literal(3.0))
    ) should equal(FloatValue(2.0f))
    evalTest.map(
      ValueExpr.BinOp(Op.MIN, ValueExpr.Literal(3.0), ValueExpr.Literal(2.0))
    ) should equal(FloatValue(2.0f))
  }

  it should "handle binary range ops" in {
    import edg.expr.expr.BinaryExpr.Op
    evalTest.map(ValueExpr.BinOp(Op.INTERSECTION,
      ValueExpr.Literal(4.0, 6.0), ValueExpr.Literal(5.0, 7.0)
    )) should equal(RangeValue(5.0f, 6.0f))
    evalTest.map(ValueExpr.BinOp(Op.INTERSECTION,
      ValueExpr.Literal(5.0, 7.0), ValueExpr.Literal(4.0, 6.0)
    )) should equal(RangeValue(5.0f, 6.0f))
    evalTest.map(ValueExpr.BinOp(Op.INTERSECTION,
      ValueExpr.Literal(5.0, 7.0), ValueExpr.Literal(7.0, 10.0)
    )) should equal(RangeValue(7.0f, 7.0f))
    assert(RangeValue.isEmpty(evalTest.map(ValueExpr.BinOp(Op.INTERSECTION,
      ValueExpr.Literal(5.0, 7.0), ValueExpr.Literal(8.0, 10.0)
    )).asInstanceOf[RangeValue]))

    evalTest.map(ValueExpr.BinOp(Op.SUBSET,
      ValueExpr.Literal(6.0), ValueExpr.Literal(5.0, 7.0)
    )) should equal(BooleanValue(true))
    evalTest.map(ValueExpr.BinOp(Op.SUBSET,
      ValueExpr.Literal(7.0), ValueExpr.Literal(5.0, 7.0)
    )) should equal(BooleanValue(true))
    evalTest.map(ValueExpr.BinOp(Op.SUBSET,
      ValueExpr.Literal(7.5), ValueExpr.Literal(5.0, 7.0)
    )) should equal(BooleanValue(false))
    evalTest.map(ValueExpr.BinOp(Op.SUBSET,
      ValueExpr.Literal(4.5), ValueExpr.Literal(5.0, 7.0)
    )) should equal(BooleanValue(false))

    evalTest.map(ValueExpr.BinOp(Op.SUBSET,
      ValueExpr.Literal(5.0, 7.0), ValueExpr.Literal(5.0, 7.0)
    )) should equal(BooleanValue(true))
    evalTest.map(ValueExpr.BinOp(Op.SUBSET,
      ValueExpr.Literal(5.5, 6.5), ValueExpr.Literal(5.0, 7.0)
    )) should equal(BooleanValue(true))
    evalTest.map(ValueExpr.BinOp(Op.SUBSET,
      ValueExpr.Literal(4.5, 6.5), ValueExpr.Literal(5.0, 7.0)
    )) should equal(BooleanValue(false))
    evalTest.map(ValueExpr.BinOp(Op.SUBSET,
      ValueExpr.Literal(5.5, 7.5), ValueExpr.Literal(5.0, 7.0)
    )) should equal(BooleanValue(false))
  }

  it should "handle arithmetic promotions" in {
    import edg.expr.expr.BinaryExpr.Op
    evalTest.map(  // float + int -> float
      ValueExpr.BinOp(Op.ADD, ValueExpr.Literal(2.0), ValueExpr.Literal(3))
    ) should equal(FloatValue(5.0f))
    evalTest.map(  // int + float -> float
      ValueExpr.BinOp(Op.ADD, ValueExpr.Literal(2), ValueExpr.Literal(3.0))
    ) should equal(FloatValue(5.0f))

    evalTest.map(  // range + int -> range
      ValueExpr.BinOp(Op.ADD, ValueExpr.Literal(2.0, 3.0), ValueExpr.Literal(3))
    ) should equal(RangeValue(5.0f, 6.0f))
    evalTest.map(  // int + range -> range
      ValueExpr.BinOp(Op.ADD, ValueExpr.Literal(2), ValueExpr.Literal(6.0, 8.0))
    ) should equal(RangeValue(8.0f, 10.0f))

    evalTest.map(  // range + float -> range
      ValueExpr.BinOp(Op.ADD, ValueExpr.Literal(2.0, 3.0), ValueExpr.Literal(3.0))
    ) should equal(RangeValue(5.0f, 6.0f))
    evalTest.map(  // float + range -> range
      ValueExpr.BinOp(Op.ADD, ValueExpr.Literal(2.0), ValueExpr.Literal(6.0, 8.0))
    ) should equal(RangeValue(8.0f, 10.0f))
  }

  it should "handle chained ops" in {
    import edg.expr.expr.BinaryExpr.Op
    evalTest.map(ValueExpr.BinOp(Op.ADD,
      ValueExpr.BinOp(Op.SUB, ValueExpr.Literal(2.0), ValueExpr.Literal(-1)),
      ValueExpr.Literal(3.0)
    )) should equal(FloatValue(6.0f))

    evalTest.map(ValueExpr.BinOp(Op.AND,
      ValueExpr.BinOp(Op.OR, ValueExpr.Literal(true), ValueExpr.Literal(false)),
      ValueExpr.Literal(true)
    )) should equal(BooleanValue(true))
  }

  it should "handle equality" in {
    import edg.expr.expr.BinaryExpr.Op
    evalTest.map(
      ValueExpr.BinOp(Op.EQ, ValueExpr.Literal(3.0), ValueExpr.Literal(3.0))
    ) should equal(BooleanValue(true))
    evalTest.map(
      ValueExpr.BinOp(Op.EQ, ValueExpr.Literal(4.0), ValueExpr.Literal(3.0))
    ) should equal(BooleanValue(false))
    evalTest.map(
      ValueExpr.BinOp(Op.EQ, ValueExpr.Literal(3.0), ValueExpr.Literal(4.0))
    ) should equal(BooleanValue(false))

    evalTest.map(
      ValueExpr.BinOp(Op.NEQ, ValueExpr.Literal(3.0), ValueExpr.Literal(3.0))
    ) should equal(BooleanValue(false))
    evalTest.map(
      ValueExpr.BinOp(Op.NEQ, ValueExpr.Literal(4.0), ValueExpr.Literal(3.0))
    ) should equal(BooleanValue(true))
    evalTest.map(
      ValueExpr.BinOp(Op.NEQ, ValueExpr.Literal(3.0), ValueExpr.Literal(4.0))
    ) should equal(BooleanValue(true))

    evalTest.map(
      ValueExpr.BinOp(Op.EQ, ValueExpr.Literal(2.0, 3.0), ValueExpr.Literal(2.0, 3.0))
    ) should equal(BooleanValue(true))
    evalTest.map(
      ValueExpr.BinOp(Op.EQ, ValueExpr.Literal(2.0, 4.0), ValueExpr.Literal(2.0, 3.0))
    ) should equal(BooleanValue(false))
    evalTest.map(
      ValueExpr.BinOp(Op.EQ, ValueExpr.Literal(2.0, 3.0), ValueExpr.Literal(2.0, 4.0))
    ) should equal(BooleanValue(false))

    evalTest.map(
      ValueExpr.BinOp(Op.EQ, ValueExpr.Literal(true), ValueExpr.Literal(true))
    ) should equal(BooleanValue(true))
    evalTest.map(
      ValueExpr.BinOp(Op.EQ, ValueExpr.Literal(false), ValueExpr.Literal(false))
    ) should equal(BooleanValue(true))
    evalTest.map(
      ValueExpr.BinOp(Op.EQ, ValueExpr.Literal(true), ValueExpr.Literal(false))
    ) should equal(BooleanValue(false))

    // with int promotion
    evalTest.map(
      ValueExpr.BinOp(Op.EQ, ValueExpr.Literal(3.0), ValueExpr.Literal(3))
    ) should equal(BooleanValue(true))
    evalTest.map(
      ValueExpr.BinOp(Op.EQ, ValueExpr.Literal(3), ValueExpr.Literal(3.0))
    ) should equal(BooleanValue(true))
    evalTest.map(
      ValueExpr.BinOp(Op.EQ, ValueExpr.Literal(4.0), ValueExpr.Literal(3))
    ) should equal(BooleanValue(false))
  }

  it should "handle if then else" in {
    evalTest.map(
      ValueExpr.IfThenElse(ValueExpr.Literal(true), ValueExpr.Literal(4), ValueExpr.Literal(3))
    ) should equal(IntValue(4))
    evalTest.map(
      ValueExpr.IfThenElse(ValueExpr.Literal(false), ValueExpr.Literal(4), ValueExpr.Literal(3))
    ) should equal(IntValue(3))

    import edg.expr.expr.BinaryExpr.Op
    evalTest.map(
      ValueExpr.IfThenElse(ValueExpr.BinOp(Op.AND, ValueExpr.Literal(true), ValueExpr.Literal(true)),
      ValueExpr.Literal(4), ValueExpr.Literal(3))
    ) should equal(IntValue(4))
    evalTest.map(
      ValueExpr.IfThenElse(ValueExpr.BinOp(Op.AND, ValueExpr.Literal(true), ValueExpr.Literal(false)),
        ValueExpr.Literal(4), ValueExpr.Literal(3))
    ) should equal(IntValue(3))
  }
}
