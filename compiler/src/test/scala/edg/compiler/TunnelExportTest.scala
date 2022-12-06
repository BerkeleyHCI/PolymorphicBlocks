package edg.compiler

import edg.CompilerTestUtil
import edg.ElemBuilder._
import edg.ExprBuilder.ValueExpr.RefAllocate
import edg.ExprBuilder.{Ref, ValInit, ValueExpr}
import edg.wir.ProtoUtil.ConstraintProtoToSeqMap
import edg.wir.{IndirectDesignPath, IndirectStep}
import org.scalatest._
import org.scalatest.flatspec.AnyFlatSpec
import org.scalatest.matchers.should.Matchers._

import scala.collection.SeqMap


/** Tests tunnel exports.
  */
class TunnelExportTest extends AnyFlatSpec with CompilerTestUtil {
  import edgir.expr.expr.UnarySetExpr.Op
  val library = Library(
    ports = Seq(
      Port.Port("port",
        params = SeqMap(
          "floatVal" -> ValInit.Floating,
        )
      ),
    ),
    blocks = Seq(
      Block.Block("portBlock",
        params = SeqMap(
          "portVal" -> ValInit.Floating,
          "blockVal" -> ValInit.Floating,
        ),
        ports = SeqMap(
          "port" -> Port.Library("port"),
        ),
        constraints = SeqMap(
          "innerVal" -> Constraint.Assign(Ref("port", "floatVal"), ValueExpr.Ref("portVal")),
        ),
      ),
      Block.Block("portBlockContainer",
        params = SeqMap(
          "portVal" -> ValInit.Floating,
          "blockVal" -> ValInit.Floating,
        ),
        ports = SeqMap(
          "port" -> Port.Library("port"),
        ),
        blocks = SeqMap(
          "inner" -> Block.Library("portBlock")
        ),
        constraints = SeqMap(
          "export" -> Constraint.Exported(Ref("port"), Ref("inner", "port")),
          "innerPortVal" -> Constraint.Assign(Ref("inner", "portVal"), ValueExpr.Ref("portVal")),
          "innerBlockVal" -> Constraint.Assign(Ref("inner", "blockVal"), ValueExpr.Ref("blockVal")),
        ),
      ),
      Block.Block("portBlockArray2",  // without generators, the length must be fixed
        params = SeqMap(
          "portVal" -> ValInit.Floating,
          "block0Val" -> ValInit.Floating,
          "block1Val" -> ValInit.Floating,
        ),
        ports = SeqMap(
          "ports" -> Port.Array("port", Seq("0", "1"), Port.Library("port")),
        ),
        constraints = SeqMap(
          "innerVal0" -> Constraint.Assign(Ref("port", "0", "floatVal"), ValueExpr.Ref("portVal")),
          "innerVal1" -> Constraint.Assign(Ref("port", "1", "floatVal"), ValueExpr.Ref("portVal")),
        ),
      ),
    ),
    links = Seq(
      Link.Link("link",
        ports = SeqMap(
          "ports" -> Port.Array("port"),
        ),
        params = SeqMap(
          "sum" -> ValInit.Floating,
          "hull" -> ValInit.Range,
        ),
        constraints = SeqMap(
          "calcSum" -> ValueExpr.Assign(Ref("sum"), ValueExpr.UnarySetOp(Op.SUM,
            ValueExpr.MapExtract(Ref("ports"), Ref("floatVal"))
          )),
          "calcHull" -> ValueExpr.Assign(Ref("hull"), ValueExpr.UnarySetOp(Op.HULL,
            ValueExpr.MapExtract(Ref("ports"), Ref("floatVal"))
          )),
        )
      ),
    )
  )

  "Compiler on design with single tunnel export" should "propagate and evaluate values" in {
    val inputDesign = Design(Block.Block("topDesign",
      blocks = SeqMap(
        "container" -> Block.Library("portBlockContainer"),
        "packedBlock" -> Block.Library("portBlock"),
      ),
      links = SeqMap(
        "link" -> Link.Library("link")
      ),
      constraints = SeqMap(
        "containerPortVal" -> ValueExpr.Assign(Ref("container", "portVal"), ValueExpr.Literal(1.0)),
        "containerBlockVal" -> ValueExpr.Assign(Ref("container", "blockVal"), ValueExpr.Literal(8.0)),
        "containerConnect" -> Constraint.Connected(Ref("container", "port"), Ref.Allocate(Ref("link", "ports"))),

        "packedAssign" -> Constraint.Assign(Ref("packedBlock", "blockVal"), ValueExpr.Ref("container", "blockVal")),
        "packedExport" -> Constraint.ExportedTunnel(Ref("container", "inner", "port"), Ref("packedBlock", "port")),
      )
    ))
    val (compiler, compiled) = testCompile(inputDesign, library)

    compiler.getValue(IndirectDesignPath() + "packedBlock" + "port" + "floatVal") should equal(Some(FloatValue(1.0)))
    compiler.getValue(IndirectDesignPath() + "packedBlock" + "blockVal") should equal(Some(FloatValue(8.0)))

    compiler.getValue(IndirectDesignPath() + "link" + "sum") should equal(Some(FloatValue(1.0)))
    compiler.getValue(IndirectDesignPath() + "link" + "hull") should equal(Some(RangeValue(1.0, 1.0)))

    // check CONNECTED_LINK through outer (direct connection)
    val linkThroughPacked = IndirectDesignPath() + "packedBlock"  + "port" + IndirectStep.ConnectedLink
    compiler.getValue(linkThroughPacked + "sum") should equal(Some(FloatValue(1.0)))
    compiler.getValue(linkThroughPacked + "hull") should equal(Some(RangeValue(1.0, 1.0)))

    // check IS_CONNECTED
    compiler.getValue(IndirectDesignPath() + "packedBlock" + "port" + IndirectStep.IsConnected) should equal(
      Some(BooleanValue(true)))
    compiler.getValue(IndirectDesignPath() + "link" + "ports" + "0" + IndirectStep.IsConnected) should equal(
      Some(BooleanValue(true)))
  }

