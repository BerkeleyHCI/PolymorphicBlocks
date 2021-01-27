package edg.compiler

import org.scalatest._
import org.scalatest.flatspec.AnyFlatSpec
import matchers.should.Matchers._
import edg.ElemBuilder._
import edg.ExprBuilder.Ref
import edg.wir


/** Basic test that tests block, link, and port expansion behavior, by matching the reference output exactly.
  */
class CompilerExpansionTest extends AnyFlatSpec {
  val library = Library(
    ports = Map(
      "sourcePort" -> Port.Port(),
      "sinkPort" -> Port.Port(),
    ),
    blocks = Map(
      "sourceBlock" -> Block.Block(
        ports = Map(
          "port" -> Port.Library("sourcePort"),
        )
      ),
      "sinkBlock" -> Block.Block(
        ports = Map(
          "port" -> Port.Library("sinkPort"),
        )
      ),
      "sourceContainerBlock" -> Block.Block(
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
      "sinkContainerBlock" -> Block.Block(
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
    links = Map(
      "link" -> Link.Link(
        ports = Map(
          "source" -> Port.Library("sourcePort"),
          "sink" -> Port.Library("sinkPort"),
        )
      ),
    )
  )

  "Compiler on design with single source and sink" should "expand blocks" in {
    val inputDesign = Design(Block.Block(
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
    val referenceElaborated = Design(Block.Block(
      blocks = Map(
        "source" -> Block.Block(superclass="sourceBlock",
          ports = Map(
            "port" -> Port.Port(superclass="sourcePort"),
          )
        ),
        "sink" -> Block.Block(superclass="sinkBlock",
          ports = Map(
            "port" -> Port.Port(superclass="sinkPort"),
          )
        ),
      ),
      links = Map(
        "link" -> Link.Link(superclass="link",
          ports = Map(
            "source" -> Port.Port(superclass="sourcePort"),
            "sink" -> Port.Port(superclass="sinkPort"),
          )
        )
      ),
      constraints = Map(
        "sourceConnect" -> Constraint.Connected(Ref("source", "port"), Ref("link", "source")),
        "sinkConnect" -> Constraint.Connected(Ref("sink", "port"), Ref("link", "sink")),
      )
    ))
    val compiler = new Compiler(inputDesign, new wir.EdgirLibrary(library))
    compiler.compile should equal(referenceElaborated)
  }

  "Compiler on design with single nested source and sink" should "expand blocks" in {
    val inputDesign = Design(Block.Block(
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
    val referenceElaborated = Design(Block.Block(
      blocks = Map(
        "source" -> Block.Block(superclass="sourceContainerBlock",
          ports = Map(
            "port" -> Port.Port(superclass="sourcePort"),
          ),
          blocks = Map(
            "inner" -> Block.Block(superclass="sourceBlock",
              ports = Map(
                "port" -> Port.Port(superclass="sourcePort"),
              )
            )
          ),
          constraints = Map(
            "export" -> Constraint.Exported(Ref("port"), Ref("inner", "port"))
          )
        ),
        "sink" -> Block.Block(superclass="sinkContainerBlock",
          ports = Map(
            "port" -> Port.Port(superclass="sinkPort"),
          ),
          blocks = Map(
            "inner" -> Block.Block(superclass="sinkBlock",
              ports = Map(
                "port" -> Port.Port(superclass="sinkPort"),
              )
            )
          ),
          constraints = Map(
            "export" -> Constraint.Exported(Ref("port"), Ref("inner", "port"))
          )
        ),
      ),
      links = Map(
        "link" -> Link.Link(superclass="link",
          ports = Map(
            "source" -> Port.Port(superclass="sourcePort"),
            "sink" -> Port.Port(superclass="sinkPort"),
          )
        )
      ),
      constraints = Map(
        "sourceConnect" -> Constraint.Connected(Ref("source", "port"), Ref("link", "source")),
        "sinkConnect" -> Constraint.Connected(Ref("sink", "port"), Ref("link", "sink")),
      )
    ))
    val compiler = new Compiler(inputDesign, new wir.EdgirLibrary(library))
    compiler.compile should equal(referenceElaborated)
  }
}
