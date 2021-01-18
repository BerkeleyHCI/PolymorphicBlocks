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
            "sinks" -> Port.Array(superclass="sinkPort", 3, Port.Port(superclass="sinkPort")),
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
    val compiled = compiler.compile().contents.get

    // Smaller comparisons to allow more targeted error messages
    val compiledBlock = compiler.compile().contents.get
    val referenceBlock = referenceElaborated.contents.get
    compiledBlock.blocks("source") should equal(referenceBlock.blocks("source"))
    compiledBlock.blocks("sink0") should equal(referenceBlock.blocks("sink0"))
    compiledBlock.blocks("sink1") should equal(referenceBlock.blocks("sink1"))
    compiledBlock.blocks("sink2") should equal(referenceBlock.blocks("sink2"))
    compiledBlock.links should equal(referenceBlock.links)
    compiledBlock.constraints("sourceConnect") should equal(referenceBlock.constraints("sourceConnect"))
    compiledBlock.constraints("sink0Connect") should equal(referenceBlock.constraints("sink0Connect"))
    compiledBlock.constraints should equal(referenceBlock.constraints)

    // The catch-all equivalence comparison
    compiled should equal(referenceElaborated)
  }
}