package edg.compiler

import org.scalatest._
import org.scalatest.flatspec.AnyFlatSpec
import matchers.should.Matchers._
import edg.ElemBuilder._
import edg.ExprBuilder.Ref
import edg.wir

class CompilerBlockExpansionTest extends AnyFlatSpec {
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
          "sink" -> Port.Library("sinkPort"),
        )
      ),
    )
  )

  "Compiler on design with " should "expand blocks" in {
    val inputDesign = Design(Block.Block(
      blocks = Map(
        "source" -> Block.Library("sourceBlock"),
        "sink" -> Block.Library("sinkBlock"),
      ),
      links = Map(
        "link" -> Link.Library("link")
      ),
      constraints = Map(
        "sourceConnect" -> Constraint.Connected(Ref("source", "port"), Ref("link", "sourcePort")),
        "sourceConnect" -> Constraint.Connected(Ref("sink", "port"), Ref("link", "sinkPort")),
      )
    ))
    val referenceElaborated = Design(Block.Block(
      blocks = Map(
        "source" -> Block.Block(
          ports = Map(
            "port" -> Port.Port(superclass="sourcePort"),
          ),
          superclass="sourceBlock"
        ),
        "sink" -> Block.Block(
          ports = Map(
            "port" -> Port.Port(superclass="sinkPort"),
          ),
          superclass="sinkBlock"
        ),
      ),
      links = Map(
        "link" -> Link.Link(
          ports = Map(
            "source" -> Port.Port(superclass="sourcePort"),
            "sink" -> Port.Port(superclass="sinkPort"),
          ),
          superclass="link"
        )
      ),
      constraints = Map(
        "sourceConnect" -> Constraint.Connected(Ref("source", "port"), Ref("link", "sourcePort")),
        "sourceConnect" -> Constraint.Connected(Ref("sink", "port"), Ref("link", "sinkPort")),
      )
    ))
    val compiler = new Compiler(inputDesign, new wir.Library(library))
    compiler.compile should equal(referenceElaborated)
  }
}
