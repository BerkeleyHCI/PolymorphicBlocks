package edg

import edg.ElemBuilder.{Block, Constraint, LibraryPath, Link, Port}
import edg.ExprBuilder.{Ref, ValInit}
import edg.wir.ProtoUtil.ConstraintProtoToSeqMap
import org.scalatest.flatspec.AnyFlatSpec
import org.scalatest.matchers.should.Matchers._

import scala.collection.SeqMap

class ConnectBuilderTest extends AnyFlatSpec {
  behavior.of("ConnectBuilder")

  val exampleBlock = Block.Block( // basic skeletal and structural example of a block with various connects
    "topDesign",
    ports = SeqMap(
      "port" -> Port.Port("sourcePort", params = SeqMap("param" -> ValInit.Integer)),
      "bundle" -> Port.Bundle(
        "sourceBundle",
        ports = SeqMap(
          "port" -> Port.Port("sourcePort", params = SeqMap("param" -> ValInit.Integer)),
        )
      ),
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
      "exportBundleSource" -> Block.Block(
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
      "sourceExport" -> Constraint.Exported(Ref("port"), Ref("exportSource", "port")),
      "bundleSourceExport" -> Constraint.Exported(Ref("bundle", "port"), Ref("exportBundleSource", "port")),
    )
  ).getHierarchy

  val exampleLink = Link.Link(
    "link",
    ports = SeqMap(
      "source" -> Port.Library("sourcePort"),
      "sinks" -> Port.Array("sinkPort"),
    ),
    params = SeqMap(
      "param" -> ValInit.Integer
    ),
  ).getLink

  it should "decode connections and get types" in {
    // basic connection forms
    ConnectTypes.fromConnect(exampleBlock.constraints.toSeqMap("sourceConnect")) should equal(Some(Seq(
      ConnectTypes.BlockPort("source", "port")
    )))
    ConnectTypes.BlockPort("source", "port").getPortType(exampleBlock) should equal(Some(LibraryPath("sourcePort")))

    ConnectTypes.fromConnect(exampleBlock.constraints.toSeqMap("sink0Connect")) should equal(Some(Seq(
      ConnectTypes.BlockPort("sink0", "port")
    )))
    ConnectTypes.BlockPort("sink0", "port").getPortType(exampleBlock) should equal(Some(LibraryPath("sinkPort")))

    ConnectTypes.fromConnect(exampleBlock.constraints.toSeqMap("sourceExport")) should equal(Some(Seq(
      ConnectTypes.BoundaryPort("port", Seq()),
      ConnectTypes.BlockPort("exportSource", "port")
    )))
    ConnectTypes.BoundaryPort("port", Seq()).getPortType(exampleBlock) should equal(Some(LibraryPath("sourcePort")))
    ConnectTypes.BlockPort("exportSource", "port").getPortType(exampleBlock) should equal(
      Some(LibraryPath("sourcePort"))
    )

    // export into bundle component / vector element
    ConnectTypes.fromConnect(exampleBlock.constraints.toSeqMap("bundleSourceExport")) should equal(Some(Seq(
      ConnectTypes.BoundaryPort("bundle", Seq("port")),
      ConnectTypes.BlockPort("exportBundleSource", "port")
    )))
    ConnectTypes.BoundaryPort("bundle", Seq("port")).getPortType(exampleBlock) should equal(
      Some(LibraryPath("sourcePort"))
    )
    ConnectTypes.BlockPort("exportBundleSource", "port").getPortType(exampleBlock) should equal(
      Some(LibraryPath("sourcePort"))
    )
  }
}
