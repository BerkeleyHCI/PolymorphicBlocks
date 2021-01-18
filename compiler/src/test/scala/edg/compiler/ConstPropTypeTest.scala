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
    constProp.addDeclaration(DesignPath.root + "a", ValInit.Integer)
    constProp.addDeclaration(DesignPath.root + "b", ValInit.Integer)
    constProp.addDeclaration(DesignPath.root + "c", ValInit.Integer)
    constProp.getUnsolved should equal(Set(
      DesignPath.root + "a",
      DesignPath.root + "b",
      DesignPath.root + "c",
    ))

    constProp.addAssignment(IndirectDesignPath.root + "a", DesignPath.root,
      ValueExpr.Literal(1),
      SourceLocator.empty
    )
    constProp.getUnsolved should equal(Set(
      DesignPath.root + "b",
      DesignPath.root + "c",
    ))

    constProp.addAssignment(IndirectDesignPath.root + "b", DesignPath.root,
      ValueExpr.Literal(1),
      SourceLocator.empty
    )
    constProp.getUnsolved should equal(Set(
      DesignPath.root + "c",
    ))

    constProp.addAssignment(IndirectDesignPath.root + "c", DesignPath.root,
      ValueExpr.Literal(1),
      SourceLocator.empty
    )
    constProp.getUnsolved should equal(Set())
  }

  it should "getUnsolved ignoring indirect paths" in {
    val constProp = new ConstProp()
    constProp.addDeclaration(DesignPath.root + "a", ValInit.Integer)
    constProp.addAssignment(IndirectDesignPath.root + "a", DesignPath.root,
      ValueExpr.Literal(1),
      SourceLocator.empty
    )
    constProp.addAssignment(IndirectDesignPath.root + "port" + IndirectStep.ConnectedLink() + "param", DesignPath.root,
      ValueExpr.Literal(1),
      SourceLocator.empty
    )
    constProp.getUnsolved should equal(Set())
  }

  it should "return declared types" in {
    val constProp = new ConstProp()
    constProp.addDeclaration(DesignPath.root + "int", ValInit.Integer)
    constProp.addDeclaration(DesignPath.root + "float", ValInit.Floating)
    constProp.addDeclaration(DesignPath.root + "boolean", ValInit.Boolean)

    constProp.getType(DesignPath.root + "int") should equal(Some(classOf[IntValue]))
    constProp.getType(DesignPath.root + "float") should equal(Some(classOf[FloatValue]))
    constProp.getType(DesignPath.root + "boolean") should equal(Some(classOf[BooleanValue]))
  }
}
