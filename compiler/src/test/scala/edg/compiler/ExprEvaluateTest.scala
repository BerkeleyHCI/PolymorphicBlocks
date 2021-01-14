package edg.compiler

import org.scalatest._
import org.scalatest.flatspec.AnyFlatSpec
import matchers.should.Matchers._
import edg.wir.IndirectDesignPath
import ExprBuilder._


class ExprEvaluateTest extends AnyFlatSpec {
  "ExprEvaluate" should "evaluate properly"

  val constProp = new ConstProp()
  val evalTest = new ExprEvaluate(constProp, IndirectDesignPath.root)

  it should "handle literals" in {
    evalTest.map(ValueExpr.Literal(Literal.Floating(2.0f))) should equal(FloatValue(2.0f))
    evalTest.map(ValueExpr.Literal(Literal.Integer(42))) should equal(IntValue(42))
    evalTest.map(ValueExpr.Literal(Literal.Boolean(true))) should equal(BooleanValue(true))
    evalTest.map(ValueExpr.Literal(Literal.Text("test"))) should equal(TextValue("test"))
    evalTest.map(ValueExpr.Literal(Literal.Range(-2, 4))) should equal(RangeValue(-2, 4))
  }
}
