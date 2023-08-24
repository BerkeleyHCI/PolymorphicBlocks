package edg

import edg.ElemBuilder.{Block, Constraint, Link, Port, LibraryPath}
import edg.ExprBuilder.{Ref, ValInit}
import org.scalatest.flatspec.AnyFlatSpec
import org.scalatest.matchers.should.Matchers._

import scala.collection.SeqMap

class ConnectBuilderTest extends AnyFlatSpec {
  behavior.of("ConnectBuilder")

  val exampleBlock = Block.Block( // basic skeletal and structural example of a block with various connects
    "topDesign",
    ports = SeqMap(
      "port" -> Port.Port("sourcePort", params = SeqMap("param" -> ValInit.Integer)),
    ),
    blocks = SeqMap(
      "source" -> Block.Block(
        "sourceBlock",
        ports = SeqMap(
          "port" -> Port.Port("sourcePort", params = SeqMap("param" -> ValInit.Integer)),
        ),
      ),
      "sink0" -> Block.Block(
        "sinkBlock",
        ports = SeqMap(
          "port" -> Port.Port("sinkPort", params = SeqMap("param" -> ValInit.Integer)),
        ),
      ),
      "exportSource" -> Block.Block(
        "sourceBlock",
        ports = SeqMap(
          "port" -> Port.Port("sourcePort", params = SeqMap("param" -> ValInit.Integer)),
        ),
      ),
    ),
    links = SeqMap(
      "link" -> Link.Array("link"),
    ),
    constraints = SeqMap(
      "sourceConnect" -> Constraint.Connected(Ref("source", "port"), Ref("link", "source")),
      "sink0Connect" -> Constraint.Connected(Ref("sink0", "port"), Ref.Allocate(Ref("link", "sinks"))),
      "sourceExport" -> Constraint.Exported(Ref("port"), Ref("exportSource", "source")),
    )
  ).getHierarchy

  it should "decode connections and get types" in {

    // basic connection forms
    ConnectTypes.fromConnect(Constraint.Connected(Ref("source", "port"), Ref("link", "source"))) should equal(Some(Seq(
      ConnectTypes.BlockPort("source", "port")
    )))
    ConnectTypes.BlockPort("source", "port").getPortType(exampleBlock) should equal(Some(LibraryPath("sourcePort")))

    ConnectTypes.fromConnect(
      Constraint.Connected(Ref("sink0", "port"), Ref.Allocate(Ref("link", "sinks")))
    ) should equal(Some(Seq(
      ConnectTypes.BlockPort("sink0", "port")
    )))
    ConnectTypes.BlockPort("sink0", "port").getPortType(exampleBlock) should equal(Some(LibraryPath("sinkPort")))

    ConnectTypes.fromConnect(Constraint.Exported(Ref("port"), Ref("exportSource", "port"))) should equal(Some(Seq(
      ConnectTypes.BoundaryPort("port", Seq()),
      ConnectTypes.BlockPort("exportSource", "port")
    )))
    ConnectTypes.BoundaryPort("port", Seq()).getPortType(exampleBlock) should equal(Some(LibraryPath("sourcePort")))
    ConnectTypes.BlockPort("exportSource", "port").getPortType(exampleBlock) should equal(
      Some(LibraryPath("sourcePort"))
    )

    // export into bundle component / vector element
    ConnectTypes.fromConnect(Constraint.Exported(Ref("source", "a"), Ref("a", "source"))) should equal(Some(Seq(
      ConnectTypes.BoundaryPort("source", Seq("a")),
      ConnectTypes.BlockPort("a", "source")
    )))
  }
}
