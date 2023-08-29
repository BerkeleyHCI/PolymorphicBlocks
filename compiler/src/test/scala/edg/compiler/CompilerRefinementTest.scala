package edg.compiler

import org.scalatest._
import org.scalatest.flatspec.AnyFlatSpec
import matchers.should.Matchers._
import edg.ElemBuilder._
import edg.ExprBuilder.{Ref, ValInit, ValueExpr}
import edg.{CompilerTestUtil, EdgirUtils, wir}
import edg.wir.{DesignPath, IndirectDesignPath, IndirectStep, Refinements}

import scala.collection.SeqMap

/** Tests refinement using the supplemental refinements data structure.
  */
class CompilerRefinementTest extends AnyFlatSpec with CompilerTestUtil {
  val library = Library(
    ports = Seq(
      Port.Port("port"),
    ),
    blocks = Seq(
      Block.Block(
        "superclassBlock",
        params = SeqMap(
          "superParam" -> ValInit.Integer,
        ),
        ports = SeqMap(
          "port" -> Port.Library("port"),
        )
      ),
      Block.Block(
        "superclassDefaultBlock",
        defaultRefinement = Some("subclassBlock"),
        params = SeqMap(
          "superParam" -> ValInit.Integer,
        ),
        ports = SeqMap(
          "port" -> Port.Library("port"),
        )
      ),
      Block.Block(
        "subclassBlock",
        superclasses = Seq("superclassBlock", "superclassDefaultBlock"),
        params = SeqMap(
          "superParam" -> ValInit.Integer,
          "subParam" -> ValInit.Integer,
        ),
        ports = SeqMap(
          "port" -> Port.Library("port"),
        )
      ),
      Block.Block(
        "subclassDefaultBlock", // contains a default param
        superclasses = Seq("superclassBlock"),
        params = SeqMap(
          "superParam" -> ValInit.Integer,
          "defaultParam" -> ValInit.Integer,
        ),
        paramDefaults = SeqMap(
          "defaultParam" -> ValueExpr.Literal(42),
        ),
        ports = SeqMap(
          "port" -> Port.Library("port"),
        )
      ),
      Block.Block(
        "subclassPortBlock", // contains a new port
        superclasses = Seq("superclassBlock"),
        params = SeqMap(
          "superParam" -> ValInit.Integer,
        ),
        ports = SeqMap(
          "port" -> Port.Library("port"),
          "newPort" -> Port.Library("port"),
          "newArray" -> Port.Array("port", Seq(), Port.Library("port")),
        )
      ),
      Block.Block(
        "subsubclassBlock",
        superclasses = Seq("subclassBlock"),
        superSuperclasses = Seq("superclassBlock", "superclassDefaultBlock"),
        params = SeqMap(
          "superParam" -> ValInit.Integer,
          "subParam" -> ValInit.Integer,
        ),
        ports = SeqMap(
          "port" -> Port.Library("port"),
        )
      ),
      Block.Block(
        "block", // specifically no superclass
        params = SeqMap(
          "superParam" -> ValInit.Integer,
        ),
        ports = SeqMap(
          "port" -> Port.Library("port"),
        )
      ),
    ),
    links = Seq(
    )
  )

  val inputDesign = Design(Block.Block(
    "topDesign",
    blocks = SeqMap(
      "block" -> Block.Library("superclassBlock"),
    )
  ))

  "Compiler on design with subclass refinement" should "work" in {
    val expected = Design(Block.Block(
      "topDesign",
      blocks = SeqMap(
        "block" -> Block.Block(
          "subclassBlock",
          superclasses = Seq("superclassBlock", "superclassDefaultBlock"),
          prerefine = "superclassBlock",
          params = SeqMap(
            "superParam" -> ValInit.Integer,
            "subParam" -> ValInit.Integer,
          ),
          ports = SeqMap(
            "port" -> Port.Port(selfClass = "port"),
          ),
          meta = Some(Map(
            "refinedNewPorts" -> EdgirUtils.strSeqToMeta(Seq()),
            "refinedNewParams" -> EdgirUtils.strSeqToMeta(Seq("subParam")),
          ))
        ),
      )
    ))
    testCompile(
      inputDesign,
      library,
      refinements = Refinements(
        classRefinements = Map(LibraryPath("superclassBlock") -> LibraryPath("subclassBlock"))
      ),
      expectedDesign = Some(expected)
    )
  }

