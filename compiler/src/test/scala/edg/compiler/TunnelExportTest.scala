package edg.compiler

import edg.CompilerTestUtil
import edg.ElemBuilder._
import edg.ExprBuilder.ValueExpr.RefAllocate
import edg.ExprBuilder.{Ref, ValInit, ValueExpr}
import edg.wir.{IndirectDesignPath, IndirectStep}
import org.scalatest._
import org.scalatest.flatspec.AnyFlatSpec
import org.scalatest.matchers.should.Matchers._


/** Tests tunnel exports.
  */
class TunnelExportTest extends AnyFlatSpec with CompilerTestUtil {
  import edgir.expr.expr.UnarySetExpr.Op
  val library = Library(
    ports = Seq(
      Port.Port("port",
        params = Map(
          "floatVal" -> ValInit.Floating,
        )
      ),
    ),
    blocks = Seq(
      Block.Block("portBlock",
        params = Map(
          "floatVal" -> ValInit.Floating,
        ),
        ports = Map(
          "port" -> Port.Library("port"),
        ),
        constraints = Map(
          "innerVal" -> Constraint.Assign(Ref("port", "floatVal"), ValueExpr.Ref("floatVal")),
        ),
      ),
      Block.Block("portBlockContainer",
        params = Map(
          "floatVal" -> ValInit.Floating,
        ),
        ports = Map(
          "port" -> Port.Library("port"),
        ),
        blocks = Map(
          "inner" -> Block.Library("portBlock")
        ),
        constraints = Map(
          "export" -> Constraint.Exported(Ref("port"), Ref("inner", "port")),
          "innerVal" -> Constraint.Assign(Ref("inner", "floatVal"), ValueExpr.Ref("floatVal")),
        ),
      ),
    ),
    links = Seq(
      Link.Link("link",
        ports = Map(
          "ports" -> Port.Array("port"),
        ),
        params = Map(
          "sum" -> ValInit.Floating,
          "hull" -> ValInit.Range,
        ),
        constraints = Map(
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
      blocks = Map(
        "container" -> Block.Library("portBlockContainer"),
        "packedBlock" -> Block.Library("portBlock"),
      ),
      links = Map(  // no connections here
      ),
      constraints = Map(
        "containerVal" -> ValueExpr.Assign(Ref("container", "floatVal"), ValueExpr.Literal(1.0)),

        "packedExport" -> Constraint.ExportedTunnel(Ref("packedBlock", "port"), Ref("container", "inner", "port")),
      )
    ))
    val (compiler, compiled) = testCompile(inputDesign, library)

    compiler.getValue(IndirectDesignPath() + "packedBlock"  + "port" + "floatValue") should equal(Some(FloatValue(1.0)))

//    // check CONNECTED_LINK through outer (direct connection)
//    val linkThroughSource = IndirectDesignPath() + "source" + "port" + IndirectStep.ConnectedLink
//    compiler.getValue(linkThroughSource + "sourceFloat") should equal(Some(FloatValue(3.0)))
//    compiler.getValue(linkThroughSource + "sinkSum") should equal(Some(FloatValue(1.0)))
//    compiler.getValue(linkThroughSource + "sinkIntersect") should equal(Some(RangeValue(5.0, 7.0)))
//    compiler.getValue(linkThroughSource + IndirectStep.Name) should equal(Some(TextValue("link")))
//
//    // check CONNECTED_LINK through inner (via exports)
//    val linkThroughInnerSource = IndirectDesignPath() + "source" + "inner" + "port" + IndirectStep.ConnectedLink
//    compiler.getValue(linkThroughInnerSource + "sourceFloat") should equal(Some(FloatValue(3.0)))
//    compiler.getValue(linkThroughInnerSource + "sinkSum") should equal(Some(FloatValue(1.0)))
//    compiler.getValue(linkThroughInnerSource + "sinkIntersect") should equal(Some(RangeValue(5.0, 7.0)))
//    compiler.getValue(linkThroughInnerSource + IndirectStep.Name) should equal(Some(TextValue("link")))
//
//    // check IS_CONNECTED
//    compiler.getValue(IndirectDesignPath() + "source" + "port" + IndirectStep.IsConnected) should equal(
//      Some(BooleanValue(true)))
//    compiler.getValue(IndirectDesignPath() + "source" + "inner" + "port" + IndirectStep.IsConnected) should equal(
//      Some(BooleanValue(true)))
  }
}
