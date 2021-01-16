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

  it should "handle multi-hop directed assignments"

  it should "handle multi-hop directed assignments, delayed"

  it should "handle equality assignments"

  it should "handle equality assignments, delayed"
}
