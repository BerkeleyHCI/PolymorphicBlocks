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
        ports = SeqMap(
          "port" -> Port.Library("port"),
        ),
        constraints = SeqMap(
          "constFloatVal" -> ValueExpr.Assign(Ref("port", "floatVal"), ValueExpr.Literal(1.0)),
        )
      ),
      Block.Block(
        "emptyLeafBlock",
        ports = SeqMap(
          "port" -> Port.Library("port"),
        ),
      ),
      Block.Block(
        "exportTapBlock",
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
      // array test support
      Block.Block(
        "leafArrayBlock",
        ports = SeqMap(
          "port" -> Port.Array("port", Seq("0", "1"), Port.Library("port")),
        ),
        constraints = SeqMap(
          "constFloatVal0" -> ValueExpr.Assign(Ref("port", "0", "floatVal"), ValueExpr.Literal(1.0)),
          "constFloatVal1" -> ValueExpr.Assign(Ref("port", "1", "floatVal"), ValueExpr.Literal(2.0)),
        )
      ),
      Block.Block(
        "emptyLeafArrayBlock",
        ports = SeqMap( // port definition must be synchronized with the outer block
          "port" -> Port.Array("port", Seq("0", "1"), Port.Library("port"))),
      ),
      Block.Block(
        "exportArrayTapBlock",
        ports = SeqMap(
          "port" -> Port.Array("port"),
        ),
        blocks = SeqMap(
          "inner" -> Block.Library("leafArrayBlock"),
          "innerTap" -> Block.Library("emptyLeafArrayBlock")
        ),
        constraints = SeqMap(
          "export" -> Constraint.ExportedArray(Ref("port"), Ref("inner", "port")),
          "tap" -> Constraint.ExportedArray(Ref("port"), Ref("innerTap", "port"), tap = true),
        )
      ),
      Block.Block(
        "emptyLeafArrayBlockBad",
        ports = SeqMap( // contains mismatched port elements
          "port" -> Port.Array("port", Seq("0"), Port.Library("port"))),
      ),
      Block.Block(
        "exportArrayTapBlockBad",
        ports = SeqMap(
          "port" -> Port.Array("port"),
        ),
        blocks = SeqMap(
          "inner" -> Block.Library("leafArrayBlock"),
          "innerTap" -> Block.Library("emptyLeafArrayBlockBad")
        ),
        constraints = SeqMap(
          "export" -> Constraint.ExportedArray(Ref("port"), Ref("inner", "port")),
          "tap" -> Constraint.ExportedArray(Ref("port"), Ref("innerTap", "port"), tap = true),
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
    compiler.getValue(
      IndirectDesignPath() + "tap" + "innerTap" + "port" + IndirectStep.ConnectedLink + "floatSum"
    ) should equal(
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
    an[TestFailedException] should be thrownBy testCompile(inputDesign, library)
  }

  "Compiler on design with tap export array" should "propagate allocated values" in {
    val inputDesign = Design(Block.Block(
      "topDesign",
      blocks = SeqMap(
        "tap" -> Block.Library("exportArrayTapBlock"),
      ),
      links = SeqMap(
        "link" -> Link.Library("link")
      ),
      constraints = SeqMap(
        "tapConnect0" -> Constraint.Connected(
          Ref.Allocate(Ref("tap", "port"), Some("0")),
          Ref.Allocate(Ref("link", "ports"))
        ),
        "tapConnect1" -> Constraint.Connected(
          Ref.Allocate(Ref("tap", "port"), Some("1")),
          Ref.Allocate(Ref("link", "ports"))
        ),
      )
    ))
    val (compiler, compiled) = testCompile(inputDesign, library)

    compiler.getValue(IndirectDesignPath() + "tap" + "innerTap" + "port" + IndirectStep.Allocated) should equal(
      Some(ArrayValue(Seq(TextValue("0"), TextValue("1"))))
    )
    compiler.getValue(IndirectDesignPath() + "link" + "floatSum") should equal(
      Some(FloatValue(3.0))
    )
    compiler.getValue(
      IndirectDesignPath() + "tap" + "innerTap" + "port" + "0" + IndirectStep.ConnectedLink + "floatSum"
    ) should equal(
      Some(FloatValue(3.0))
    )
  }

  "Compiler on design with tap export array with inconsistent elements" should "error" in {
    val inputDesign = Design(Block.Block(
      "topDesign",
      blocks = SeqMap(
        "tap" -> Block.Library("exportArrayTapBlockBad"),
      ),
      links = SeqMap(
        "link" -> Link.Library("link")
      ),
      constraints = SeqMap(
        "tapConnect0" -> Constraint.Connected(
          Ref.Allocate(Ref("tap", "port"), Some("0")),
          Ref.Allocate(Ref("link", "ports"))
        ),
        "tapConnect1" -> Constraint.Connected(
          Ref.Allocate(Ref("tap", "port"), Some("1")),
          Ref.Allocate(Ref("link", "ports"))
        ),
      )
    ))
    an[TestFailedException] should be thrownBy testCompile(inputDesign, library)
  }
}
