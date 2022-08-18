package edg.wir

import edg.compiler.IntValue
import edg.{ElemBuilder, ExprBuilder}
import org.scalatest.flatspec.AnyFlatSpec
import org.scalatest.matchers.should.Matchers._


/** Tests operations on the Refinements data structure
  */
class RefinementsTest extends AnyFlatSpec {
  behavior of "Refinements"

  it should "add refinements with nonoverlapping fields" in {
    val testRefinement = Refinements(
      classRefinements=Map(ElemBuilder.LibraryPath("base1") -> ElemBuilder.LibraryPath("sub1")),
      instanceRefinements=Map(DesignPath() + "elt1" -> ElemBuilder.LibraryPath("sub1")),
      classValues=Map(ElemBuilder.LibraryPath("base1") -> Map(ExprBuilder.Ref("param1") -> IntValue(1))),
      instanceValues=Map(DesignPath() + "elt1" -> IntValue(1))
    ) ++ Refinements(
      classRefinements=Map(ElemBuilder.LibraryPath("base2") -> ElemBuilder.LibraryPath("sub1")),
      instanceRefinements=Map(DesignPath() + "elt2" -> ElemBuilder.LibraryPath("sub1")),
      classValues = Map(ElemBuilder.LibraryPath("base1") -> Map(ExprBuilder.Ref("param2") -> IntValue(1))),
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
          ElemBuilder.LibraryPath("base1") -> Map(
            ExprBuilder.Ref("param1") -> IntValue(1),
            ExprBuilder.Ref("param2") -> IntValue(1)
          )),
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
}