  "Compiler on design with disconnected tunnel export" should "propagate and evaluate values" in {
    val inputDesign = Design(Block.Block("topDesign",
      blocks = SeqMap(
        "container" -> Block.Library("portBlockContainer"),
        "packedBlock" -> Block.Library("portBlock"),
      ),
      links = SeqMap(
      ),
      constraints = SeqMap(
        "packedExport" -> Constraint.ExportedTunnel(Ref("container", "inner", "port"), Ref("packedBlock", "port")),
      )
    ))
    val (compiler, compiled) = testCompile(inputDesign, library)

    // check IS_CONNECTED
    compiler.getValue(IndirectDesignPath() + "packedBlock" + "port" + IndirectStep.IsConnected) should equal(
      Some(BooleanValue(false)))
  }

  "Compiler on design with array tunnel export" should "propagate and evaluate values" in {
    val inputDesign = Design(Block.Block("topDesign",
      blocks = SeqMap(
        "container" -> Block.Library("portBlockContainer"),
        "block" -> Block.Library("portBlock"),

        "packedBlock" -> Block.Library("portBlockArray2"),
      ),
      links = SeqMap(
        "link" -> Link.Library("link")
      ),
      constraints = SeqMap(
        "containerPortVal" -> ValueExpr.Assign(Ref("container", "portVal"), ValueExpr.Literal(1.0)),
        "containerConnect" -> Constraint.Connected(Ref("container", "port"), Ref.Allocate(Ref("link", "ports"))),

        "blockPortVal" -> ValueExpr.Assign(Ref("block", "portVal"), ValueExpr.Literal(2.0)),
        "blockConnect" -> Constraint.Connected(Ref("block", "port"), Ref.Allocate(Ref("link", "ports"))),

        // Test tunnel export both directly within the top block, and nested one level deep
        "packed0Export" -> Constraint.ExportedTunnel(Ref("container", "inner", "port"), Ref.Allocate(Ref("packedBlock", "ports"), Some("0"))),
        "packed1Export" -> Constraint.ExportedTunnel(Ref("block", "port"), Ref.Allocate(Ref("packedBlock", "ports"), Some("1"))),
      )
    ))
    val (compiler, compiled) = testCompile(inputDesign, library)

    // check that allocates were properly lowered
    compiled.contents.get.constraints("packed0Export") should equal(
      Constraint.ExportedTunnel(Ref("container", "inner", "port"), Ref("packedBlock", "ports", "0"))
    )
    compiled.contents.get.constraints("packed1Export") should equal(
      Constraint.ExportedTunnel(Ref("block", "port"), Ref("packedBlock", "ports", "1"))
    )

    compiler.getValue(IndirectDesignPath() + "packedBlock" + "ports" + "0" + "floatVal") should equal(Some(FloatValue(1.0)))
    compiler.getValue(IndirectDesignPath() + "packedBlock" + "ports" + "1" + "floatVal") should equal(Some(FloatValue(2.0)))

    compiler.getValue(IndirectDesignPath() + "link" + "sum") should equal(Some(FloatValue(3.0)))
    compiler.getValue(IndirectDesignPath() + "link" + "hull") should equal(Some(RangeValue(1.0, 2.0)))

    compiler.getValue(IndirectDesignPath() + "packedBlock" + "ports" + IndirectStep.Elements) should equal(
      Some(ArrayValue(Seq(TextValue("0"), TextValue("1")))))

    // check CONNECTED_LINK through outer (direct connection)
    Seq("0", "1").foreach { portIndex =>
      val linkThroughPacked = IndirectDesignPath() + "packedBlock"  + "ports" + portIndex + IndirectStep.ConnectedLink
      compiler.getValue(linkThroughPacked + "sum") should equal(Some(FloatValue(3.0)))
      compiler.getValue(linkThroughPacked + "hull") should equal(Some(RangeValue(1.0, 2.0)))
    }

    // check IS_CONNECTED
    compiler.getValue(IndirectDesignPath() + "packedBlock" + "ports" + "0" + IndirectStep.IsConnected) should equal(
      Some(BooleanValue(true)))
    compiler.getValue(IndirectDesignPath() + "packedBlock" + "ports" + "1" + IndirectStep.IsConnected) should equal(
      Some(BooleanValue(true)))
    compiler.getValue(IndirectDesignPath() + "link" + "ports" + "0" + IndirectStep.IsConnected) should equal(
      Some(BooleanValue(true)))
    compiler.getValue(IndirectDesignPath() + "link" + "ports" + "1" + IndirectStep.IsConnected) should equal(
      Some(BooleanValue(true)))
  }
}