  "Compiler on design with subclass refinement" should "error if selected class is not a subclass" in {
    val compiler = new Compiler(
      inputDesign,
      new wir.EdgirLibrary(library),
      Refinements(
        instanceRefinements = Map(DesignPath() + "block" -> LibraryPath("block"))
      )
    )
    val compiled = compiler.compile()
    new DesignStructuralValidate().map(compiled) should equal(Seq(
      CompilerError.RefinementSubclassError(
        DesignPath() + "block",
        LibraryPath("block"),
        LibraryPath("superclassBlock")
      )
    ))
  }

  "Compiler on design with instance refinement" should "work" in {
    val expected = Design(Block.Block(
      "topDesign",
      blocks = SeqMap(
        "block" -> Block.Block(
          "subclassBlock",
          superclasses = Seq("superclassBlock", "superclassDefaultBlock"),
          prerefine = "superclassBlock",
          params = SeqMap(
            "superParam" -> ValInit.Integer,
            "subParam" -> ValInit.Integer,
          ),
          ports = SeqMap(
            "port" -> Port.Port(selfClass = "port"),
          ),
          meta = Some(Map(
            "refinedNewPorts" -> EdgirUtils.strSeqToMeta(Seq()),
            "refinedNewParams" -> EdgirUtils.strSeqToMeta(Seq("subParam")),
          ))
        ),
      )
    ))
    testCompile(
      inputDesign,
      library,
      refinements = Refinements(
        instanceRefinements = Map(DesignPath() + "block" -> LibraryPath("subclassBlock"))
      ),
      expectedDesign = Some(expected)
    )
  }

  "Compiler on refinement with default parameters" should "work" in {
    val (compiler, compiled) = testCompile(
      inputDesign,
      library,
      refinements = Refinements(
        instanceRefinements = Map(DesignPath() + "block" -> LibraryPath("subclassDefaultBlock"))
      )
    )
    compiler.getValue(IndirectDesignPath() + "block" + "defaultParam") should equal(Some(IntValue(42)))
  }

  "Compiler on refinement with overridden default parameters" should "work" in {
    val (compiler, compiled) = testCompile(
      inputDesign,
      library,
      refinements = Refinements(
        instanceRefinements = Map(DesignPath() + "block" -> LibraryPath("subclassDefaultBlock")),
        instanceValues = Map(DesignPath() + "block" + "defaultParam" -> IntValue(3))
      )
    )
    compiler.getValue(IndirectDesignPath() + "block" + "defaultParam") should equal(Some(IntValue(3)))
  }

  "Compiler on refinement with new ports" should "work" in {
    val (compiler, compiled) = testCompile(
      inputDesign,
      library,
      refinements = Refinements(
        instanceRefinements = Map(DesignPath() + "block" -> LibraryPath("subclassPortBlock"))
      )
    )
    compiler.getValue(IndirectDesignPath() + "block" + "newPort" + IndirectStep.IsConnected) should equal(
      Some(BooleanValue(false))
    )
    compiler.getValue(IndirectDesignPath() + "block" + "newArray" + IndirectStep.Allocated) should equal(
      Some(ArrayValue(Seq()))
    )
  }

  "Compiler on design with subclass values" should "work" in {
    val expected = Design(Block.Block(
      "topDesign",
      blocks = SeqMap(
        "block" -> Block.Block(
          selfClass = "superclassBlock",
          params = SeqMap(
            "superParam" -> ValInit.Integer,
          ),
          ports = SeqMap(
            "port" -> Port.Port(selfClass = "port"),
          )
        ),
      )
    ))
    val (compiler, compiled) = testCompile(
      inputDesign,
      library,
      refinements = Refinements(
        classValues = Map((LibraryPath("superclassBlock"), Ref("superParam")) -> IntValue(5))
      ),
      expectedDesign = Some(expected)
    )
    compiler.getValue(IndirectDesignPath() + "block" + "superParam") should equal(Some(IntValue(5)))
  }

  "Compiler on design with path values" should "work" in {
    val (compiler, compiled) = testCompile(
      inputDesign,
      library,
      refinements = Refinements(
        instanceValues = Map(DesignPath() + "block" + "superParam" -> IntValue(3))
      )
    )
    compiler.getValue(IndirectDesignPath() + "block" + "superParam") should equal(Some(IntValue(3)))
  }

