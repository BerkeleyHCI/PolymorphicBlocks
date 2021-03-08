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
      "innerLink" -> Link.Link(
        ports = Map(
          "innerSource" -> Port.Library("innerSource"),
          "innerSinks" -> Port.Array("innerSink")
        ),
        // practically invalid, missing connect constraints
      ),
      "outerLink" -> Link.Link(
        ports = Map(
          "outerPort1" -> Port.Library("outerPort"),
          "outerPort2" -> Port.Library("outerPort"),
        ),
        links = Map(
          "inner" -> Link.Library("innerLink"),
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
    ),
  )

  it should "get connected for direct exports" in {
    val inputDesign = Design(Block.Block(
      blocks = Map("dut" -> Block.Library("exportSinkBlock"))
    ))
    val compiled = new Compiler(inputDesign, new wir.EdgirLibrary(library)).compile()

    val dutPath = DesignPath() + "dut"

    val analysis = new BlockConnectivityAnalysis(dutPath,
      compiled.getContents.blocks("dut").getHierarchy)
    analysis.getConnected(Ref("port")) should equal(
      Some(Connection.Export(dutPath, "export", Ref("port"), Ref("inner", "port")))
    )
  }
}
