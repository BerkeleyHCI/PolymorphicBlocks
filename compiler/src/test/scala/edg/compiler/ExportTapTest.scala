package edg.compiler

import edg.CompilerTestUtil
import edg.ElemBuilder._
import edg.ExprBuilder.{Ref, ValInit, ValueExpr}
import edg.wir.ProtoUtil.ConstraintProtoToSeqMap
import edg.wir.{IndirectDesignPath, IndirectStep}
import org.scalatest.exceptions.TestFailedException
import org.scalatest.flatspec.AnyFlatSpec
import org.scalatest.matchers.should.Matchers._

import scala.collection.SeqMap

/** Tests export taps.
  */
class ExportTapTest extends AnyFlatSpec with CompilerTestUtil {
  import edgir.expr.expr.UnarySetExpr.Op
  val library = Library(
    ports = Seq(
      Port.Port(
        "port",
        params = SeqMap(
          "floatVal" -> ValInit.Floating,
        )
      ),
    ),
    blocks = Seq(
      Block.Block(
        "leafBlock",
        params = SeqMap(
        ),
        ports = SeqMap(
          "port" -> Port.Library("port"),
        ),
        constraints = SeqMap(
          "constFloatVal" -> ValueExpr.Assign(Ref("port", "floatVal"), ValueExpr.Literal(1.0)),
        )
      ),
      Block.Block(
        "emptyLeafBlock",
        params = SeqMap(
        ),
        ports = SeqMap(
          "port" -> Port.Library("port"),
        ),
        constraints = SeqMap(
        )
      ),
      Block.Block(
        "exportTapBlock",
        params = SeqMap(
          "floatVal" -> ValInit.Floating,
        ),
        ports = SeqMap(
          "port" -> Port.Library("port"),
        ),
        blocks = SeqMap(
          "inner" -> Block.Library("leafBlock"),
          "innerTap" -> Block.Library("emptyLeafBlock")
        ),
        constraints = SeqMap(
          "export" -> Constraint.Exported(Ref("port"), Ref("inner", "port")),
          "tap" -> Constraint.Exported(Ref("port"), Ref("innerTap", "port"), tap = true),
        )
      ),
      Block.Block(
        "badExportTapBlock",
        params = SeqMap(
          "floatVal" -> ValInit.Floating,
        ),
        ports = SeqMap(
          "port" -> Port.Library("port"),
        ),
        blocks = SeqMap(
          "inner" -> Block.Library("leafBlock"),
          "innerTap" -> Block.Library("leafBlock") // also defines parameters
        ),
        constraints = SeqMap(
          "export" -> Constraint.Exported(Ref("port"), Ref("inner", "port")),
          "tap" -> Constraint.Exported(Ref("port"), Ref("innerTap", "port"), tap = true),
        )
      ),
    ),
    links = Seq(
      Link.Link(
        "link",
        ports = SeqMap(
          "ports" -> Port.Array("port"),
        ),
        params = SeqMap(
          "floatSum" -> ValInit.Floating,
        ),
        constraints = SeqMap(
          "calcFloatSum" -> ValueExpr.Assign(
            Ref("floatSum"),
            ValueExpr.UnarySetOp(Op.SUM, ValueExpr.MapExtract(Ref("ports"), Ref("floatVal")), ValueExpr.Literal(0.0))
          ),
        )
      ),
    )
  )

  "Compiler on design with tap exports" should "propagate and evaluate values" in {
    val inputDesign = Design(Block.Block(
      "topDesign",
      blocks = SeqMap(
        "leaf" -> Block.Library("leafBlock"),
        "tap" -> Block.Library("exportTapBlock"),
      ),
      links = SeqMap(
        "link" -> Link.Library("link")
      ),
      constraints = SeqMap(
        "leafConnect" -> Constraint.Connected(Ref("leaf", "port"), Ref.Allocate(Ref("link", "ports"))),
        "tapConnect" -> Constraint.Connected(Ref("tap", "port"), Ref.Allocate(Ref("link", "ports"))),
      )
    ))
    val (compiler, compiled) = testCompile(inputDesign, library)

    compiler.getValue(IndirectDesignPath() + "link" + "floatSum") should equal(
      Some(FloatValue(2.0))
    )
  }

  "Compiler on design with bad tap exports" should "error" in {
    val inputDesign = Design(Block.Block(
      "topDesign",
      blocks = SeqMap(
        "tap" -> Block.Library("badExportTapBlock"),
      ),
      links = SeqMap(
        "link" -> Link.Library("link")
      ),
      constraints = SeqMap(
        "tapConnect" -> Constraint.Connected(Ref("tap", "port"), Ref.Allocate(Ref("link", "ports"))),
      )
    ))
    an[TestFailedException] should be thrownBy testCompile(inputDesign, library) // test the test helper code
  }
}
