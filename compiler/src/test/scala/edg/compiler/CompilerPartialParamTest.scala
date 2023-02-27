package edg.compiler

import edg.ElemBuilder._
import edg.ExprBuilder.{Ref, ValInit}
import edg.wir.{DesignPath, EdgirLibrary, IndirectDesignPath, Refinements}
import edg.{CompilerTestUtil, ElemBuilder, ExprBuilder}
import edgir.elem.elem
import org.scalatest.flatspec.AnyFlatSpec
import org.scalatest.matchers.should.Matchers._

import scala.collection.SeqMap


/** Tests partial compilation and fork-from-partial compilation for frozen parameters.
  */
class CompilerPartialParamTest extends AnyFlatSpec with CompilerTestUtil {
  val inputDesign = Design(Block.Block("topDesign",
    params = SeqMap("param" -> ValInit.Integer),
    constraints = SeqMap(
      "assign" -> Constraint.Assign(Ref("param"), ExprBuilder.ValueExpr.Literal(1)),
    )
  ))

  val inputDesignSubclass = Design(Block.Block("subTopDesign", superclasses=Seq("topDesign"),
    params = SeqMap("param" -> ValInit.Integer),
    constraints = SeqMap(
      "assign" -> Constraint.Assign(Ref("param"), ExprBuilder.ValueExpr.Literal(1)),
    )
  ))

  "Compiler on path-based partial design specification" should "not evaluate that parameter" in {
    val compiler = new Compiler(inputDesign, new EdgirLibrary(Library()),
      partial=PartialCompile(params=Seq(DesignPath() + "param")))
    compiler.compile()
    compiler.getValue(IndirectDesignPath() + "param") shouldEqual None
  }

  "Compiler on class-based partial design specification" should "not evaluate that parameter" in {
    val compiler = new Compiler(inputDesign, new EdgirLibrary(Library()),
      partial = PartialCompile(classParams = Seq((ElemBuilder.LibraryPath("topDesign"), Ref("param")))))
    compiler.compile()
    compiler.getValue(IndirectDesignPath() + "param") shouldEqual None
  }

  "Compiler on subclass-based partial design specification" should "not evaluate that parameter" in {
    val compiler = new Compiler(inputDesignSubclass, new EdgirLibrary(Library(
      blocks = Seq(  // needed for subclass to resolve
        elem.BlockLike(`type`=elem.BlockLike.Type.Hierarchy(inputDesign.getContents)),
        elem.BlockLike(`type`=elem.BlockLike.Type.Hierarchy(inputDesignSubclass.getContents))
      ))),
      partial = PartialCompile(classParams = Seq((ElemBuilder.LibraryPath("topDesign"), Ref("param")))))
    compiler.compile()
    compiler.getValue(IndirectDesignPath() + "param") shouldEqual None
  }

  "Compiler on class-based partial design specification and refinement" should "evaluate to the refinement" in {
    val compiler = new Compiler(inputDesign, new EdgirLibrary(Library()),
      partial = PartialCompile(classParams = Seq((ElemBuilder.LibraryPath("topDesign"), Ref("param")))))
    compiler.compile()
    compiler.getValue(IndirectDesignPath() + "param") shouldEqual None

    val forkedCompiler = compiler.fork(Refinements(
      classValues=Map(ElemBuilder.LibraryPath("topDesign") -> Map(Ref("param") -> IntValue(2)))
    ), PartialCompile())
    forkedCompiler.compile()
    forkedCompiler.getValue(IndirectDesignPath() + "param") shouldEqual Some(IntValue(2))
  }

  "Compiler on partial design specification" should "fork independently" in {
    val compiler = new Compiler(inputDesign, new EdgirLibrary(Library()),
      partial = PartialCompile(params = Seq(DesignPath() + "param")))
    compiler.compile()

    val forkedCompiler = compiler.fork(Refinements(), PartialCompile())
    forkedCompiler.compile()
    forkedCompiler.getValue(IndirectDesignPath() + "param") shouldEqual Some(IntValue(1))

    // check original was not changed
    compiler.getValue(IndirectDesignPath() + "param") shouldEqual None

    // check that we can fork multiple times
    val forkedCompiler2 = compiler.fork(Refinements(), PartialCompile())
    forkedCompiler2.compile()

    forkedCompiler.getValue(IndirectDesignPath() + "param") shouldEqual Some(IntValue(1))
  }
}
