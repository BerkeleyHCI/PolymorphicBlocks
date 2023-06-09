package edg.wir

import edg.compiler.IntValue
import edg.{ElemBuilder, ExprBuilder}
import edgrpc.hdl.hdl
import org.scalatest.flatspec.AnyFlatSpec
import org.scalatest.matchers.should.Matchers._

/** Tests operations on the Refinements data structure
  */
class RefinementsTest extends AnyFlatSpec {
  behavior.of("Refinements")

  it should "add refinements with nonoverlapping fields" in {
    val testRefinement = Refinements(
      classRefinements = Map(ElemBuilder.LibraryPath("base1") -> ElemBuilder.LibraryPath("sub1")),
      instanceRefinements = Map(DesignPath() + "elt1" -> ElemBuilder.LibraryPath("sub1")),
      classValues = Map((ElemBuilder.LibraryPath("base1"), ExprBuilder.Ref("param1")) -> IntValue(1)),
      instanceValues = Map(DesignPath() + "elt1" -> IntValue(1))
    ) ++ Refinements(
      classRefinements = Map(ElemBuilder.LibraryPath("base2") -> ElemBuilder.LibraryPath("sub1")),
      instanceRefinements = Map(DesignPath() + "elt2" -> ElemBuilder.LibraryPath("sub1")),
      classValues = Map((ElemBuilder.LibraryPath("base1"), ExprBuilder.Ref("param2")) -> IntValue(1)),
      instanceValues = Map(DesignPath() + "elt2" -> IntValue(1))
    )
    testRefinement should equal(Refinements(
      classRefinements = Map(
        ElemBuilder.LibraryPath("base1") -> ElemBuilder.LibraryPath("sub1"),
        ElemBuilder.LibraryPath("base2") -> ElemBuilder.LibraryPath("sub1")
      ),
      instanceRefinements = Map(
        DesignPath() + "elt1" -> ElemBuilder.LibraryPath("sub1"),
        DesignPath() + "elt2" -> ElemBuilder.LibraryPath("sub1")
      ),
      classValues = Map(
        (ElemBuilder.LibraryPath("base1"), ExprBuilder.Ref("param1")) -> IntValue(1),
        (ElemBuilder.LibraryPath("base1"), ExprBuilder.Ref("param2")) -> IntValue(1),
      ),
      instanceValues = Map(
        DesignPath() + "elt1" -> IntValue(1),
        DesignPath() + "elt2" -> IntValue(1)
      )
    ))
  }

  it should "error on duplicate fields" in {
    assertThrows[IllegalArgumentException] {
      Refinements(
        classRefinements = Map(ElemBuilder.LibraryPath("base1") -> ElemBuilder.LibraryPath("sub1"))
      ) ++ Refinements(
        classRefinements = Map(ElemBuilder.LibraryPath("base1") -> ElemBuilder.LibraryPath("sub1"))
      )
    }
  }

  it should "convert to proto" in {
    Refinements(
      classRefinements = Map(ElemBuilder.LibraryPath("base1") -> ElemBuilder.LibraryPath("sub1")),
      instanceRefinements = Map(DesignPath() + "elt1" -> ElemBuilder.LibraryPath("sub1")),
      classValues = Map((ElemBuilder.LibraryPath("base1"), ExprBuilder.Ref("param1")) -> IntValue(1)),
      instanceValues = Map(DesignPath() + "elt1" -> IntValue(1))
    ).toPb should equal(hdl.Refinements(
      subclasses = Seq(
        hdl.Refinements.Subclass(
          source = hdl.Refinements.Subclass.Source.Cls(ElemBuilder.LibraryPath("base1")),
          replacement = Some(ElemBuilder.LibraryPath("sub1"))
        ),
        hdl.Refinements.Subclass(
          source = hdl.Refinements.Subclass.Source.Path((IndirectDesignPath() + "elt1").toLocalPath),
          replacement = Some(ElemBuilder.LibraryPath("sub1"))
        ),
      ),
      values = Seq(
        hdl.Refinements.Value(
          source = hdl.Refinements.Value.Source.ClsParam(
            value = hdl.Refinements.Value.ClassParamPath(
              cls = Some(ElemBuilder.LibraryPath("base1")),
              paramPath = Some(ExprBuilder.Ref("param1"))
            )
          ),
          value = hdl.Refinements.Value.Value.Expr(IntValue(1).toLit)
        ),
        hdl.Refinements.Value(
          source = hdl.Refinements.Value.Source.Path((IndirectDesignPath() + "elt1").toLocalPath),
          value = hdl.Refinements.Value.Value.Expr(IntValue(1).toLit)
        ),
      )
    ))
  }
}
