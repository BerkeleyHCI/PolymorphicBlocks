package edg.compiler

import org.scalatest._
import org.scalatest.flatspec.AnyFlatSpec
import matchers.should.Matchers._
import edg.wir.{IndirectDesignPath, DesignPath}
import edg.ExprBuilder._
import edg.compiler.IntValue


class ConstPropAssignTest extends AnyFlatSpec {
  behavior of "ConstProp with element values"

  import ConstPropImplicit._

  it should "handle single-hop directed assignments" in {
    val constProp = new ConstProp()
    constProp.addAssignValue(IndirectDesignPath() + "a", IntValue(2))
    constProp.getValue(IndirectDesignPath() + "a") should equal(Some(IntValue(2)))
  }

  it should "fire callbacks" in {
    var lastSolved: Option[IndirectDesignPath] = None
    val constProp = new ConstProp() {
      override def onParamSolved(param: IndirectDesignPath, value: ExprValue): Unit = {
        lastSolved = Some(param)
      }
    }
    lastSolved should equal(None)
    constProp.addAssignValue(IndirectDesignPath() + "a", IntValue(2))
    lastSolved should equal(Some(IndirectDesignPath() + "a"))
  }

  it should "handle multi-hop directed assignments" in {
    import edgir.expr.expr.BinaryExpr.Op
    val constProp = new ConstProp()
    constProp.addAssignValue(IndirectDesignPath() + "a", IntValue(2))
    constProp.addAssignExpr(IndirectDesignPath() + "b",
      ValueExpr.BinOp(Op.ADD, ValueExpr.Literal(3), ValueExpr.Ref("a")),
    )
    constProp.getValue(IndirectDesignPath() + "a") should equal(Some(IntValue(2)))
    constProp.getValue(IndirectDesignPath() + "b") should equal(Some(IntValue(5)))
  }

  it should "handle multi-hop directed assignments, delayed" in {
    import edgir.expr.expr.BinaryExpr.Op
    val constProp = new ConstProp()
    constProp.addAssignExpr(IndirectDesignPath() + "b",
      ValueExpr.BinOp(Op.ADD, ValueExpr.Literal(3), ValueExpr.Ref("a"))
    )
    constProp.addAssignExpr(IndirectDesignPath() + "c",
      ValueExpr.BinOp(Op.ADD, ValueExpr.Literal(5), ValueExpr.Ref("b"))
    )

    constProp.addAssignValue(IndirectDesignPath() + "a", IntValue(2))

    constProp.getValue(IndirectDesignPath() + "a") should equal(Some(IntValue(2)))
    constProp.getValue(IndirectDesignPath() + "b") should equal(Some(IntValue(5)))
    constProp.getValue(IndirectDesignPath() + "c") should equal(Some(IntValue(10)))
  }

  it should "handle equality assignments" in {
    val constProp = new ConstProp()
    constProp.addAssignValue(IndirectDesignPath() + "a", IntValue(2))

    constProp.addEquality(IndirectDesignPath() + "a", IndirectDesignPath() + "b1")
    constProp.addEquality(IndirectDesignPath() + "b2", IndirectDesignPath() + "a")

    constProp.getValue(IndirectDesignPath() + "b1") should equal(Some(IntValue(2)))
    constProp.getValue(IndirectDesignPath() + "b2") should equal(Some(IntValue(2)))
  }

  it should "handle equality assignments, delayed" in {
    val constProp = new ConstProp()
    constProp.addEquality(IndirectDesignPath() + "a", IndirectDesignPath() + "a1")
    constProp.addEquality(IndirectDesignPath() + "a2", IndirectDesignPath() + "a")
    constProp.getValue(IndirectDesignPath() + "a1") should equal(None)
    constProp.getValue(IndirectDesignPath() + "a2") should equal(None)

    constProp.addAssignValue(IndirectDesignPath() + "a", IntValue(2))

    constProp.getValue(IndirectDesignPath() + "a1") should equal(Some(IntValue(2)))
    constProp.getValue(IndirectDesignPath() + "a2") should equal(Some(IntValue(2)))
  }

  it should "handle directed equality assignments" in {
    val constProp = new ConstProp()
    constProp.addAssignValue(IndirectDesignPath() + "a", IntValue(2))

    constProp.addAssignEqual(IndirectDesignPath() + "b", IndirectDesignPath() + "a")
    constProp.addAssignEqual(IndirectDesignPath() + "c", IndirectDesignPath() + "b")

    constProp.getValue(IndirectDesignPath() + "b") should equal(Some(IntValue(2)))
    constProp.getValue(IndirectDesignPath() + "c") should equal(Some(IntValue(2)))
  }

  it should "handle directed equality assignments, delayed" in {
    val constProp = new ConstProp()
    constProp.addAssignEqual(IndirectDesignPath() + "b", IndirectDesignPath() + "a")
    constProp.addAssignEqual(IndirectDesignPath() + "c", IndirectDesignPath() + "b")
    constProp.getValue(IndirectDesignPath() + "b") should equal(None)
    constProp.getValue(IndirectDesignPath() + "c") should equal(None)

    constProp.addAssignValue(IndirectDesignPath() + "a", IntValue(2))

    constProp.getValue(IndirectDesignPath() + "b") should equal(Some(IntValue(2)))
    constProp.getValue(IndirectDesignPath() + "c") should equal(Some(IntValue(2)))
  }

