package edg.compiler

import org.scalatest._
import org.scalatest.flatspec.AnyFlatSpec
import matchers.should.Matchers._
import edg.wir.{IndirectDesignPath, IndirectStep, DesignPath}
import edg.ExprBuilder._


class ConstPropTypeTest extends AnyFlatSpec {
  behavior of "ConstProp with types and declarations"

  import ConstPropImplicit._

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

    constProp.addAssignExpr(IndirectDesignPath() + "a",
      ValueExpr.Literal(1)
    )
    constProp.getUnsolved should equal(Set(
      DesignPath() + "b",
      DesignPath() + "c",
    ))

    constProp.addAssignExpr(IndirectDesignPath() + "b",
      ValueExpr.Literal(1)
    )
    constProp.getUnsolved should equal(Set(
      DesignPath() + "c",
    ))

    constProp.addAssignExpr(IndirectDesignPath() + "c",
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

  it should "track types of clones separately" in {
    val constProp1 = new ConstProp()
    constProp1.addDeclaration(DesignPath() + "int", ValInit.Integer)

    val constProp2 = new ConstProp()
    constProp2.initFrom(constProp1)
    constProp1.getType(DesignPath() + "int") should equal(Some(classOf[IntValue]))
    constProp2.getType(DesignPath() + "int") should equal(Some(classOf[IntValue]))  // track common types

    constProp1.addDeclaration(DesignPath() + "float", ValInit.Floating)  // add different types
    constProp2.addDeclaration(DesignPath() + "boolean", ValInit.Boolean)
    constProp1.getType(DesignPath() + "boolean") should equal(None)  // types should be independent
    constProp2.getType(DesignPath() + "float") should equal(None)

    constProp1.getUnsolved should equal(Set(
      DesignPath() + "int",
      DesignPath() + "float",
    ))
    constProp2.getUnsolved should equal(Set(
      DesignPath() + "int",
      DesignPath() + "boolean",
    ))

    constProp1.addAssignExpr(IndirectDesignPath() + "int",  // unsolved should be independent
      ValueExpr.Literal(1)
    )
    constProp1.getUnsolved should equal(Set(
      DesignPath() + "float",
    ))
    constProp2.getUnsolved should equal(Set(
      DesignPath() + "int",
      DesignPath() + "boolean",
    ))
  }
}
