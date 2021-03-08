package edg.wir

import org.scalatest._
import org.scalatest.flatspec.AnyFlatSpec
import matchers.should.Matchers._
import edg.ElemBuilder._
import edg.ExprBuilder.Ref
import edg.compiler.Compiler
import edg.wir


/** Tests compiler Bundle expansion / elaboration, including nested links.
  */
class BlockConnectivityAnalysisTest extends AnyFlatSpec {
  private val library = Library(
    ports = Map(
      "sourcePort" -> Port.Port(),
      "sinkPort" -> Port.Port(),
    ),
    links = Map(
      "link" -> Link.Link(
        ports = Map(
          "source" -> Port.Library("source"),
          "sinks" -> Port.Array("sink")
        ),
        // practically invalid, missing connect constraints
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
      "sourceFromExtSinkBridge" -> Block.Block(
        superclass=LibraryConnectivityAnalysis.portBridge.getTarget.getName,
        ports = Map(
          LibraryConnectivityAnalysis.portBridgeLinkPort -> Port.Library("sourcePort"),
          LibraryConnectivityAnalysis.portBridgeOuterPort -> Port.Library("sinkPort"),
        )
      ),
      "sinkFromExtSourceBridge" -> Block.Block(
        superclass=LibraryConnectivityAnalysis.portBridge.getTarget.getName,
        ports = Map(
          LibraryConnectivityAnalysis.portBridgeLinkPort -> Port.Library("sinkPort"),
          LibraryConnectivityAnalysis.portBridgeOuterPort -> Port.Library("sourcePort"),
        )
      ),

      "exportSinkBlock" -> Block.Block(
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
      "bridgedSinkBlock" -> Block.Block(
        ports = Map(
          "port" -> Port.Library("sinkPort"),
        ),
        blocks = Map(
          "bridge" -> Block.Library("sourceFromExtSinkBridge"),
          "sink1Block" -> Block.Library("sinkBlock"),
          "sink2Block" -> Block.Library("sinkBlock"),
        ),
        links = Map(
          "link" -> Link.Library("link")
        ),
        constraints = Map(
          "export" -> Constraint.Exported(Ref("port"), Ref("bridge", LibraryConnectivityAnalysis.portBridgeOuterPort)),
          "sourceConnect" -> Constraint.Connected(Ref("bridge", LibraryConnectivityAnalysis.portBridgeLinkPort), Ref("link", "source")),
          "sink1Connect" -> Constraint.Connected(Ref("sink1Block", "port"), Ref.Allocate(Ref("link", "sinks"))),
          "sink2Connect" -> Constraint.Connected(Ref("sink2Block", "port"), Ref.Allocate(Ref("link", "sinks"))),
        )
      )
    ),
  )

  it should "get connected for direct exports" in {
    val inputDesign = Design(Block.Block(
      blocks = Map(
        "dut" -> Block.Library("exportSinkBlock")
      )
    ))
    val compiled = new Compiler(inputDesign, new wir.EdgirLibrary(library)).compile()
    val dutPath = DesignPath() + "dut"
    val analysis = new BlockConnectivityAnalysis(dutPath,
      compiled.getContents.blocks("dut").getHierarchy)

    analysis.getConnected(Ref("port")) should equal(
      Some(Connection.Export(dutPath, "export", Ref("port"), Ref("inner", "port")))
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
      blocks = Map(
        "sourceBlock" -> Block.Library("sourceBlock"),
        "sink1Block" -> Block.Library("sinkBlock"),
        "sink2Block" -> Block.Library("sinkBlock"),
      ),
      links = Map(
        "link" -> Link.Library("link")
      ),
      constraints = Map(
        "sourceConnect" -> Constraint.Connected(Ref("sourceBlock", "port"), Ref("link", "source")),
        "sink1Connect" -> Constraint.Connected(Ref("sink1Block", "port"), Ref.Allocate(Ref("link", "sinks"))),
        "sink2Connect" -> Constraint.Connected(Ref("sink2Block", "port"), Ref.Allocate(Ref("link", "sinks"))),
      )
    ))
    val compiled = new Compiler(inputDesign, new wir.EdgirLibrary(library)).compile()
    val dutPath = DesignPath()
    val analysis = new BlockConnectivityAnalysis(dutPath, compiled.getContents)

    val expectedConnects = Connection.Link(
      dutPath, "link",
      Seq(
        (Ref("sourceBlock", "port"), "sourceConnect"),
        (Ref("sink1Block", "port"), "sink1Connect"),
        (Ref("sink2Block", "port"), "sink2Connect"),
      ),
      Seq()
    )

    analysis.getConnected(Ref("sourceBlock", "port")) should equal(Some(expectedConnects))
    analysis.getConnected(Ref("sink1Block", "port")) should equal(Some(expectedConnects))
    analysis.getConnected(Ref("sink2Block", "port")) should equal(Some(expectedConnects))

    analysis.getAllConnectedInternalPorts should equal(
      Seq(Ref("sourceBlock", "port"), Ref("sink1Block", "port"), Ref("sink2Block", "port"))
    )
  }

  it should "get connected for mixed link and exports" in {
    val inputDesign = Design(Block.Block(
      blocks = Map(
        "dut" -> Block.Library("bridgedSinkBlock")
      )
    ))
    val compiled = new Compiler(inputDesign, new wir.EdgirLibrary(library)).compile()
    val dutPath = DesignPath() + "dut"
    val analysis = new BlockConnectivityAnalysis(dutPath,
      compiled.getContents.blocks("dut").getHierarchy)

    val expectedConnects = Connection.Link(
      dutPath, "link",
      Seq(
        (Ref("bridge", LibraryConnectivityAnalysis.portBridgeLinkPort), "sourceConnect"),
        (Ref("sink1Block", "port"), "sink1Connect"),
        (Ref("sink2Block", "port"), "sink2Connect"),
      ),
      Seq(
        (Ref("port"), "bridge", "export")
      )
    )

    analysis.getConnected(Ref("sink1Block", "port")) should equal(Some(expectedConnects))
    analysis.getConnected(Ref("sink2Block", "port")) should equal(Some(expectedConnects))
    analysis.getConnected(Ref("port")) should equal(Some(expectedConnects))
    analysis.getConnected(Ref("bridge", LibraryConnectivityAnalysis.portBridgeLinkPort)) should equal(Some(expectedConnects))
    analysis.getConnected(Ref("bridge", LibraryConnectivityAnalysis.portBridgeOuterPort)) should equal(Some(expectedConnects))

    analysis.getAllConnectedInternalPorts.toSet should equal(
      Set(Ref("bridge", LibraryConnectivityAnalysis.portBridgeLinkPort),
        Ref("bridge", LibraryConnectivityAnalysis.portBridgeOuterPort),
        Ref("sink1Block", "port"), Ref("sink2Block", "port"))
    )
    analysis.getAllConnectedExternalPorts should equal(
      Seq(Ref("port"))
    )
  }
}
