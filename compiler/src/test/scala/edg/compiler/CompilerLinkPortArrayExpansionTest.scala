package edg.compiler

import org.scalatest._
import org.scalatest.flatspec.AnyFlatSpec
import matchers.should.Matchers._
import edg.ElemBuilder._
import edg.ExprBuilder.{Ref, ValueExpr}
import edg.wir.ProtoUtil._
import edg.{CompilerTestUtil, wir}

import scala.collection.SeqMap

/** Tests compiler PortArray expansion / elaboration and connected constraint allocation with link-side PortArray only.
  * Not dependent on generators or parameter propagation.
  */
class CompilerLinkPortArrayExpansionTest extends AnyFlatSpec with CompilerTestUtil {
  val library = Library(
    ports = Seq(
      Port.Port("sourcePort"),
      Port.Port("sinkPort"),
      Port.Bundle(
        "outerSourcePort",
        ports = SeqMap(
          "a" -> Port.Library("sourcePort"),
          "b" -> Port.Library("sourcePort"),
        )
      ),
      Port.Bundle(
        "outerSinkPort",
        ports = SeqMap(
          "a" -> Port.Library("sinkPort"),
          "b" -> Port.Library("sinkPort"),
        )
      ),
    ),
    blocks = Seq(
      Block.Block(
        "sourceBlock",
        ports = SeqMap(
          "port" -> Port.Library("sourcePort"),
        )
      ),
      Block.Block(
        "sinkBlock",
        ports = SeqMap(
          "port" -> Port.Library("sinkPort"),
        )
      ),
      Block.Block(
        "outerSourceBlock",
        ports = SeqMap(
          "port" -> Port.Library("outerSourcePort"),
        ),
        blocks = SeqMap(
          "inner" -> Block.Library("sourceBlock"),
        ),
        constraints = SeqMap(
          "export" -> Constraint.Exported(Ref("port"), Ref("inner", "port"))
        )
      ),
      Block.Block(
        "outerSinkBlock",
        ports = SeqMap(
          "port" -> Port.Library("outerSinkPort"),
        ),
        blocks = SeqMap(
          "inner" -> Block.Library("sourceBlock"),
        ),
        constraints = SeqMap(
          "export" -> Constraint.Exported(Ref("port"), Ref("inner", "port"))
        )
      ),
    ),
    links = Seq(
      Link.Link(
        "link",
        ports = SeqMap(
          "source" -> Port.Library("sourcePort"),
          "sinks" -> Port.Array("sinkPort"),
        )
      ),
      Link.Link(
        "outerLink",
        ports = SeqMap(
          "source" -> Port.Library("outerSourcePort"),
          "sinks" -> Port.Array("outerSinkPort"),
        ),
        links = SeqMap(
          "a" -> Link.Library("link"),
          "b" -> Link.Library("link"),
        ),
        constraints = SeqMap(
          "sourceAExport" -> Constraint.Exported(Ref("source", "a"), Ref("a", "source")),
          "sourceBExport" -> Constraint.Exported(Ref("source", "b"), Ref("b", "source")),
          "sinkAExport" -> Constraint.ExportedArray(
            ValueExpr.MapExtract(Ref("sinks"), "a"),
            Ref.Allocate(Ref("a", "sinks"))
          ),
          "sinkBExport" -> Constraint.ExportedArray(
            ValueExpr.MapExtract(Ref("sinks"), "b"),
            Ref.Allocate(Ref("b", "sinks"))
          ),
        )
      ),
    )
  )

