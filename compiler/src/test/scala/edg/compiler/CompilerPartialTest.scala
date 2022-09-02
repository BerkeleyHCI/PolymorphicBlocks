package edg.compiler

import edg.ElemBuilder._
import edg.ExprBuilder.{Ref, ValInit, ValueExpr}
import edg.wir.{DesignPath, EdgirLibrary, IndirectDesignPath, Refinements}
import edg.{CompilerTestUtil, wir}
import org.scalatest._
import org.scalatest.flatspec.AnyFlatSpec
import org.scalatest.matchers.should.Matchers._


/** Tests partial compilation and fork-from-partial compilation.
  */
class CompilerPartialTest extends AnyFlatSpec with CompilerTestUtil {
  val inputDesign = Design(Block.Block("topDesign",
    blocks = Map(
      "source" -> Block.Library("sourceContainerBlock"),
      "sink" -> Block.Library("sinkContainerBlock"),
    ),
    links = Map(
      "link" -> Link.Library("link")
    ),
    constraints = Map(
      "sourceConnect" -> Constraint.Connected(Ref("source", "port"), Ref("link", "source")),
      "sinkConnect" -> Constraint.Connected(Ref("sink", "port"), Ref("link", "sink")),
    )
  ))

  "Compiler on partial design specification" should "not compile those blocks" in {
    val referenceElaborated = Design(Block.Block("topDesign",
      blocks = Map(
        "source" -> Block.Block(selfClass="sourceContainerBlock",
          ports = Map(
            "port" -> Port.Port(selfClass="sourcePort"),
          ),
          blocks = Map(
            "inner" -> Block.Library("sourceBlock")
          ),
          constraints = Map(
            "export" -> Constraint.Exported(Ref("port"), Ref("inner", "port"))
          )
        ),
        "sink" -> Block.Block(selfClass="sinkContainerBlock",
          ports = Map(
            "port" -> Port.Port(selfClass="sinkPort"),
          ),
          blocks = Map(
            "inner" -> Block.Block(selfClass="sinkBlock",
              ports = Map(
                "port" -> Port.Port(selfClass="sinkPort"),
              )
            )
          ),
          constraints = Map(
            "export" -> Constraint.Exported(Ref("port"), Ref("inner", "port"))
          )
        ),
      ),
      links = Map(
        "link" -> Link.Link(selfClass="link",
          ports = Map(
            "source" -> Port.Port(selfClass="sourcePort"),
            "sink" -> Port.Port(selfClass="sinkPort"),
          )
        )
      ),
      constraints = Map(
        "sourceConnect" -> Constraint.Connected(Ref("source", "port"), Ref("link", "source")),
        "sinkConnect" -> Constraint.Connected(Ref("sink", "port"), Ref("link", "sink")),
      )
    ))
    val compiler = new Compiler(inputDesign, new EdgirLibrary(CompilerExpansionTest.library),
      partial=PartialCompile(blocks=Seq(DesignPath() + "source" + "inner")))
    val compiled = compiler.compile()
    compiled should equal(referenceElaborated)
  }
}
