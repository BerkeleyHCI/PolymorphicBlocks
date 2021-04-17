package edg.compiler

import edg.ExprBuilder._
import edg.expr.expr
import edg.wir.{DesignPath, IndirectDesignPath}
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
      ValueExpr.BinOp(expr.BinaryExpr.Op.ADD, ValueExpr.Literal(2.0), ValueExpr.Literal(3.0))
    ) should equal(ExprResult.Result(FloatValue(5.0)))
    evalTest.map(ValueExpr.BinOp(expr.BinaryExpr.Op.INTERSECTION,
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
    val evalTest = new ExprEvaluatePartial(emptyConstProp, DesignPath())

    evalTest.map(
      ValueExpr.Ref("ref")
    ) should equal(ExprResult.Missing(Set(ExprRef.Param(IndirectDesignPath() + "ref"))))

    evalTest.map(
      ValueExpr.BinOp(expr.BinaryExpr.Op.ADD, ValueExpr.Ref("ref1"), ValueExpr.Ref("ref2"))
    ) should equal(ExprResult.Missing(Set(
      ExprRef.Param(IndirectDesignPath() + "ref1"),
      ExprRef.Param(IndirectDesignPath() + "ref2"),
    )))
  }

  it should "resolve references" in {
    val constProp = new ConstProp()
    val evalTest = new ExprEvaluatePartial(constProp, DesignPath())

    constProp.setValue(IndirectDesignPath() + "ref", IntValue(0))
    constProp.setValue(IndirectDesignPath() + "ref1", IntValue(1))
    constProp.setValue(IndirectDesignPath() + "ref2", IntValue(2))

    evalTest.map(
      ValueExpr.Ref("ref")
    ) should equal(ExprResult.Result(IntValue(0)))

    evalTest.map(
      ValueExpr.BinOp(expr.BinaryExpr.Op.ADD, ValueExpr.Ref("ref1"), ValueExpr.Ref("ref2"))
    ) should equal(ExprResult.Result(IntValue(3)))
  }

  it should "report partially missing references" in {
    val constProp = new ConstProp()
    val evalTest = new ExprEvaluatePartial(constProp, DesignPath())

    constProp.setValue(IndirectDesignPath() + "ref1", IntValue(1))

    evalTest.map(
      ValueExpr.BinOp(expr.BinaryExpr.Op.ADD, ValueExpr.Ref("ref1"), ValueExpr.Ref("ref2"))
    ) should equal(ExprResult.Missing(Set(ExprRef.Param(IndirectDesignPath() + "ref2"))))
  }

  it should "return missing condition refs, then branch refs" in {
    val constProp = new ConstProp()
    val evalTest = new ExprEvaluatePartial(constProp, DesignPath())

    val iteExpr = ValueExpr.IfThenElse(ValueExpr.Ref("cond"), ValueExpr.Ref("ref1"), ValueExpr.Ref("ref2"))
    val negIteExpr = ValueExpr.IfThenElse(
      ValueExpr.BinOp(expr.BinaryExpr.Op.XOR, ValueExpr.Literal(true), ValueExpr.Ref("cond")),
      ValueExpr.Ref("ref1"), ValueExpr.Ref("ref2"))

    evalTest.map(iteExpr) should equal(ExprResult.Missing(Set(ExprRef.Param(IndirectDesignPath() + "cond"))))
    evalTest.map(negIteExpr) should equal(ExprResult.Missing(Set(ExprRef.Param(IndirectDesignPath() + "cond"))))

    constProp.setValue(IndirectDesignPath() + "cond", BooleanValue(true))
    evalTest.map(iteExpr) should equal(ExprResult.Missing(Set(ExprRef.Param(IndirectDesignPath() + "ref1"))))
    evalTest.map(negIteExpr) should equal(ExprResult.Missing(Set(ExprRef.Param(IndirectDesignPath() + "ref2"))))
  }

  it should "resolve if-then-else with only the branch taken available" in {
    val constProp = new ConstProp()
    val evalTest = new ExprEvaluatePartial(constProp, DesignPath())
    constProp.setValue(IndirectDesignPath() + "ref", IntValue(42))

    evalTest.map(
      ValueExpr.IfThenElse(ValueExpr.Literal(true), ValueExpr.Ref("ref"), ValueExpr.Ref("bad"))
    ) should equal(ExprResult.Result(IntValue(42)))
    evalTest.map(
      ValueExpr.IfThenElse(ValueExpr.Literal(false), ValueExpr.Ref("bad"), ValueExpr.Ref("ref"))
    ) should equal(ExprResult.Result(IntValue(42)))
  }

  it should "return a missing array before its components" in {
    val constProp = new ConstProp()
    val evalTest = new ExprEvaluatePartial(constProp, DesignPath())
    val mapExtractExpr = ValueExpr.MapExtract(Ref("container"), "inner")

    evalTest.map(
      mapExtractExpr
    ) should equal(ExprResult.Missing(Set(ExprRef.Array(DesignPath() + "container"))))

    constProp.setArrayElts(DesignPath() + "container", Seq("0", "1", "2"))
    evalTest.map(
      mapExtractExpr
    ) should equal(ExprResult.Missing(Set(
      ExprRef.Param(IndirectDesignPath() + "container" + "0" + "inner"),
      ExprRef.Param(IndirectDesignPath() + "container" + "1" + "inner"),
      ExprRef.Param(IndirectDesignPath() + "container" + "2" + "inner"),
    )))

    constProp.setValue(IndirectDesignPath() + "container" + "1" + "inner", IntValue(1))
    evalTest.map(
      mapExtractExpr
    ) should equal(ExprResult.Missing(Set(
      ExprRef.Param(IndirectDesignPath() + "container" + "0" + "inner"),
      ExprRef.Param(IndirectDesignPath() + "container" + "2" + "inner"),
    )))
  }

  it should "resolve arrays and reduction ops" in {
    val constProp = new ConstProp()
    val evalTest = new ExprEvaluatePartial(constProp, DesignPath())

    constProp.setArrayElts(DesignPath() + "container", Seq("0", "1", "2"))
    constProp.setValue(IndirectDesignPath() + "container" + "0" + "inner", IntValue(1))
    constProp.setValue(IndirectDesignPath() + "container" + "1" + "inner", IntValue(2))
    constProp.setValue(IndirectDesignPath() + "container" + "2" + "inner", IntValue(3))

    evalTest.map(
      ValueExpr.Reduce(expr.ReductionExpr.Op.SUM, ValueExpr.MapExtract(Ref("container"), "inner"))
    ) should equal(ExprResult.Result(IntValue(6)))
  }
}
