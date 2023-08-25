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
      "sink1" -> Block.Block(
        "sinkBlock",
        ports = SeqMap(
          "port" -> Port.Port("sinkPort", params = SeqMap("param" -> ValInit.Integer)),
        ),
      ),
      "sinkArray" -> Block.Block(
        "sinkArrayBlock",
        ports = SeqMap(
          "port" -> Port.Array(
            "sinkPort",
            Seq("0"),
            Port.Port("sinkPort", params = SeqMap("param" -> ValInit.Integer))
          ),
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
      "link" -> Link.Link("link"),
    ),
    constraints = SeqMap(
      "sourceConnect" -> Constraint.Connected(Ref("source", "port"), Ref("link", "source")),
      "sink0Connect" -> Constraint.Connected(Ref("sink0", "port"), Ref.Allocate(Ref("link", "sinks"))),
      "sink1Connect" -> Constraint.Connected(Ref("sink1", "port"), Ref.Allocate(Ref("link", "sinks"))),
      "sinkArrayConnect" -> Constraint.Connected(
        Ref.Allocate(Ref("sinkArray", "port")),
        Ref.Allocate(Ref("link", "sinks"))
      ),
      "sourceExport" -> Constraint.Exported(Ref("port"), Ref("exportSource", "port")),
      "bundleSourceExport" -> Constraint.Exported(Ref("bundle", "port"), Ref("exportBundleSource", "port")),
    )
  ).getHierarchy

  val exampleArrayBlock = Block.Block( // basic example using link arrays
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
        "sourceArrayBlock",
        ports = SeqMap(
          "port" -> Port.Array(
            "sourcePort",
            Seq("0", "1"),
            Port.Port("sourcePort", params = SeqMap("param" -> ValInit.Integer))
          ),
        ),
      ),
      "sink0" -> Block.Block(
        "sinkArrayBlock",
        ports = SeqMap(
          "port" -> Port.Array(
            "sinkPort",
            Seq("0", "1"),
            Port.Port("sinkPort", params = SeqMap("param" -> ValInit.Integer))
          ),
        ),
      ),
      "sink1" -> Block.Block(
        "sinkArrayBlock",
        ports = SeqMap(
          "port" -> Port.Array(
            "sinkPort",
            Seq("0", "1"),
            Port.Port("sinkPort", params = SeqMap("param" -> ValInit.Integer))
          ),
        ),
      ),
      "sinkArray" -> Block.Block(
        "sinkArrayBlock",
        ports = SeqMap(
          "port" -> Port.Array(
            "sinkPort",
            Seq("0", "1"),
            Port.Port("sinkPort", params = SeqMap("param" -> ValInit.Integer))
          ),
        ),
      ),
    ),
    links = SeqMap(
      "link" -> Link.Array("link"),
    ),
    constraints = SeqMap(
      "sourceConnect" -> Constraint.ConnectedArray(Ref("source", "port"), Ref("link", "source")),
      "sink0Connect" -> Constraint.ConnectedArray(Ref("sink0", "port"), Ref.Allocate(Ref("link", "sinks"))),
      "sink1Connect" -> Constraint.ConnectedArray(Ref("sink1", "port"), Ref.Allocate(Ref("link", "sinks"))),
      "sinkArrayConnect" -> Constraint.ConnectedArray(
        Ref.Allocate(Ref("sinkArray", "port")),
        Ref.Allocate(Ref("link", "sinks"))
      ),
    )
  ).getHierarchy

  val exampleLink = Link.Link(
    "link",
    ports = SeqMap(
      "source" -> Port.Port("sourcePort"),
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

  it should "build valid connects from empty, starting with a port" in {
    val emptyConnect = ConnectBuilder(exampleBlock, exampleLink, Seq())
    emptyConnect should not be empty
    emptyConnect.get.connectMode should equal(ConnectMode.Ambiguous)

    val sourceConnect = emptyConnect.get.append(Seq(
      (ConnectTypes.BlockPort("source", "port"), LibraryPath("sourcePort"))
    ))
    sourceConnect should not be empty
    sourceConnect.get.connectMode should equal(ConnectMode.Port)

    val sink0Connect = sourceConnect.get.append(Seq(
      (ConnectTypes.BlockPort("sink0", "port"), LibraryPath("sinkPort"))
    ))
    sink0Connect should not be empty
    sink0Connect.get.connectMode should equal(ConnectMode.Port)
  }

  it should "build valid port connects from empty, starting with an ambiguous vector" in {
    val emptyConnect = ConnectBuilder(exampleBlock, exampleLink, Seq())
    val sliceConnect = emptyConnect.get.append(Seq(
      (ConnectTypes.BlockVectorSlice("sinkArray", "port", None), LibraryPath("sinkPort"))
    ))
    sliceConnect should not be empty
    sliceConnect.get.connectMode should equal(ConnectMode.Ambiguous) // stays ambiguous

    val sink0Connect = sliceConnect.get.append(Seq(
      (ConnectTypes.BlockPort("sink0", "port"), LibraryPath("sinkPort"))
    ))
    sink0Connect should not be empty
    sink0Connect.get.connectMode should equal(ConnectMode.Port) // connection type resolved here
  }

  it should "build valid array connects from empty, starting with an ambiguous vector" in {
    val emptyConnect = ConnectBuilder(exampleBlock, exampleLink, Seq())
    val sliceConnect = emptyConnect.get.append(Seq(
      (ConnectTypes.BlockVectorSlice("sinkArray", "port", None), LibraryPath("sinkPort"))
    ))

    val sinkArrayConnect = sliceConnect.get.append(Seq(
      (ConnectTypes.BlockVectorUnit("sinkArray2", "port"), LibraryPath("sinkPort"))
    ))
    sinkArrayConnect should not be empty
    sinkArrayConnect.get.connectMode should equal(ConnectMode.Vector) // connection type resolved here
  }

  it should "build valid connects with multiple allocations to an array" in {
    val connect = ConnectBuilder(
      exampleBlock,
      exampleLink,
      Seq(
        exampleBlock.constraints.toSeqMap("sink0Connect"),
        exampleBlock.constraints.toSeqMap("sink1Connect"),
        exampleBlock.constraints.toSeqMap("sinkArrayConnect")
      )
    )
    connect should not be empty
    connect.get.connectMode should equal(ConnectMode.Port)
  }

  it should "not overallocate single connects" in {
    val sourceConnect = ConnectBuilder(
      exampleBlock,
      exampleLink,
      Seq(exampleBlock.constraints.toSeqMap("sourceConnect"))
    ).get
    sourceConnect.append(Seq(
      (ConnectTypes.BlockPort("source", "port"), LibraryPath("sourcePort"))
    )) shouldBe empty
  }

  it should "allow appending vector slices in port mode" in {
    val sourceConnect = ConnectBuilder(
      exampleBlock,
      exampleLink,
      Seq(exampleBlock.constraints.toSeqMap("sourceConnect"), exampleBlock.constraints.toSeqMap("sink0Connect"))
    ).get
    val sinkConnected = sourceConnect.append(Seq(
      (ConnectTypes.BlockPort("sink1", "port"), LibraryPath("sinkPort"))
    ))
    sinkConnected should not be empty
    val sliceConnected = sinkConnected.get.append(Seq(
      (ConnectTypes.BlockVectorSlicePort("sinkArray", "port", None), LibraryPath("sinkPort"))
    ))
    sliceConnected should not be empty
    sliceConnected.get.connectMode should equal(ConnectMode.Port)
  }
}
