package edg.wir

import org.scalatest._
import org.scalatest.flatspec.AnyFlatSpec
import matchers.should.Matchers._
import edg.ElemBuilder._
import edg.ExprBuilder.Ref
import edg.compiler.Compiler
import edg.wir.ProtoUtil.BlockProtoToSeqMap
import edg.{CompilerTestUtil, wir}

import scala.collection.SeqMap

class BlockConnectivityAnalysisTest extends AnyFlatSpec with CompilerTestUtil {
  private val library = Library(
    ports = Seq(
      Port.Port("sourcePort"),
      Port.Port("sinkPort"),
    ),
    links = Seq(
      Link.Link(
        "link",
        ports = SeqMap(
          "source" -> Port.Library("sourcePort"),
          "sinks" -> Port.Array("sinkPort")
        ),
        // practically invalid, missing connect constraints
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
        "sourceFromExtSinkBridge",
        superclasses = Seq(LibraryConnectivityAnalysis.portBridge.getTarget.getName),
        ports = SeqMap(
          LibraryConnectivityAnalysis.portBridgeLinkPort -> Port.Library("sourcePort"),
          LibraryConnectivityAnalysis.portBridgeOuterPort -> Port.Library("sinkPort"),
        )
      ),
      Block.Block(
        "sinkFromExtSourceBridge",
        superclasses = Seq(LibraryConnectivityAnalysis.portBridge.getTarget.getName),
        ports = SeqMap(
          LibraryConnectivityAnalysis.portBridgeLinkPort -> Port.Library("sinkPort"),
          LibraryConnectivityAnalysis.portBridgeOuterPort -> Port.Library("sourcePort"),
        )
      ),
      Block.Block(
        "exportSinkBlock",
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
      Block.Block(
        "bridgedSinkBlock",
        ports = SeqMap(
          "port" -> Port.Library("sinkPort"),
        ),
        blocks = SeqMap(
          "bridge" -> Block.Library("sourceFromExtSinkBridge"),
          "sink1Block" -> Block.Library("sinkBlock"),
          "sink2Block" -> Block.Library("sinkBlock"),
        ),
        links = SeqMap(
          "link" -> Link.Library("link")
        ),
        constraints = SeqMap(
          "export" -> Constraint.Exported(Ref("port"), Ref("bridge", LibraryConnectivityAnalysis.portBridgeOuterPort)),
          "sourceConnect" -> Constraint.Connected(
            Ref("bridge", LibraryConnectivityAnalysis.portBridgeLinkPort),
            Ref("link", "source")
          ),
          "sink1Connect" -> Constraint.Connected(Ref("sink1Block", "port"), Ref.Allocate(Ref("link", "sinks"))),
          "sink2Connect" -> Constraint.Connected(Ref("sink2Block", "port"), Ref.Allocate(Ref("link", "sinks"))),
        )
      )
    ),
  )

  it should "get connected for direct exports" in {
    val inputDesign = Design(Block.Block(
      "topDesign",
      blocks = SeqMap(
        "dut" -> Block.Library("exportSinkBlock")
      )
    ))
    val (compiler, compiled) = testCompile(inputDesign, library)
    val analysis = new BlockConnectivityAnalysis(compiled.getContents.blocks("dut").getHierarchy)

    analysis.getConnected(Ref("port")) should equal(
      Connection.Export("export", Ref("port"), Ref("inner", "port"))
    )

    analysis.getAllConnectedInternalPorts should equal(
      Seq(Ref("inner", "port"))
    )
    analysis.getAllConnectedExternalPorts should equal(
      Seq(Ref("port"))
    )
  }

  it should "get connected for links only" in {
    val inputDesign = Design(Block.Block(
      "topDesign",
      blocks = SeqMap(
        "sourceBlock" -> Block.Library("sourceBlock"),
        "sink1Block" -> Block.Library("sinkBlock"),
        "sink2Block" -> Block.Library("sinkBlock"),
      ),
      links = SeqMap(
        "link" -> Link.Library("link")
      ),
      constraints = SeqMap(
        "sourceConnect" -> Constraint.Connected(Ref("sourceBlock", "port"), Ref("link", "source")),
        "sink1Connect" -> Constraint.Connected(Ref("sink1Block", "port"), Ref.Allocate(Ref("link", "sinks"))),
        "sink2Connect" -> Constraint.Connected(Ref("sink2Block", "port"), Ref.Allocate(Ref("link", "sinks"))),
      )
    ))
    val (compiler, compiled) = testCompile(inputDesign, library)
    val analysis = new BlockConnectivityAnalysis(compiled.getContents)

    val expectedConnects = Connection.Link(
      "link",
      Seq(
        (Ref("sourceBlock", "port"), "sourceConnect"),
        (Ref("sink1Block", "port"), "sink1Connect"),
        (Ref("sink2Block", "port"), "sink2Connect"),
      ),
      Seq()
    )

    analysis.getConnected(Ref("sourceBlock", "port")) should equal(expectedConnects)
    analysis.getConnected(Ref("sink1Block", "port")) should equal(expectedConnects)
    analysis.getConnected(Ref("sink2Block", "port")) should equal(expectedConnects)

    analysis.getAllConnectedInternalPorts should equal(
      Seq(Ref("sourceBlock", "port"), Ref("sink1Block", "port"), Ref("sink2Block", "port"))
    )
  }

  it should "get connected for mixed link and exports" in {
    val inputDesign = Design(Block.Block(
      "topDesign",
      blocks = SeqMap(
        "dut" -> Block.Library("bridgedSinkBlock")
      )
    ))
    val (compiler, compiled) = testCompile(inputDesign, library)
    val analysis = new BlockConnectivityAnalysis(compiled.getContents.blocks("dut").getHierarchy)

    val expectedConnects = Connection.Link(
      "link",
      Seq(
        (Ref("bridge", LibraryConnectivityAnalysis.portBridgeLinkPort), "sourceConnect"),
        (Ref("sink1Block", "port"), "sink1Connect"),
        (Ref("sink2Block", "port"), "sink2Connect"),
      ),
      Seq(
        (Ref("port"), "bridge", "export")
      )
    )

    analysis.getConnected(Ref("sink1Block", "port")) should equal(expectedConnects)
    analysis.getConnected(Ref("sink2Block", "port")) should equal(expectedConnects)
    analysis.getConnected(Ref("port")) should equal(expectedConnects)
    analysis.getConnected(Ref("bridge", LibraryConnectivityAnalysis.portBridgeLinkPort)) should equal(expectedConnects)
    analysis.getConnected(Ref("bridge", LibraryConnectivityAnalysis.portBridgeOuterPort)) should equal(expectedConnects)

    analysis.getAllConnectedInternalPorts.toSet should equal(
      Set(
        Ref("bridge", LibraryConnectivityAnalysis.portBridgeLinkPort),
        Ref("bridge", LibraryConnectivityAnalysis.portBridgeOuterPort),
        Ref("sink1Block", "port"),
        Ref("sink2Block", "port")
      )
    )
    analysis.getAllConnectedExternalPorts should equal(
      Seq(Ref("port"))
    )

    analysis.allConnectablePortTypes should equal(
      analysis.ConnectablePorts(
        innerPortTypes = Set(
          (Ref("sink1Block", "port"), LibraryPath("sinkPort")),
          (Ref("sink2Block", "port"), LibraryPath("sinkPort")),
          (Ref("bridge", LibraryConnectivityAnalysis.portBridgeLinkPort), LibraryPath("sourcePort")),
          (Ref("bridge", LibraryConnectivityAnalysis.portBridgeOuterPort), LibraryPath("sinkPort")),
        ),
        exteriorPortTypes = Set(
          (Ref("port"), LibraryPath("sinkPort")),
        )
      )
    )
  }
}
