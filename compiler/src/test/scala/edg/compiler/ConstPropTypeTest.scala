package edg.compiler

import org.scalatest._
import org.scalatest.flatspec.AnyFlatSpec
import matchers.should.Matchers._
import edg.wir.{IndirectDesignPath, DesignPath}
import ExprBuilder._


class ConstPropTypeTest extends AnyFlatSpec {
  "ConstProp with types and declarations" should "work properly"

  it should "getUnsolved of declared types" in {
    val constProp = new ConstProp()
    constProp.addDeclaration(DesignPath.root + "a", ValInit.Integer)
    constProp.addDeclaration(DesignPath.root + "b", ValInit.Integer)
    constProp.addDeclaration(DesignPath.root + "c", ValInit.Integer)


  }

  it should "getUnsolved excluding indirect paths" in {
    val constProp = new ConstProp()
    constProp.addDeclaration(DesignPath.root + "a", ValInit.Integer)
    constProp.addDeclaration(DesignPath.root + "b", ValInit.Integer)
    constProp.addDeclaration(DesignPath.root + "c", ValInit.Integer)
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
