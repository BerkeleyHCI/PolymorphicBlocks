package edg.compiler

import org.scalatest._
import org.scalatest.flatspec.AnyFlatSpec
import matchers.should.Matchers._
import edg.wir.{IndirectDesignPath, DesignPath}
import edg.ExprBuilder._


class ConstPropAssignTest extends AnyFlatSpec {
  "ConstProp" should "work properly"

  it should "handle single-hop directed assignments" in {
    val constProp = new ConstProp()
    constProp.addAssignment(IndirectDesignPath.root + "a",
      DesignPath.root,
      ValueExpr.Literal(2),
      SourceLocator.empty
    )
    constProp.getValue(IndirectDesignPath.root + "a") should equal(Some(IntValue(2)))
  }

  it should "handle multi-hop directed assignments" in {
    import edg.expr.expr.BinaryExpr.Op
    val constProp = new ConstProp()
    constProp.addAssignment(IndirectDesignPath.root + "a",
      DesignPath.root,
      ValueExpr.Literal(2),
      SourceLocator.empty
    )
    constProp.addAssignment(IndirectDesignPath.root + "b",
      DesignPath.root,
      ValueExpr.BinOp(Op.ADD, ValueExpr.Literal(3), ValueExpr.Ref("a")),
      SourceLocator.empty
    )
    constProp.getValue(IndirectDesignPath.root + "a") should equal(Some(IntValue(2)))
    constProp.getValue(IndirectDesignPath.root + "b") should equal(Some(IntValue(5)))
  }

  it should "handle multi-hop directed assignments, delayed" in {
    import edg.expr.expr.BinaryExpr.Op
    val constProp = new ConstProp()
    constProp.addAssignment(IndirectDesignPath.root + "b",
      DesignPath.root,
      ValueExpr.BinOp(Op.ADD, ValueExpr.Literal(3), ValueExpr.Ref("a")),
      SourceLocator.empty
    )
    constProp.addAssignment(IndirectDesignPath.root + "c",
      DesignPath.root,
      ValueExpr.BinOp(Op.ADD, ValueExpr.Literal(5), ValueExpr.Ref("b")),
      SourceLocator.empty
    )

    constProp.addAssignment(IndirectDesignPath.root + "a",
      DesignPath.root,
      ValueExpr.Literal(2),
      SourceLocator.empty
    )
    constProp.getValue(IndirectDesignPath.root + "a") should equal(Some(IntValue(2)))
    constProp.getValue(IndirectDesignPath.root + "b") should equal(Some(IntValue(5)))
    constProp.getValue(IndirectDesignPath.root + "c") should equal(Some(IntValue(10)))
  }

  it should "handle equality assignments" in {
    val constProp = new ConstProp()
    constProp.addAssignment(IndirectDesignPath.root + "a",
      DesignPath.root,
      ValueExpr.Literal(2),
      SourceLocator.empty
    )
    constProp.addEquality(IndirectDesignPath.root + "a", IndirectDesignPath.root + "b1")
    constProp.addEquality(IndirectDesignPath.root + "b2", IndirectDesignPath.root + "a")

    constProp.getValue(IndirectDesignPath.root + "b1") should equal(Some(IntValue(2)))
    constProp.getValue(IndirectDesignPath.root + "b2") should equal(Some(IntValue(2)))
  }

  it should "handle equality assignments, delayed" in {
    val constProp = new ConstProp()
    constProp.addEquality(IndirectDesignPath.root + "a", IndirectDesignPath.root + "a1")
    constProp.addEquality(IndirectDesignPath.root + "a2", IndirectDesignPath.root + "a")
    constProp.getValue(IndirectDesignPath.root + "a1") should equal(None)
    constProp.getValue(IndirectDesignPath.root + "a2") should equal(None)

    constProp.addAssignment(IndirectDesignPath.root + "a",
      DesignPath.root,
      ValueExpr.Literal(2),
      SourceLocator.empty
    )

    constProp.getValue(IndirectDesignPath.root + "a1") should equal(Some(IntValue(2)))
    constProp.getValue(IndirectDesignPath.root + "a2") should equal(Some(IntValue(2)))
  }

  it should "handle evaluations on both side of assignments, delayed" in {
    import edg.expr.expr.BinaryExpr.Op
    val constProp = new ConstProp()
    constProp.addAssignment(IndirectDesignPath.root + "b", DesignPath.root,
      ValueExpr.BinOp(Op.ADD, ValueExpr.Literal(2), ValueExpr.Ref("a")),
      SourceLocator.empty
    )
    constProp.addEquality(IndirectDesignPath.root + "b", IndirectDesignPath.root + "b1")
    constProp.addEquality(IndirectDesignPath.root + "b2", IndirectDesignPath.root + "b")
    constProp.addAssignment(IndirectDesignPath.root + "c1", DesignPath.root,
      ValueExpr.BinOp(Op.ADD, ValueExpr.Literal(3), ValueExpr.Ref("b1")),
      SourceLocator.empty
    )
    constProp.addAssignment(IndirectDesignPath.root + "c2", DesignPath.root,
      ValueExpr.BinOp(Op.ADD, ValueExpr.Literal(4), ValueExpr.Ref("b2")),
      SourceLocator.empty
    )
    constProp.getValue(IndirectDesignPath.root + "b") should equal(None)
    constProp.getValue(IndirectDesignPath.root + "b1") should equal(None)
    constProp.getValue(IndirectDesignPath.root + "b2") should equal(None)
    constProp.getValue(IndirectDesignPath.root + "c1") should equal(None)
    constProp.getValue(IndirectDesignPath.root + "c2") should equal(None)

    constProp.addAssignment(IndirectDesignPath.root + "a", DesignPath.root,
      ValueExpr.Literal(1),
      SourceLocator.empty
    )

    constProp.getValue(IndirectDesignPath.root + "b") should equal(Some(IntValue(3)))
    constProp.getValue(IndirectDesignPath.root + "b1") should equal(Some(IntValue(3)))
    constProp.getValue(IndirectDesignPath.root + "b2") should equal(Some(IntValue(3)))
    constProp.getValue(IndirectDesignPath.root + "c1") should equal(Some(IntValue(6)))
    constProp.getValue(IndirectDesignPath.root + "c2") should equal(Some(IntValue(7)))
  }
}
