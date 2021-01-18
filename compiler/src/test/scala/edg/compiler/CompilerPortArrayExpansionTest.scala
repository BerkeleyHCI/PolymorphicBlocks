package edg.compiler

import org.scalatest._
import org.scalatest.flatspec.AnyFlatSpec
import matchers.should.Matchers._
import edg.ElemBuilder._
import edg.ExprBuilder.Ref
import edg.wir


/** Tests compiler PortArray expansion / elaboration and connected constraint allocation with link-side PortArray only.
  * Not dependent on generators or parameter propagation.
  */
class CompilerPortArrayExpansionTest extends AnyFlatSpec {
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
    ),
    links = Map(
      "link" -> Link.Link(
        ports = Map(
          "source" -> Port.Library("sourcePort"),
          "sinks" -> Port.Array("sinkPort"),
        )
      ),
    )
  )

  "Compiler on design with source and array sink" should "expand blocks" in {
    val inputDesign = Design(Block.Block(
      blocks = Map(
        "source" -> Block.Library("sourceBlock"),
        "sink0" -> Block.Library("sinkBlock"),
        "sink1" -> Block.Library("sinkBlock"),
        "sink2" -> Block.Library("sinkBlock"),
      ),
      links = Map(
        "link" -> Link.Library("link")
      ),
      constraints = Map(
        "sourceConnect" -> Constraint.Connected(Ref("source", "port"), Ref("link", "source")),
        "sink0Connect" -> Constraint.Connected(Ref("sink0", "port"), Ref.Allocate(Ref("link", "sinks"))),
        "sink1Connect" -> Constraint.Connected(Ref("sink1", "port"), Ref.Allocate(Ref("link", "sinks"))),
        "sink2Connect" -> Constraint.Connected(Ref("sink2", "port"), Ref.Allocate(Ref("link", "sinks"))),
      )
    ))
    val referenceElaborated = Design(Block.Block(
      blocks = Map(
        "source" -> Block.Block(superclass="sourceBlock",
          ports = Map(
            "port" -> Port.Port(superclass="sourcePort"),
          )
        ),
        "sink0" -> Block.Block(superclass="sinkBlock",
          ports = Map(
            "port" -> Port.Port(superclass="sinkPort"),
          )
        ),
        "sink1" -> Block.Block(superclass="sinkBlock",
          ports = Map(
            "port" -> Port.Port(superclass="sinkPort"),
          )
        ),
        "sink2" -> Block.Block(superclass="sinkBlock",
          ports = Map(
            "port" -> Port.Port(superclass="sinkPort"),
          )
        ),
      ),
      links = Map(
        "link" -> Link.Link(superclass="link",
          ports = Map(
            "source" -> Port.Port(superclass="sourcePort"),
            "sinks" -> Port.Port(superclass="sinkPort"),
          )
        )
      ),
      constraints = Map(
        "sourceConnect" -> Constraint.Connected(Ref("source", "port"), Ref("link", "source")),
        "sink0Connect" -> Constraint.Connected(Ref("sink0", "port"), Ref("link", "sinks", "0")),
        "sink1Connect" -> Constraint.Connected(Ref("sink1", "port"), Ref("link", "sinks", "1")),
        "sink2Connect" -> Constraint.Connected(Ref("sink2", "port"), Ref("link", "sinks", "2")),
      )
    ))
    val compiler = new Compiler(inputDesign, new wir.Library(library))
    compiler.compile should equal(referenceElaborated)
  }
}