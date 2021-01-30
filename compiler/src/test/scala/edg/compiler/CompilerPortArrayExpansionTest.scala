package edg.compiler

import org.scalatest._
import org.scalatest.flatspec.AnyFlatSpec
import matchers.should.Matchers._
import edg.ElemBuilder._
import edg.ExprBuilder.{Ref, ValueExpr}
import edg.wir


/** Tests compiler PortArray expansion / elaboration and connected constraint allocation with link-side PortArray only.
  * Not dependent on generators or parameter propagation.
  */
class CompilerPortArrayExpansionTest extends AnyFlatSpec {
  val library = Library(
    ports = Map(
      "sourcePort" -> Port.Port(),
      "sinkPort" -> Port.Port(),
      "outerSourcePort" -> Port.Bundle(
        ports = Map(
          "a" -> Port.Library("sourcePort"),
          "b" -> Port.Library("sourcePort"),
        )
      ),
      "outerSinkPort" -> Port.Bundle(
        ports = Map(
          "a" -> Port.Library("sinkPort"),
          "b" -> Port.Library("sinkPort"),
        )
      ),
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
      "outerSourceBlock" -> Block.Block(
        ports = Map(
          "port" -> Port.Library("outerSourcePort"),
        ),
        blocks = Map(
          "inner" -> Block.Library("sourceBlock"),
        ),
        constraints = Map(
          "export" -> Constraint.Exported(Ref("port"), Ref("inner", "port"))
        )
      ),
      "outerSinkBlock" -> Block.Block(
        ports = Map(
          "port" -> Port.Library("outerSinkPort"),
        ),
        blocks = Map(
          "inner" -> Block.Library("sourceBlock"),
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
          "sinks" -> Port.Array("sinkPort"),
        )
      ),
      "outerLink" -> Link.Link(
        ports = Map(
          "source" -> Port.Library("outerSourcePort"),
          "sinks" -> Port.Array("outerSinkPort"),
        ),
        links = Map(
          "a" -> Link.Library("link"),
          "b" -> Link.Library("link"),
        ),
        constraints = Map(
          "sourceAExport" -> Constraint.Exported(Ref("source", "a"), Ref("a", "source")),
          "sourceBExport" -> Constraint.Exported(Ref("source", "b"), Ref("b", "source")),
          "sinkAExport" -> Constraint.Exported(ValueExpr.MapExtract(Ref("sinks"), "a"),
            Ref.Allocate(Ref("a", "sinks"))
          ),
          "sinkBExport" -> Constraint.Exported(ValueExpr.MapExtract(Ref("sinks"), "b"),
            Ref.Allocate(Ref("b", "sinks"))
          ),
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
    val compiler = new Compiler(inputDesign, new wir.EdgirLibrary(library))
    val compiled = compiler.compile()

    // Smaller comparisons to allow more targeted error messages
    val compiledBlock = compiled.getContents
    val referenceBlock = referenceElaborated.getContents
    compiledBlock.blocks("source") should equal(referenceBlock.blocks("source"))
    compiledBlock.blocks("sink0") should equal(referenceBlock.blocks("sink0"))
    compiledBlock.blocks("sink1") should equal(referenceBlock.blocks("sink1"))
    compiledBlock.blocks("sink2") should equal(referenceBlock.blocks("sink2"))
    compiledBlock.blocks should equal(referenceBlock.blocks)
    compiledBlock.links should equal(referenceBlock.links)
    compiledBlock.constraints("sourceConnect") should equal(referenceBlock.constraints("sourceConnect"))
    compiledBlock.constraints("sink0Connect") should equal(referenceBlock.constraints("sink0Connect"))
    compiledBlock.constraints("sink1Connect") should equal(referenceBlock.constraints("sink1Connect"))
    compiledBlock.constraints("sink2Connect") should equal(referenceBlock.constraints("sink2Connect"))

    compiledBlock.constraints should equal(referenceBlock.constraints)

    // The catch-all equivalence comparison
    compiled should equal(referenceElaborated)
  }

  "Compiler on design with bundle source and array bundle sink" should "expand link connections" in {
    val inputDesign = Design(Block.Block(
      blocks = Map(
        "source" -> Block.Library("outerSourceBlock"),
        "sink0" -> Block.Library("outerSinkBlock"),
        "sink1" -> Block.Library("outerSinkBlock"),
        "sink2" -> Block.Library("outerSinkBlock"),
      ),
      links = Map(
        "link" -> Link.Library("outerLink")
      ),
      constraints = Map(
        "sourceConnect" -> Constraint.Connected(Ref("source", "port"), Ref("link", "source")),
        "sink0Connect" -> Constraint.Connected(Ref("sink0", "port"), Ref.Allocate(Ref("link", "sinks"))),
        "sink1Connect" -> Constraint.Connected(Ref("sink1", "port"), Ref.Allocate(Ref("link", "sinks"))),
        "sink2Connect" -> Constraint.Connected(Ref("sink2", "port"), Ref.Allocate(Ref("link", "sinks"))),
      )
    ))

    val expectedLinkConstraints = Map(
      "sourceAExport" -> Constraint.Exported(Ref("source", "a"), Ref("a", "source")),
      "sourceBExport" -> Constraint.Exported(Ref("source", "b"), Ref("b", "source")),
      "sinkAExport.0" -> Constraint.Exported(Ref("sinks", "0", "a"), Ref("a", "sinks", "0")),
      "sinkAExport.1" -> Constraint.Exported(Ref("sinks", "1", "a"), Ref("a", "sinks", "1")),
      "sinkAExport.2" -> Constraint.Exported(Ref("sinks", "2", "a"), Ref("a", "sinks", "2")),
      "sinkBExport.0" -> Constraint.Exported(Ref("sinks", "0", "b"), Ref("b", "sinks", "0")),
      "sinkBExport.1" -> Constraint.Exported(Ref("sinks", "1", "b"), Ref("b", "sinks", "1")),
      "sinkBExport.2" -> Constraint.Exported(Ref("sinks", "2", "b"), Ref("b", "sinks", "2")),
    )

    val compiler = new Compiler(inputDesign, new wir.EdgirLibrary(library))
    val compiled = compiler.compile()

    compiled.contents.get.links("link").getLink.constraints should equal(expectedLinkConstraints)
  }
}
