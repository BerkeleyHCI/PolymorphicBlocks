package edg.compiler

import org.scalatest._
import org.scalatest.flatspec.AnyFlatSpec
import matchers.should.Matchers._
import edg.ElemBuilder._
import edg.ExprBuilder.Ref
import edg.{CompilerTestUtil, wir}

import scala.collection.SeqMap


/** Library with simple problem structure that can be shared across tests.
  */
object CompilerExpansionTest {
  val library = Library(
    ports = Seq(
       Port.Port("sourcePort"),
       Port.Port("sinkPort"),
    ),
    blocks = Seq(
      Block.Block("sourceBlock",
        ports = SeqMap(
          "port" -> Port.Library("sourcePort"),
        )
      ),
      Block.Block("sinkBlock",
        ports = SeqMap(
          "port" -> Port.Library("sinkPort"),
        )
      ),
      Block.Block("sourceContainerBlock",
        ports = SeqMap(
          "port" -> Port.Library("sourcePort"),
        ),
        blocks = SeqMap(
          "inner" -> Block.Library("sourceBlock")
        ),
        constraints = SeqMap(
          "export" -> Constraint.Exported(Ref("port"), Ref("inner", "port"))
        )
      ),
      Block.Block("sinkContainerBlock",
        ports = SeqMap(
          "port" -> Port.Library("sinkPort"),
        ),
        blocks = SeqMap(
          "inner" -> Block.Library("sinkBlock")
        ),
        constraints = SeqMap(
          "export" -> Constraint.Exported(Ref("port"), Ref("inner", "port"))
        )
      ),
    ),
    links = Seq(
      Link.Link("link",
        ports = SeqMap(
          "source" -> Port.Library("sourcePort"),
          "sink" -> Port.Library("sinkPort"),
        )
      ),
    )
  )
}


/** Basic test that tests block, link, and port expansion behavior, by matching the reference output exactly.
  */
class CompilerExpansionTest extends AnyFlatSpec with CompilerTestUtil {
  "Compiler on design with single source and sink" should "expand blocks" in {
    val inputDesign = Design(Block.Block("topDesign",
      blocks = SeqMap(
        "source" -> Block.Library("sourceBlock"),
        "sink" -> Block.Library("sinkBlock"),
      ),
      links = SeqMap(
        "link" -> Link.Library("link")
      ),
      constraints = SeqMap(
        "sourceConnect" -> Constraint.Connected(Ref("source", "port"), Ref("link", "source")),
        "sinkConnect" -> Constraint.Connected(Ref("sink", "port"), Ref("link", "sink")),
      )
    ))
    val referenceElaborated = Design(Block.Block("topDesign",
      blocks = SeqMap(
        "source" -> Block.Block(selfClass="sourceBlock",
          ports = SeqMap(
            "port" -> Port.Port(selfClass="sourcePort"),
          )
        ),
        "sink" -> Block.Block(selfClass="sinkBlock",
          ports = SeqMap(
            "port" -> Port.Port(selfClass="sinkPort"),
          )
        ),
      ),
      links = SeqMap(
        "link" -> Link.Link(selfClass="link",
          ports = SeqMap(
            "source" -> Port.Port(selfClass="sourcePort"),
            "sink" -> Port.Port(selfClass="sinkPort"),
          )
        )
      ),
      constraints = SeqMap(
        "sourceConnect" -> Constraint.Connected(Ref("source", "port"), Ref("link", "source")),
        "sinkConnect" -> Constraint.Connected(Ref("sink", "port"), Ref("link", "sink")),
      )
    ))
    testCompile(inputDesign, CompilerExpansionTest.library, expectedDesign=Some(referenceElaborated))
  }

  "Compiler on design with single nested source and sink" should "expand blocks" in {
    val inputDesign = Design(Block.Block("topDesign",
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
    val referenceElaborated = Design(Block.Block("topDesign",
      blocks = SeqMap(
        "source" -> Block.Block(selfClass="sourceContainerBlock",
          ports = SeqMap(
            "port" -> Port.Port(selfClass="sourcePort"),
          ),
          blocks = SeqMap(
            "inner" -> Block.Block(selfClass="sourceBlock",
              ports = SeqMap(
                "port" -> Port.Port(selfClass="sourcePort"),
              )
            )
          ),
          constraints = SeqMap(
            "export" -> Constraint.Exported(Ref("port"), Ref("inner", "port"))
          )
        ),
        "sink" -> Block.Block(selfClass="sinkContainerBlock",
          ports = SeqMap(
            "port" -> Port.Port(selfClass="sinkPort"),
          ),
          blocks = SeqMap(
            "inner" -> Block.Block(selfClass="sinkBlock",
              ports = SeqMap(
                "port" -> Port.Port(selfClass="sinkPort"),
              )
            )
          ),
          constraints = SeqMap(
            "export" -> Constraint.Exported(Ref("port"), Ref("inner", "port"))
          )
        ),
      ),
      links = SeqMap(
        "link" -> Link.Link(selfClass="link",
          ports = SeqMap(
            "source" -> Port.Port(selfClass="sourcePort"),
            "sink" -> Port.Port(selfClass="sinkPort"),
          )
        )
      ),
      constraints = SeqMap(
        "sourceConnect" -> Constraint.Connected(Ref("source", "port"), Ref("link", "source")),
        "sinkConnect" -> Constraint.Connected(Ref("sink", "port"), Ref("link", "sink")),
      )
    ))
    testCompile(inputDesign, CompilerExpansionTest.library, expectedDesign=Some(referenceElaborated))
  }
}
