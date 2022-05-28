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
      links = Map(
        "link" -> Link.Library("link")
      ),
      constraints = Map(
        "containerVal" -> ValueExpr.Assign(Ref("container", "floatVal"), ValueExpr.Literal(1.0)),
        "containerConnect" -> Constraint.Connected(Ref("container", "port"), Ref.Allocate(Ref("link", "ports"))),

        "packedExport" -> Constraint.ExportedTunnel(Ref("container", "inner", "port"), Ref("packedBlock", "port")),
      )
    ))
    val (compiler, compiled) = testCompile(inputDesign, library)

    compiler.getValue(IndirectDesignPath() + "packedBlock" + "port" + "floatVal") should equal(Some(FloatValue(1.0)))

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
      blocks = Map(
        "container" -> Block.Library("portBlockContainer"),
        "packedBlock" -> Block.Library("portBlock"),
      ),
      links = Map(
      ),
      constraints = Map(
        "packedExport" -> Constraint.ExportedTunnel(Ref("container", "inner", "port"), Ref("packedBlock", "port")),
      )
    ))
    val (compiler, compiled) = testCompile(inputDesign, library)

    // check IS_CONNECTED
    compiler.getValue(IndirectDesignPath() + "packedBlock" + "port" + IndirectStep.IsConnected) should equal(
      Some(BooleanValue(false)))
  }
}