  "Compiler on design with path assignments" should "work" in {
    val (compiler, compiled) = testCompile(
      inputDesign,
      library,
      refinements = Refinements(
        instanceRefinements = Map(DesignPath() + "block" -> LibraryPath("subclassBlock")), // need the sub param
        instanceValues = Map(DesignPath() + "block" + "superParam" -> IntValue(3)),
        instanceAssigns = Map(DesignPath() + "block" + "subParam" -> (DesignPath() + "block" + "superParam"))
      )
    )
    compiler.getValue(IndirectDesignPath() + "block" + "subParam") should equal(Some(IntValue(3)))
  }

  "Compiler on design with path values" should "supersede class values" in {
    val (compiler, compiled) = testCompile(
      inputDesign,
      library,
      refinements = Refinements(
        classValues = Map((LibraryPath("superclassBlock"), Ref("superParam")) -> IntValue(0)),
        instanceValues = Map(DesignPath() + "block" + "superParam" -> IntValue(3))
      )
    )
    compiler.getValue(IndirectDesignPath() + "block" + "superParam") should equal(Some(IntValue(3)))
  }

  "Compiler on block with default refinement" should "work" in {
    val blockDefaultInputDesign = Design(Block.Block(
      "topDesign",
      blocks = SeqMap(
        "block" -> Block.Library("superclassDefaultBlock"),
      )
    ))
    val expected = Design(Block.Block(
      "topDesign",
      blocks = SeqMap(
        "block" -> Block.Block(
          "subclassBlock",
          superclasses = Seq("superclassBlock", "superclassDefaultBlock"),
          prerefine = "superclassDefaultBlock",
          params = SeqMap(
            "superParam" -> ValInit.Integer,
            "subParam" -> ValInit.Integer,
          ),
          ports = SeqMap(
            "port" -> Port.Port(selfClass = "port"),
          ),
          meta = Some(Map(
            "refinedNewPorts" -> EdgirUtils.strSeqToMeta(Seq()),
            "refinedNewParams" -> EdgirUtils.strSeqToMeta(Seq("subParam")),
          ))
        ),
      )
    ))
    testCompile(blockDefaultInputDesign, library, expectedDesign = Some(expected))
  }

  "Compiler on design with chained (instance + class) refinement" should "work" in {
    val expected = Design(Block.Block(
      "topDesign",
      blocks = SeqMap(
        "block" -> Block.Block(
          "subsubclassBlock",
          superclasses = Seq("subclassBlock"),
          superSuperclasses = Seq("superclassBlock", "superclassDefaultBlock"),
          prerefine = "superclassBlock",
          params = SeqMap(
            "superParam" -> ValInit.Integer,
            "subParam" -> ValInit.Integer,
          ),
          ports = SeqMap(
            "port" -> Port.Port(selfClass = "port"),
          ),
          meta = Some(Map(
            "refinedNewPorts" -> EdgirUtils.strSeqToMeta(Seq()),
            "refinedNewParams" -> EdgirUtils.strSeqToMeta(Seq("subParam")),
          ))
        ),
      )
    ))
    testCompile(
      inputDesign,
      library,
      refinements = Refinements(
        instanceRefinements = Map(DesignPath() + "block" -> LibraryPath("subclassBlock")),
        classRefinements = Map(LibraryPath("subclassBlock") -> LibraryPath("subsubclassBlock"))
      ),
      expectedDesign = Some(expected)
    )
  }

  "Compiler on design with chained (default + class) refinement" should "work" in {
    val blockDefaultInputDesign = Design(Block.Block(
      "topDesign",
      blocks = SeqMap(
        "block" -> Block.Library("superclassDefaultBlock"),
      )
    ))
    val expected = Design(Block.Block(
      "topDesign",
      blocks = SeqMap(
        "block" -> Block.Block(
          "subsubclassBlock",
          superclasses = Seq("subclassBlock"),
          superSuperclasses = Seq("superclassBlock", "superclassDefaultBlock"),
          prerefine = "superclassDefaultBlock",
          params = SeqMap(
            "superParam" -> ValInit.Integer,
            "subParam" -> ValInit.Integer,
          ),
          ports = SeqMap(
            "port" -> Port.Port(selfClass = "port"),
          ),
          meta = Some(Map(
            "refinedNewPorts" -> EdgirUtils.strSeqToMeta(Seq()),
            "refinedNewParams" -> EdgirUtils.strSeqToMeta(Seq("subParam")),
          ))
        ),
      )
    ))
    testCompile(
      blockDefaultInputDesign,
      library,
      refinements = Refinements(
        classRefinements = Map(LibraryPath("subclassBlock") -> LibraryPath("subsubclassBlock"))
      ),
      expectedDesign = Some(expected)
    )
  }
}
