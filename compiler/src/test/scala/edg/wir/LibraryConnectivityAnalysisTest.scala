package edg.wir

import org.scalatest._
import org.scalatest.flatspec.AnyFlatSpec
import matchers.should.Matchers._
import edg.ElemBuilder._
import edg.ExprBuilder.Ref


/** Tests compiler Bundle expansion / elaboration, including nested links.
  */
class LibraryConnectivityAnalysisTest extends AnyFlatSpec {
  private val library = Library(
    ports = Map(
      "innerSource" -> Port.Port(),
      "innerSink" -> Port.Port(),
      "outerPort" -> Port.Bundle(
        ports = Map(
          "inner" -> Port.Library("innerPort"),
        )
      ),
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
      "sourceAdapter" -> Block.Block(
        superclass=LibraryConnectivityAnalysis.portBridge.getTarget.getName,
        ports = Map(
          LibraryConnectivityAnalysis.portBridgeLinkPort -> Port.Library("sourcePort"),
          LibraryConnectivityAnalysis.portBridgeOuterPort -> Port.Library("sinkPort"),
        )
      ),
      "sinkAdapter" -> Block.Block(
        superclass=LibraryConnectivityAnalysis.portBridge.getTarget.getName,
        ports = Map(
          LibraryConnectivityAnalysis.portBridgeLinkPort -> Port.Library("sinkPort"),
          LibraryConnectivityAnalysis.portBridgeOuterPort -> Port.Library("sourcePort"),
        )
      ),
    ),
  )

  private val analysis = new LibraryConnectivityAnalysis(new EdgirLibrary(library))

  behavior of "LibraryConnectivityAnalysis"
  it should "return links from ports" in {
    analysis.linkOfPort(LibraryPath("innerSource")) should equal(Some(LibraryPath("innerLink")))
    analysis.linkOfPort(LibraryPath("innerSink")) should equal(Some(LibraryPath("innerLink")))
    analysis.linkOfPort(LibraryPath("outerPort")) should equal(Some(LibraryPath("outerLink")))
    analysis.linkOfPort(LibraryPath("lol")) should equal(None)
  }

  it should "return connectable ports of links" in {
    analysis.connectablePorts(LibraryPath("innerLink")) should equal(
      Map(LibraryPath("innerSource") -> 1, LibraryPath("innerSink") -> Integer.MAX_VALUE))
    analysis.connectablePorts(LibraryPath("outerLink")) should equal(
      Map(LibraryPath("outerPort") -> 2))
    analysis.connectablePorts(LibraryPath("lol")) should equal(Map())
  }

  it should "return port bridges" in {
    analysis.bridgedPortByOuter(LibraryPath("sinkPort")) should equal(Some(LibraryPath("sourcePort")))
    analysis.bridgedPortByOuter(LibraryPath("sourcePort")) should equal(Some(LibraryPath("sinkPort")))
    analysis.bridgedPortByOuter(LibraryPath("outerPort")) should equal(None)

    analysis.bridgeByOuter(LibraryPath("sinkPort")) should equal(Some(LibraryPath("sourceAdapter")))
    analysis.bridgeByOuter(LibraryPath("sourcePort")) should equal(Some(LibraryPath("sinkAdapter")))
    analysis.bridgeByOuter(LibraryPath("outerPort")) should equal(None)
  }
}
