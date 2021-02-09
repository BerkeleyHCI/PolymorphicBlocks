package edg.compiler

import org.scalatest._
import org.scalatest.flatspec.AnyFlatSpec
import matchers.should.Matchers._
import edg.wir.{IndirectDesignPath, IndirectStep, DesignPath}
import edg.ExprBuilder._


class ConstPropTypeTest extends AnyFlatSpec {
  behavior of "ConstProp with types and declarations"

  it should "getUnsolved of declared types" in {
    val constProp = new ConstProp()
    constProp.addDeclaration(DesignPath() + "a", ValInit.Integer)
    constProp.addDeclaration(DesignPath() + "b", ValInit.Integer)
    constProp.addDeclaration(DesignPath() + "c", ValInit.Integer)
    constProp.getUnsolved should equal(Set(
      DesignPath() + "a",
      DesignPath() + "b",
      DesignPath() + "c",
    ))

    constProp.addAssignment(IndirectDesignPath() + "a", DesignPath(),
      ValueExpr.Literal(1)
    )
    constProp.getUnsolved should equal(Set(
      DesignPath() + "b",
      DesignPath() + "c",
    ))

    constProp.addAssignment(IndirectDesignPath() + "b", DesignPath(),
      ValueExpr.Literal(1)
    )
    constProp.getUnsolved should equal(Set(
      DesignPath() + "c",
    ))

    constProp.addAssignment(IndirectDesignPath() + "c", DesignPath(),
      ValueExpr.Literal(1)
    )
    constProp.getUnsolved should equal(Set())
  }

  it should "getUnsolved ignoring indirect paths" in {
    val constProp = new ConstProp()
    constProp.addDeclaration(DesignPath() + "a", ValInit.Integer)
    constProp.addAssignment(IndirectDesignPath() + "a", DesignPath(),
      ValueExpr.Literal(1)
    )
    constProp.addAssignment(IndirectDesignPath() + "port" + IndirectStep.ConnectedLink + "param", DesignPath(),
      ValueExpr.Literal(1)
    )
    constProp.getUnsolved should equal(Set())
  }

  it should "return declared types" in {
    val constProp = new ConstProp()
    constProp.addDeclaration(DesignPath() + "int", ValInit.Integer)
    constProp.addDeclaration(DesignPath() + "float", ValInit.Floating)
    constProp.addDeclaration(DesignPath() + "boolean", ValInit.Boolean)

    constProp.getType(DesignPath() + "int") should equal(Some(classOf[IntValue]))
    constProp.getType(DesignPath() + "float") should equal(Some(classOf[FloatValue]))
    constProp.getType(DesignPath() + "boolean") should equal(Some(classOf[BooleanValue]))
  }
}
