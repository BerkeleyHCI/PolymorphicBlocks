package edg.compiler

import org.scalatest._
import org.scalatest.flatspec.AnyFlatSpec
import matchers.should.Matchers._
import edg.ElemBuilder._
import edg.ExprBuilder.Ref
import edg.wir


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
        ports = Map(
          "port" -> Port.Library("sourcePort"),
        )
      ),
      Block.Block("sinkBlock",
        ports = Map(
          "port" -> Port.Library("sinkPort"),
        )
      ),
      Block.Block("sourceContainerBlock",
        ports = Map(
          "port" -> Port.Library("sourcePort"),
        ),
        blocks = Map(
          "inner" -> Block.Library("sourceBlock")
        ),
        constraints = Map(
          "export" -> Constraint.Exported(Ref("port"), Ref("inner", "port"))
        )
      ),
      Block.Block("sinkContainerBlock",
        ports = Map(
          "port" -> Port.Library("sinkPort"),
        ),
        blocks = Map(
          "inner" -> Block.Library("sinkBlock")
        ),
        constraints = Map(
          "export" -> Constraint.Exported(Ref("port"), Ref("inner", "port"))
        )
      ),
    ),
    links = Seq(
      Link.Link("link",
        ports = Map(
          "source" -> Port.Library("sourcePort"),
          "sink" -> Port.Library("sinkPort"),
        )
      ),
    )
  )
}


/** Basic test that tests block, link, and port expansion behavior, by matching the reference output exactly.
  */
class CompilerExpansionTest extends AnyFlatSpec {


  "Compiler on design with single source and sink" should "expand blocks" in {
    val inputDesign = Design(Block.Block("topDesign",
      blocks = Map(
        "source" -> Block.Library("sourceBlock"),
        "sink" -> Block.Library("sinkBlock"),
      ),
      links = Map(
        "link" -> Link.Library("link")
      ),
      constraints = Map(
        "sourceConnect" -> Constraint.Connected(Ref("source", "port"), Ref("link", "source")),
        "sinkConnect" -> Constraint.Connected(Ref("sink", "port"), Ref("link", "sink")),
      )
    ))
    val referenceElaborated = Design(Block.Block("topDesign",
      blocks = Map(
        "source" -> Block.Block(selfClass="sourceBlock",
          ports = Map(
            "port" -> Port.Port(selfClass="sourcePort"),
          )
        ),
        "sink" -> Block.Block(selfClass="sinkBlock",
          ports = Map(
            "port" -> Port.Port(selfClass="sinkPort"),
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
    val compiler = new Compiler(inputDesign, new wir.EdgirLibrary(CompilerExpansionTest.library))
    compiler.compile should equal(referenceElaborated)
  }

  "Compiler on design with single nested source and sink" should "expand blocks" in {
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
    val referenceElaborated = Design(Block.Block("topDesign",
      blocks = Map(
        "source" -> Block.Block(selfClass="sourceContainerBlock",
          ports = Map(
            "port" -> Port.Port(selfClass="sourcePort"),
          ),
          blocks = Map(
            "inner" -> Block.Block(selfClass="sourceBlock",
              ports = Map(
                "port" -> Port.Port(selfClass="sourcePort"),
              )
            )
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
    val compiler = new Compiler(inputDesign, new wir.EdgirLibrary(CompilerExpansionTest.library))
    compiler.compile should equal(referenceElaborated)
  }
}
