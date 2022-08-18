package edg.compiler

import org.scalatest._
import org.scalatest.flatspec.AnyFlatSpec
import matchers.should.Matchers._
import edg.ElemBuilder._
import edg.ExprBuilder.{Ref, ValInit, ValueExpr}
import edg.{CompilerTestUtil, wir}
import edg.wir.{DesignPath, IndirectDesignPath, Refinements}


/** Tests refinement using the supplemental refinements data structure.
  */
class CompilerRefinementTest extends AnyFlatSpec with CompilerTestUtil {
  val library = Library(
    ports = Seq(
      Port.Port("port"),
    ),
    blocks = Seq(
      Block.Block("superclassBlock",
        params = Map(
          "superParam" -> ValInit.Integer,
        ),
        ports = Map(
          "port" -> Port.Library("port"),
        )
      ),
      Block.Block("subclassBlock",
        superclasses = Seq("superclassBlock"),
        params = Map(
          "superParam" -> ValInit.Integer,
          "subParam" -> ValInit.Integer,
        ),
        ports = Map(
          "port" -> Port.Library("port"),
        )
      ),
      Block.Block("subclassDefaultBlock",  // contains a default param
        superclasses = Seq("superclassBlock"),
        params = Map(
          "superParam" -> ValInit.Integer,
          "defaultParam" -> ValInit.Integer,
        ),
        paramDefaults = Map(
          "defaultParam" -> ValueExpr.Literal(42),
        ),
        ports = Map(
          "port" -> Port.Library("port"),
        )
      ),
      Block.Block("block",  // specifically no superclass
        params = Map(
          "superParam" -> ValInit.Integer,
        ),
        ports = Map(
          "port" -> Port.Library("port"),
        )
      ),
    ),
    links = Seq(
    )
  )

  val inputDesign = Design(Block.Block("topDesign",
    blocks = Map(
      "block" -> Block.Library("superclassBlock"),
    )
  ))

  "Compiler on design with subclass refinement" should "work" in {
    val expected = Design(Block.Block("topDesign",
      blocks = Map(
        "block" -> Block.Block("subclassBlock",
          superclasses=Seq("superclassBlock"),
          prerefine="superclassBlock",
          params = Map(
            "superParam" -> ValInit.Integer,
            "subParam" -> ValInit.Integer,
          ),
          ports = Map(
            "port" -> Port.Port(selfClass="port"),
          )
        ),
      )
    ))
    testCompile(inputDesign, library, refinements=Refinements(
        classRefinements = Map(LibraryPath("superclassBlock") -> LibraryPath("subclassBlock"))),
      expectedDesign=Some(expected))
  }

  "Compiler on design with subclass refinement" should "error if selected class is not a subclass" in {
    val compiler = new Compiler(inputDesign, new wir.EdgirLibrary(library), Refinements(
      instanceRefinements = Map(DesignPath() + "block" -> LibraryPath("block"))
    ))
    compiler.compile()
    compiler.getErrors() should not be (empty)
  }

  "Compiler on design with instance refinement" should "work" in {
    val expected = Design(Block.Block("topDesign",
      blocks = Map(
        "block" -> Block.Block("subclassBlock",
          superclasses=Seq("superclassBlock"),
          prerefine="superclassBlock",
          params = Map(
            "superParam" -> ValInit.Integer,
            "subParam" -> ValInit.Integer,
          ),
          ports = Map(
            "port" -> Port.Port(selfClass="port"),
          )
        ),
      )
    ))
    testCompile(inputDesign, library, refinements=Refinements(
        instanceRefinements = Map(DesignPath() + "block" -> LibraryPath("subclassBlock"))),
      expectedDesign=Some(expected))
  }

  "Compiler on refinement with default parameters" should "work" in {
    val (compiler, compiled) = testCompile(inputDesign, library, refinements=Refinements(
        instanceRefinements = Map(DesignPath() + "block" -> LibraryPath("subclassDefaultBlock"))))
    compiler.getValue(IndirectDesignPath() + "block" + "defaultParam") should equal(Some(IntValue(42)))
  }

  "Compiler on refinement with overridden default parameters" should "work" in {
    val (compiler, compiled) = testCompile(inputDesign, library, refinements=Refinements(
      instanceRefinements = Map(DesignPath() + "block" -> LibraryPath("subclassDefaultBlock")),
      instanceValues = Map(DesignPath() + "block" + "defaultParam" -> IntValue(3))))
    compiler.getValue(IndirectDesignPath() + "block" + "defaultParam") should equal(Some(IntValue(3)))
  }

  "Compiler on design with subclass values" should "work" in {
    val expected = Design(Block.Block("topDesign",
      blocks = Map(
        "block" -> Block.Block(selfClass="superclassBlock",
          params = Map(
            "superParam" -> ValInit.Integer,
          ),
          ports = Map(
            "port" -> Port.Port(selfClass="port"),
          )
        ),
      )
    ))
    val (compiler, compiled) = testCompile(inputDesign, library, refinements=Refinements(
      classValues = Map(LibraryPath("superclassBlock") -> Map(
        Ref("superParam") -> IntValue(5)),
      )),
      expectedDesign=Some(expected))
    compiler.getValue(IndirectDesignPath() + "block" + "superParam") should equal(Some(IntValue(5)))
  }

  "Compiler on design with path values" should "work" in {
    val (compiler, compiled) = testCompile(inputDesign, library, refinements=Refinements(
      instanceValues = Map(DesignPath() + "block" + "superParam" -> IntValue(3))))
    compiler.getValue(IndirectDesignPath() + "block" + "superParam") should equal(Some(IntValue(3)))
  }
}
