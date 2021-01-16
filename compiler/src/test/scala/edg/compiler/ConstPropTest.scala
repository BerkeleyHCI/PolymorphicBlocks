package edg.compiler

import org.scalatest._
import org.scalatest.flatspec.AnyFlatSpec
import matchers.should.Matchers._
import edg.wir.{IndirectDesignPath, DesignPath}
import ExprBuilder._


class ConstPropTest extends AnyFlatSpec {
  "ConstProp" should "work properly"

  it should "handle single-hop directed assignments" in {
    val constProp = new ConstProp()
    constProp.addAssignment(IndirectDesignPath.root + "a",
      DesignPath.root,
      ValueExpr.Literal(2.0),
      new SourceLocator()
    )
    constProp.getValue(IndirectDesignPath.root + "a") should equal(Some(FloatValue(2.0f)))
  }

  it should "handle multi-hop directed assignments" in {
    import edg.expr.expr.BinaryExpr.Op
    val constProp = new ConstProp()
    constProp.addAssignment(IndirectDesignPath.root + "a",
      DesignPath.root,
      ValueExpr.Literal(2.0),
      new SourceLocator()
    )
    constProp.addAssignment(IndirectDesignPath.root + "b",
      DesignPath.root,
      ValueExpr.BinOp(Op.ADD, ValueExpr.Literal(3.0), ValueExpr.Ref("a")),
      new SourceLocator()
    )
    constProp.getValue(IndirectDesignPath.root + "a") should equal(Some(FloatValue(2.0f)))
    constProp.getValue(IndirectDesignPath.root + "b") should equal(Some(FloatValue(5.0f)))
  }

  it should "handle multi-hop directed assignments, delayed" in {
    import edg.expr.expr.BinaryExpr.Op
    val constProp = new ConstProp()
    constProp.addAssignment(IndirectDesignPath.root + "b",
      DesignPath.root,
      ValueExpr.BinOp(Op.ADD, ValueExpr.Literal(3.0), ValueExpr.Ref("a")),
      new SourceLocator()
    )
    constProp.addAssignment(IndirectDesignPath.root + "c",
      DesignPath.root,
      ValueExpr.BinOp(Op.ADD, ValueExpr.Literal(5.0), ValueExpr.Ref("b")),
      new SourceLocator()
    )

    constProp.addAssignment(IndirectDesignPath.root + "a",
      DesignPath.root,
      ValueExpr.Literal(2.0),
      new SourceLocator()
    )
    constProp.getValue(IndirectDesignPath.root + "a") should equal(Some(FloatValue(2.0f)))
    constProp.getValue(IndirectDesignPath.root + "b") should equal(Some(FloatValue(5.0f)))
    constProp.getValue(IndirectDesignPath.root + "c") should equal(Some(FloatValue(10.0f)))
  }

  it should "handle equality assignments"

  it should "handle equality assignments, delayed"
}