  "Compiler on design with source and array sink" should "expand blocks" in {
    val inputDesign = Design(Block.Block(
      "topDesign",
      blocks = SeqMap(
        "source" -> Block.Library("sourceBlock"),
        "sink0" -> Block.Library("sinkBlock"),
        "sink1" -> Block.Library("sinkBlock"),
        "sink2" -> Block.Library("sinkBlock"),
      ),
      links = SeqMap(
        "link" -> Link.Library("link")
      ),
      constraints = SeqMap(
        "sourceConnect" -> Constraint.Connected(Ref("source", "port"), Ref("link", "source")),
        "sink0Connect" -> Constraint.Connected(Ref("sink0", "port"), Ref.Allocate(Ref("link", "sinks"))),
        "sink1Connect" -> Constraint.Connected(Ref("sink1", "port"), Ref.Allocate(Ref("link", "sinks"))),
        "sink2Connect" -> Constraint.Connected(Ref("sink2", "port"), Ref.Allocate(Ref("link", "sinks"))),
      )
    ))
    val referenceElaborated = Design(Block.Block(
      "topDesign",
      blocks = SeqMap(
        "source" -> Block.Block(
          selfClass = "sourceBlock",
          ports = SeqMap(
            "port" -> Port.Port(selfClass = "sourcePort"),
          )
        ),
        "sink0" -> Block.Block(
          selfClass = "sinkBlock",
          ports = SeqMap(
            "port" -> Port.Port(selfClass = "sinkPort"),
          )
        ),
        "sink1" -> Block.Block(
          selfClass = "sinkBlock",
          ports = SeqMap(
            "port" -> Port.Port(selfClass = "sinkPort"),
          )
        ),
        "sink2" -> Block.Block(
          selfClass = "sinkBlock",
          ports = SeqMap(
            "port" -> Port.Port(selfClass = "sinkPort"),
          )
        ),
      ),
      links = SeqMap(
        "link" -> Link.Link(
          selfClass = "link",
          ports = SeqMap(
            "source" -> Port.Port(selfClass = "sourcePort"),
            "sinks" -> Port.Array(selfClass = "sinkPort", Seq("0", "1", "2"), Port.Port(selfClass = "sinkPort")),
          )
        )
      ),
      constraints = SeqMap(
        "sourceConnect" -> Constraint.Connected(Ref("source", "port"), Ref("link", "source")),
        "sink0Connect" -> Constraint.Connected(Ref("sink0", "port"), Ref("link", "sinks", "0")),
        "sink1Connect" -> Constraint.Connected(Ref("sink1", "port"), Ref("link", "sinks", "1")),
        "sink2Connect" -> Constraint.Connected(Ref("sink2", "port"), Ref("link", "sinks", "2")),
      )
    ))
    val (compiler, compiled) = testCompile(inputDesign, library)

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

  "Compiler on design with source and array sink" should "support empty arrays" in {
    val inputDesign = Design(Block.Block(
      "topDesign",
      blocks = SeqMap(
        "source" -> Block.Library("sourceBlock"),
      ),
      links = SeqMap(
        "link" -> Link.Library("link")
      ),
      constraints = SeqMap(
        "sourceConnect" -> Constraint.Connected(Ref("source", "port"), Ref("link", "source")),
      )
    ))
    val referenceElaborated = Design(Block.Block(
      "topDesign",
      blocks = SeqMap(
        "source" -> Block.Block(
          selfClass = "sourceBlock",
          ports = SeqMap(
            "port" -> Port.Port(selfClass = "sourcePort"),
          )
        ),
      ),
      links = SeqMap(
        "link" -> Link.Link(
          selfClass = "link",
          ports = SeqMap(
            "source" -> Port.Port(selfClass = "sourcePort"),
            "sinks" -> Port.Array(selfClass = "sinkPort", Seq(), Port.Port(selfClass = "sinkPort")),
          )
        )
      ),
      constraints = SeqMap(
        "sourceConnect" -> Constraint.Connected(Ref("source", "port"), Ref("link", "source")),
      )
    ))
    testCompile(inputDesign, library, expectedDesign = Some(referenceElaborated))
  }

  "Compiler on design with bundle source and array bundle sink" should "expand link connections" in {
    val inputDesign = Design(Block.Block(
      "topDesign",
      blocks = SeqMap(
        "source" -> Block.Library("outerSourceBlock"),
        "sink0" -> Block.Library("outerSinkBlock"),
        "sink1" -> Block.Library("outerSinkBlock"),
        "sink2" -> Block.Library("outerSinkBlock"),
      ),
      links = SeqMap(
        "link" -> Link.Library("outerLink")
      ),
      constraints = SeqMap(
        "sourceConnect" -> Constraint.Connected(Ref("source", "port"), Ref("link", "source")),
        "sink0Connect" -> Constraint.Connected(Ref("sink0", "port"), Ref.Allocate(Ref("link", "sinks"))),
        "sink1Connect" -> Constraint.Connected(Ref("sink1", "port"), Ref.Allocate(Ref("link", "sinks"))),
        "sink2Connect" -> Constraint.Connected(Ref("sink2", "port"), Ref.Allocate(Ref("link", "sinks"))),
      )
    ))

    val expectedLinkConstraints = SeqMap(
      "sourceAExport" -> Constraint.Exported(Ref("source", "a"), Ref("a", "source")),
      "sourceBExport" -> Constraint.Exported(Ref("source", "b"), Ref("b", "source")),
      "sinkAExport.0" -> Constraint.Exported(Ref("sinks", "0", "a"), Ref("a", "sinks", "0_0")),
      "sinkAExport.1" -> Constraint.Exported(Ref("sinks", "1", "a"), Ref("a", "sinks", "0_1")),
      "sinkAExport.2" -> Constraint.Exported(Ref("sinks", "2", "a"), Ref("a", "sinks", "0_2")),
      "sinkBExport.0" -> Constraint.Exported(Ref("sinks", "0", "b"), Ref("b", "sinks", "0_0")),
      "sinkBExport.1" -> Constraint.Exported(Ref("sinks", "1", "b"), Ref("b", "sinks", "0_1")),
      "sinkBExport.2" -> Constraint.Exported(Ref("sinks", "2", "b"), Ref("b", "sinks", "0_2")),
    )

    val (compiler, compiled) = testCompile(inputDesign, library)

    compiled.contents.get.links("link").getLink.constraints.toSeqMap should equal(expectedLinkConstraints)
  }
}
