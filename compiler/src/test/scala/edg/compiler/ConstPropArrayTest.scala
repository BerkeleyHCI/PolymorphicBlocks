package edg.compiler

import org.scalatest._
import org.scalatest.flatspec.AnyFlatSpec
import matchers.should.Matchers._
import edg.wir.{DesignPath, IndirectDesignPath, IndirectStep}
import edg.ExprBuilder._
import edg.compiler.CompilerError.ExprError

class ConstPropArrayTest extends AnyFlatSpec {
  behavior.of("ConstProp with array paths")

  import edgir.expr.expr
  import ConstPropImplicit._

  /** Adds array assigns to a ConstProp object. Note: all paths (including prefix and anything in the expr) are
    * referenced from the argument root.
    */
  def addArray(
      constProp: ConstProp,
      root: Seq[String],
      length: Int,
      exprFn: Int => expr.ValueExpr,
      pathPrefix: Seq[String],
      pathSuffix: Seq[String]
  ): Unit = {
    for (i <- 0 until length) {
      constProp.addDeclaration(DesignPath() ++ root ++ pathPrefix + i.toString ++ pathSuffix, ValInit.Integer)
      constProp.addAssignExpr(
        IndirectDesignPath() ++ root ++ pathPrefix + i.toString ++ pathSuffix,
        exprFn(i)
      )
    }
    constProp.addAssignValue(
      IndirectDesignPath() ++ root ++ pathPrefix + IndirectStep.Elements,
      ArrayValue((0 until length).map(i => TextValue(i.toString)))
    )
  }

  it should "read out elements" in {
    val constProp = new ConstProp()
    addArray(constProp, Seq(), 3, ValueExpr.Literal(_), Seq("ports"), Seq("param"))

    constProp.getValue(IndirectDesignPath() + "ports" + "0" + "param") should equal(Some(IntValue(0)))
    constProp.getValue(IndirectDesignPath() + "ports" + "1" + "param") should equal(Some(IntValue(1)))
    constProp.getValue(IndirectDesignPath() + "ports" + "2" + "param") should equal(Some(IntValue(2)))
  }

  it should "read out sum" in {
    import edgir.expr.expr.UnarySetExpr.Op
    val constProp = new ConstProp()
    addArray(constProp, Seq(), 5, { i => ValueExpr.Literal(i + 1) }, Seq("ports"), Seq("param"))

    constProp.addDeclaration(DesignPath() + "reduce", ValInit.Integer)
    constProp.addAssignExpr(
      IndirectDesignPath() + "reduce",
      ValueExpr.UnarySetOp(Op.SUM, ValueExpr.MapExtract(Ref("ports"), "param"))
    )
    constProp.getValue(IndirectDesignPath() + "reduce") should equal(Some(IntValue(1 + 2 + 3 + 4 + 5)))
  }

  it should "read out maximum" in {
    import edgir.expr.expr.UnarySetExpr.Op
    val constProp = new ConstProp()
    addArray(constProp, Seq(), 4, { i => ValueExpr.Literal(i + 2) }, Seq("ports"), Seq("param"))

    constProp.addDeclaration(DesignPath() + "reduce", ValInit.Integer)
    constProp.addAssignExpr(
      IndirectDesignPath() + "reduce",
      ValueExpr.UnarySetOp(Op.MAXIMUM, ValueExpr.MapExtract(Ref("ports"), "param"))
    )
    constProp.getValue(IndirectDesignPath() + "reduce") should equal(Some(IntValue(5)))
  }

  it should "read out intersection" in {
    import edgir.expr.expr.UnarySetExpr.Op
    val constProp = new ConstProp()
    addArray(constProp, Seq(), 4, { i => ValueExpr.Literal(i.toFloat, (i + 4).toFloat) }, Seq("ports"), Seq("param"))

    constProp.addDeclaration(DesignPath() + "reduce", ValInit.Integer)
    constProp.addAssignExpr(
      IndirectDesignPath() + "reduce",
      ValueExpr.UnarySetOp(Op.INTERSECTION, ValueExpr.MapExtract(Ref("ports"), "param"))
    )
    constProp.getValue(IndirectDesignPath() + "reduce") should equal(Some(RangeValue(3.0, 4.0)))
  }

  it should "fail to SetExtract for different values" in {
    import edgir.expr.expr.UnarySetExpr.Op
    val constProp = new ConstProp()
    addArray(constProp, Seq(), 4, { i => ValueExpr.Literal(i + 2) }, Seq("ports"), Seq("param"))
    constProp.addDeclaration(DesignPath() + "reduce", ValInit.Integer)
    constProp.addAssignExpr(
      IndirectDesignPath() + "reduce",
      ValueExpr.UnarySetOp(Op.SET_EXTRACT, ValueExpr.MapExtract(Ref("ports"), "param"))
    )
    constProp.getValue(IndirectDesignPath() + "reduce") should equal(None)
    constProp.getErrors should not be empty
  }

  it should "SetExtract for same values" in {
    import edgir.expr.expr.UnarySetExpr.Op
    val constProp = new ConstProp()
    addArray(constProp, Seq(), 4, { i => ValueExpr.Literal(2) }, Seq("ports"), Seq("param"))

    constProp.addDeclaration(DesignPath() + "reduce", ValInit.Integer)
    constProp.addAssignExpr(
      IndirectDesignPath() + "reduce",
      ValueExpr.UnarySetOp(Op.SET_EXTRACT, ValueExpr.MapExtract(Ref("ports"), "param"))
    )
    constProp.getValue(IndirectDesignPath() + "reduce") should equal(Some(IntValue(2)))
  }

  // TODO: this might not be needed right now, but will be eventually
  it should "work on delayed ops" in {
    import edgir.expr.expr.UnarySetExpr.Op
    val constProp = new ConstProp()

    constProp.addDeclaration(DesignPath() + "reduce", ValInit.Integer)
    constProp.addAssignExpr(
      IndirectDesignPath() + "reduce",
      ValueExpr.UnarySetOp(Op.SUM, ValueExpr.MapExtract(Ref("ports"), "param"))
    )

    addArray(constProp, Seq(), 5, { i => ValueExpr.Literal(i + 1) }, Seq("ports"), Seq("param"))
    constProp.getValue(IndirectDesignPath() + "reduce") should equal(Some(IntValue(1 + 2 + 3 + 4 + 5)))
  }
}
