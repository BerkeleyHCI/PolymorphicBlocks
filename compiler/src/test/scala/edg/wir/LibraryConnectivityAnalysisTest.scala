package edg.wir

import org.scalatest._
import org.scalatest.flatspec.AnyFlatSpec
import matchers.should.Matchers._
import edg.ElemBuilder._


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
          "outerPort" -> Port.Library("outerPort"),
        ),
        links = Map(
          "inner" -> Link.Library("innerLink"),
        ),
        // practically invalid, missing connect constraints
      ),
    )
  )

  private val analysis = new LibraryConnectivityAnalysis(new EdgirLibrary(library))

  behavior of "LibraryConnectivityAnalysis"
  it should "return links from ports" in {
    analysis.linkOfPort(LibraryPath("innerSource")) should equal(Some(LibraryPath("innerLink")))
    analysis.linkOfPort(LibraryPath("innerSink")) should equal(Some(LibraryPath("innerLink")))
    analysis.linkOfPort(LibraryPath("outerPort")) should equal(Some(LibraryPath("outerLink")))
    analysis.linkOfPort(LibraryPath("lol")) should equal(None)
  }
}