  it should "handle evaluations on both side of assignments, delayed" in {
    import edgir.expr.expr.BinaryExpr.Op
    val constProp = new ConstProp()
    constProp.addAssignExpr(IndirectDesignPath() + "b",
      ValueExpr.BinOp(Op.ADD, ValueExpr.Literal(2), ValueExpr.Ref("a"))
    )
    constProp.addEquality(IndirectDesignPath() + "b", IndirectDesignPath() + "b1")
    constProp.addEquality(IndirectDesignPath() + "b2", IndirectDesignPath() + "b")
    constProp.addAssignExpr(IndirectDesignPath() + "c1",
      ValueExpr.BinOp(Op.ADD, ValueExpr.Literal(3), ValueExpr.Ref("b1"))
    )
    constProp.addAssignExpr(IndirectDesignPath() + "c2",
      ValueExpr.BinOp(Op.ADD, ValueExpr.Literal(4), ValueExpr.Ref("b2"))
    )
    constProp.getValue(IndirectDesignPath() + "b") should equal(None)
    constProp.getValue(IndirectDesignPath() + "b1") should equal(None)
    constProp.getValue(IndirectDesignPath() + "b2") should equal(None)
    constProp.getValue(IndirectDesignPath() + "c1") should equal(None)
    constProp.getValue(IndirectDesignPath() + "c2") should equal(None)

    constProp.addAssignExpr(IndirectDesignPath() + "a",
      ValueExpr.Literal(1)
    )

    constProp.getValue(IndirectDesignPath() + "b") should equal(Some(IntValue(3)))
    constProp.getValue(IndirectDesignPath() + "b1") should equal(Some(IntValue(3)))
    constProp.getValue(IndirectDesignPath() + "b2") should equal(Some(IntValue(3)))
    constProp.getValue(IndirectDesignPath() + "c1") should equal(Some(IntValue(6)))
    constProp.getValue(IndirectDesignPath() + "c2") should equal(Some(IntValue(7)))
  }

  it should "handle forced set and ignore subsequent assignments" in {
    val constProp = new ConstProp()
    constProp.setForcedValue(DesignPath() + "a", IntValue(3), "forced")
    constProp.addAssignValue(IndirectDesignPath() + "a", IntValue(2))  // should be ignored from above forced-set
    constProp.getValue(IndirectDesignPath() + "a") should equal(Some(IntValue(3)))
  }

  it should "handle clone assignments separately" in {
    val constProp1 = new ConstProp()
    constProp1.addAssignValue(IndirectDesignPath() + "a", IntValue(2))  // shared assignment
    constProp1.getValue(IndirectDesignPath() + "a") should equal(Some(IntValue(2)))

    val constProp2 = new ConstProp()
    constProp2.initFrom(constProp1)
    constProp2.getValue(IndirectDesignPath() + "a") should equal(Some(IntValue(2)))

    constProp1.addAssignValue(IndirectDesignPath() + "b", IntValue(5))
    constProp1.getValue(IndirectDesignPath() + "b") should equal(Some(IntValue(5)))
    constProp2.getValue(IndirectDesignPath() + "b") should equal(None)

    constProp2.addAssignValue(IndirectDesignPath() + "b", IntValue(6))
    constProp2.getValue(IndirectDesignPath() + "b") should equal(Some(IntValue(6)))
    constProp1.getValue(IndirectDesignPath() + "b") should equal(Some(IntValue(5)))
  }

  it should "freeze parameters properly and unfreeze on clone" in {
    import edgir.expr.expr.BinaryExpr.Op

    val constProp1 = new ConstProp(Set(IndirectDesignPath() + "a"))
    constProp1.addAssignValue(IndirectDesignPath() + "a", IntValue(2))
    constProp1.addAssignExpr(IndirectDesignPath() + "b",
      ValueExpr.BinOp(Op.ADD, ValueExpr.Literal(3), ValueExpr.Ref("a")),
    )
    constProp1.getValue(IndirectDesignPath() + "a") should equal(None)
    constProp1.getValue(IndirectDesignPath() + "b") should equal(None)

    val constProp2 = new ConstProp()
    constProp2.initFrom(constProp1)
    constProp2.getValue(IndirectDesignPath() + "a") should equal(Some(IntValue(2)))
    constProp2.getValue(IndirectDesignPath() + "b") should equal(Some(IntValue(5)))  // check second assign triggers
    constProp1.getValue(IndirectDesignPath() + "a") should equal(None)  // should not have changed
    constProp1.getValue(IndirectDesignPath() + "b") should equal(None)  // should not have changed
  }

  it should "allow forcing frozen params" in {
    val constProp1 = new ConstProp(Set(IndirectDesignPath() + "a"))
    constProp1.addAssignValue(IndirectDesignPath() + "a", IntValue(2))
    constProp1.getValue(IndirectDesignPath() + "a") should equal(None)

    val constProp2 = new ConstProp()
    constProp2.initFrom(constProp1, Map(
      DesignPath() + "a" -> (IntValue(3), "forced")
    ))
    constProp2.getValue(IndirectDesignPath() + "a") should equal(Some(IntValue(3)))
  }
}
