package edg.compiler

import org.scalatest._
import org.scalatest.flatspec.AnyFlatSpec
import matchers.should.Matchers._
import edg.ElemBuilder._
import edg.ExprBuilder.{Ref, ValInit}
import edg.wir
import edg.wir.{DesignPath, IndirectDesignPath, Refinements}


/** Basic test that tests block, link, and port expansion behavior, by matching the reference output exactly.
  */
class CompilerRefinementTest extends AnyFlatSpec {
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
    val compiler = new Compiler(inputDesign, new wir.EdgirLibrary(library), Refinements(
      classRefinements = Map(LibraryPath("superclassBlock") -> LibraryPath("subclassBlock"))
    ))
    compiler.compile() should equal(expected)
    compiler.getErrors() shouldBe empty
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
    val compiler = new Compiler(inputDesign, new wir.EdgirLibrary(library), Refinements(
      instanceRefinements = Map(DesignPath() + "block" -> LibraryPath("subclassBlock"))
    ))
    compiler.compile() should equal(expected)
    compiler.getErrors() shouldBe empty
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
    val compiler = new Compiler(inputDesign, new wir.EdgirLibrary(library), Refinements(
      classValues = Map(LibraryPath("superclassBlock") -> Seq(
        (Ref("superParam"), IntValue(5))),
      )
    ))
    compiler.compile()
    compiler.getErrors() shouldBe empty
    compiler.getValue(IndirectDesignPath() + "block" + "superParam") should equal(Some(IntValue(5)))
  }

  "Compiler on design with path values" should "work" in {
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
    val compiler = new Compiler(inputDesign, new wir.EdgirLibrary(library), Refinements(
      instanceValues = Map(DesignPath() + "block" + "superParam" -> IntValue(3))
    ))
    compiler.compile()
    compiler.getErrors() shouldBe empty
    compiler.getValue(IndirectDesignPath() + "block" + "superParam") should equal(Some(IntValue(3)))
  }
}
