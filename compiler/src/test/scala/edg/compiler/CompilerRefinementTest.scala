package edg.compiler

import org.scalatest._
import org.scalatest.flatspec.AnyFlatSpec
import matchers.should.Matchers._
import edg.ElemBuilder._
import edg.ExprBuilder.{Ref, ValInit}
import edg.wir
import edg.wir.{DesignPath, IndirectDesignPath}


/** Basic test that tests block, link, and port expansion behavior, by matching the reference output exactly.
  */
class CompilerRefinementTest extends AnyFlatSpec {
  val library = Library(
    ports = Map(
      "port" -> Port.Port(),
    ),
    blocks = Map(
      "superclassBlock" -> Block.Block(
        params = Map(
          "superParam" -> ValInit.Integer,
        ),
        ports = Map(
          "port" -> Port.Library("port"),
        )
      ),
      "subclassBlock" -> Block.Block(
        superclass="superclassBlock",
        params = Map(
          "superParam" -> ValInit.Integer,
          "subParam" -> ValInit.Integer,
        ),
        ports = Map(
          "port" -> Port.Library("port"),
        )
      ),
      "block" -> Block.Block(  // specifically no superclass
        params = Map(
          "superParam" -> ValInit.Integer,
        ),
        ports = Map(
          "port" -> Port.Library("port"),
        )
      ),
    ),
    links = Map(
    )
  )

  val inputDesign = Design(Block.Block(
    blocks = Map(
      "block" -> Block.Library("superclassBlock"),
    )
  ))

  "Compiler on design with subclass refinement" should "work" in {
    val expected = Design(Block.Block(
      blocks = Map(
        "block" -> Block.Block(superclass="subclassBlock",
          prerefine="superclassBlock",
          params = Map(
            "superParam" -> ValInit.Integer,
            "subParam" -> ValInit.Integer,
          ),
          ports = Map(
            "port" -> Port.Port(superclass="port"),
          )
        ),
      )
    ))
    val compiler = new Compiler(inputDesign, new wir.EdgirLibrary(library), Refinements(
      classRefinements = Map(LibraryPath("superclassBlock") -> LibraryPath("subclassBlock"))
    ))
    compiler.compile() should equal(expected)
  }

  "Compiler on design with subclass refinement" should "error if selected class is not a subclass" in {
    val compiler = new Compiler(inputDesign, new wir.EdgirLibrary(library), Refinements(
      instanceRefinements = Map(DesignPath.root + "block" -> LibraryPath("block"))
    ))
    assertThrows[IllegalArgumentException] {
      compiler.compile()
    }
  }

  "Compiler on design with instance refinement" should "work" in {
    val expected = Design(Block.Block(
      blocks = Map(
        "block" -> Block.Block(superclass="subclassBlock",
          prerefine="superclassBlock",
          params = Map(
            "superParam" -> ValInit.Integer,
            "subParam" -> ValInit.Integer,
          ),
          ports = Map(
            "port" -> Port.Port(superclass="port"),
          )
        ),
      )
    ))
    val compiler = new Compiler(inputDesign, new wir.EdgirLibrary(library), Refinements(
      instanceRefinements = Map(DesignPath.root + "block" -> LibraryPath("subclassBlock"))
    ))
    compiler.compile() should equal(expected)
  }

  "Compiler on design with subclass values" should "work" in {
    val expected = Design(Block.Block(
      blocks = Map(
        "block" -> Block.Block(superclass="superclassBlock",
          params = Map(
            "superParam" -> ValInit.Integer,
          ),
          ports = Map(
            "port" -> Port.Port(superclass="port"),
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
    compiler.getValue(IndirectDesignPath.root + "block" + "superParam") should equal(Some(IntValue(5)))
  }

  "Compiler on design with path values" should "work" in {
    val expected = Design(Block.Block(
      blocks = Map(
        "block" -> Block.Block(superclass="superclassBlock",
          params = Map(
            "superParam" -> ValInit.Integer,
          ),
          ports = Map(
            "port" -> Port.Port(superclass="port"),
          )
        ),
      )
    ))
    val compiler = new Compiler(inputDesign, new wir.EdgirLibrary(library), Refinements(
      instanceValues = Map(DesignPath.root + "block" + "superParam" -> IntValue(3))
    ))
    compiler.compile()
    compiler.getValue(IndirectDesignPath.root + "block" + "superParam") should equal(Some(IntValue(3)))
  }
}
