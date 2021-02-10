package edg.compiler

import edg.ExprBuilder._
import edg.expr.expr.BinaryExpr.Op
import edg.wir.DesignPath
import org.scalatest._
import org.scalatest.flatspec.AnyFlatSpec
import org.scalatest.matchers.should.Matchers._


/** This test set is mostly a delta from ExprEvaluateTest, focusing on missing references (array and param)
  * as well as the more complicated if-then-else logic.
  * Otherwise, both classes share much underlying code which does not need to be re-tested.
  */
class ExprEvaluatePartialTest extends AnyFlatSpec {
  behavior of "ExprEvaluatePartial"

  val emptyConstProp = new ConstProp()


  it should "handle basic expressions without references" in {
    val evalTest = new ExprEvaluatePartial(emptyConstProp, DesignPath())

    evalTest.map(
      ValueExpr.Literal(Literal.Integer(42))
    ) should equal(ExprResult.Result(IntValue(42)))
    evalTest.map(
      ValueExpr.BinOp(Op.ADD, ValueExpr.Literal(2.0), ValueExpr.Literal(3.0))
    ) should equal(ExprResult.Result(FloatValue(5.0)))
    evalTest.map(ValueExpr.BinOp(Op.INTERSECTION,
      ValueExpr.Literal(5.0, 7.0), ValueExpr.Literal(4.0, 6.0)
    )) should equal(ExprResult.Result(RangeValue(5.0, 6.0)))
    evalTest.map(
      ValueExpr.IfThenElse(ValueExpr.Literal(true), ValueExpr.Literal(4), ValueExpr.Literal(3))
    ) should equal(ExprResult.Result(IntValue(4)))
    evalTest.map(
      ValueExpr.IfThenElse(ValueExpr.Literal(false), ValueExpr.Literal(4), ValueExpr.Literal(3))
    ) should equal(ExprResult.Result(IntValue(3)))
  }

  it should "report missing references" in {

  }

  it should "resolve references" in {

  }

  it should "report partially missing references" in {

  }

  it should "return missing condition refs, then branch refs" in {

  }

  it should "resolve if-then-else with only the branch taken available" in {

  }

  it should "return a missing array before its components" in {

  }

  it should "return missing references for arrays" in {

  }

  it should "resolve arrays and reduction ops" in {

  }
}
