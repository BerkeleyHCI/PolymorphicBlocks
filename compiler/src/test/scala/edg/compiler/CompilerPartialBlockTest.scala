package edg.compiler

import edg.ElemBuilder._
import edg.ExprBuilder.{Ref, ValInit, ValueExpr}
import edg.wir.{DesignPath, EdgirLibrary, IndirectDesignPath, Refinements}
import edg.{CompilerTestUtil, ElemBuilder, ExprBuilder, wir}
import org.scalatest._
import org.scalatest.flatspec.AnyFlatSpec
import org.scalatest.matchers.should.Matchers._

import scala.collection.SeqMap

/** Tests partial compilation and fork-from-partial compilation for frozen blocks.
  */
class CompilerPartialBlockTest extends AnyFlatSpec with CompilerTestUtil {
  val inputDesign = Design(Block.Block(
    "topDesign",
    blocks = SeqMap(
      "source" -> Block.Library("sourceContainerBlock"),
      "sink" -> Block.Library("sinkContainerBlock"),
    ),
    links = SeqMap(
      "link" -> Link.Library("link")
    ),
    constraints = SeqMap(
      "sourceConnect" -> Constraint.Connected(Ref("source", "port"), Ref("link", "source")),
      "sinkConnect" -> Constraint.Connected(Ref("sink", "port"), Ref("link", "sink")),
    )
  ))

  val referencePartialElaborated = Design(Block.Block(
    "topDesign",
    blocks = SeqMap(
      "source" -> Block.Block(
        selfClass = "sourceContainerBlock",
        ports = SeqMap(
          "port" -> Port.Port(selfClass = "sourcePort"),
        ),
        blocks = SeqMap(
          "inner" -> Block.Library("sourceBlock")
        ),
        constraints = SeqMap(
          "export" -> Constraint.Exported(Ref("port"), Ref("inner", "port"))
        )
      ),
      "sink" -> Block.Block(
        selfClass = "sinkContainerBlock",
        ports = SeqMap(
          "port" -> Port.Port(selfClass = "sinkPort"),
        ),
        blocks = SeqMap(
          "inner" -> Block.Block(
            selfClass = "sinkBlock",
            ports = SeqMap(
              "port" -> Port.Port(selfClass = "sinkPort"),
            )
          )
        ),
        constraints = SeqMap(
          "export" -> Constraint.Exported(Ref("port"), Ref("inner", "port"))
        )
      ),
    ),
    links = SeqMap(
      "link" -> Link.Link(
        selfClass = "link",
        ports = SeqMap(
          "source" -> Port.Port(selfClass = "sourcePort"),
          "sink" -> Port.Port(selfClass = "sinkPort"),
        )
      )
    ),
    constraints = SeqMap(
      "sourceConnect" -> Constraint.Connected(Ref("source", "port"), Ref("link", "source")),
      "sinkConnect" -> Constraint.Connected(Ref("sink", "port"), Ref("link", "sink")),
    )
  ))

  val referenceFullElaborated = Design(Block.Block(
    "topDesign",
    blocks = SeqMap(
      "source" -> Block.Block(
        selfClass = "sourceContainerBlock",
        ports = SeqMap(
          "port" -> Port.Port(selfClass = "sourcePort"),
        ),
        blocks = SeqMap(
          "inner" -> Block.Block(
            selfClass = "sourceBlock",
            ports = SeqMap(
              "port" -> Port.Port(selfClass = "sourcePort"),
            )
          )
        ),
        constraints = SeqMap(
          "export" -> Constraint.Exported(Ref("port"), Ref("inner", "port"))
        )
      ),
      "sink" -> Block.Block(
        selfClass = "sinkContainerBlock",
        ports = SeqMap(
          "port" -> Port.Port(selfClass = "sinkPort"),
        ),
        blocks = SeqMap(
          "inner" -> Block.Block(
            selfClass = "sinkBlock",
            ports = SeqMap(
              "port" -> Port.Port(selfClass = "sinkPort"),
            )
          )
        ),
        constraints = SeqMap(
          "export" -> Constraint.Exported(Ref("port"), Ref("inner", "port"))
        )
      ),
    ),
    links = SeqMap(
      "link" -> Link.Link(
        selfClass = "link",
        ports = SeqMap(
          "source" -> Port.Port(selfClass = "sourcePort"),
          "sink" -> Port.Port(selfClass = "sinkPort"),
        )
      )
    ),
    constraints = SeqMap(
      "sourceConnect" -> Constraint.Connected(Ref("source", "port"), Ref("link", "source")),
      "sinkConnect" -> Constraint.Connected(Ref("sink", "port"), Ref("link", "sink")),
    )
  ))

  "Compiler on path-based partial design specification" should "not compile those blocks" in {
    val compiler = new Compiler(
      inputDesign,
      new EdgirLibrary(CompilerExpansionTest.library),
      partial = PartialCompile(blocks = Seq(DesignPath() + "source" + "inner"))
    )
    val compiled = compiler.compile()
    compiled should equal(referencePartialElaborated)
    compiler.getErrors() should contain(
      CompilerError.Unelaborated(
        ElaborateRecord.ExpandBlock(
          DesignPath() + "source" + "inner",
          ElemBuilder.LibraryPath("sourceBlock"),
          0.5f
        ),
        Set()
      )
    )
  }

  "Compiler on class-based partial design specification" should "not compile those blocks" in {
    val compiler = new Compiler(
      inputDesign,
      new EdgirLibrary(CompilerExpansionTest.library),
      partial = PartialCompile(classes = Seq(ElemBuilder.LibraryPath("sourceBlock")))
    )
    val compiled = compiler.compile()
    compiled should equal(referencePartialElaborated)
    compiler.getErrors() should contain(
      CompilerError.Unelaborated(
        ElaborateRecord.ExpandBlock(
          DesignPath() + "source" + "inner",
          ElemBuilder.LibraryPath("sourceBlock"),
          0.5f
        ),
        Set()
      )
    )
  }

  "Compiler on partial design specification" should "fork independently" in {
    val compiler = new Compiler(
      inputDesign,
      new EdgirLibrary(CompilerExpansionTest.library),
      partial = PartialCompile(blocks = Seq(DesignPath() + "source" + "inner"))
    )
    val compiled = compiler.compile()

    val forkedCompiler = compiler.fork(Refinements(), PartialCompile())
    val forkedCompiled = forkedCompiler.compile()

    forkedCompiled should equal(referenceFullElaborated)
    forkedCompiler.getErrors() should be(empty)

    // check original was not changed
    compiled should equal(referencePartialElaborated)
    compiler.getErrors() should contain(
      CompilerError.Unelaborated(
        ElaborateRecord.ExpandBlock(
          DesignPath() + "source" + "inner",
          ElemBuilder.LibraryPath("sourceBlock"),
          0.5f
        ),
        Set()
      )
    )

    // check that we can fork multiple times
    val forkedCompiler2 = compiler.fork(Refinements(), PartialCompile())
    val forkedCompiled2 = forkedCompiler2.compile()

    forkedCompiled2 should equal(referenceFullElaborated)
    forkedCompiler2.getErrors() should be(empty)
  }
}
