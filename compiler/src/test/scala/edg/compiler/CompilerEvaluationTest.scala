package edg.compiler

import org.scalatest._
import org.scalatest.flatspec.AnyFlatSpec
import matchers.should.Matchers._
import edg.ElemBuilder._
import edg.ExprBuilder.{Ref, ValInit, ValueExpr}
import edg.wir
import edg.wir.{DesignPath, IndirectDesignPath}


/** Tests compiler parameter and expression evaluation using ASSIGN constraints.
  */
class CompilerEvaluationTest extends AnyFlatSpec {
  import edg.expr.expr.ReductionExpr.Op
  val library = Library(
    ports = Map(
      "sourcePort" -> Port.Port(
        params = Map(
          "floatVal" -> ValInit.Floating,
        )
      ),
      "sinkPort" -> Port.Port(
        params = Map(
          "sumVal" -> ValInit.Floating,
          "intersectVal" -> ValInit.Range,
        )
      ),
    ),
    blocks = Map(
      "sourceBlock" -> Block.Block(
        params = Map(
          "floatVal" -> ValInit.Floating,
        ),
        ports = Map(
          "port" -> Port.Library("sourcePort"),
        ),
        constraints = Map(
          "propFloatVal" -> ValueExpr.Assign(Ref("port", "floatVal"), ValueExpr.Ref("floatVal")),
        )
      ),
      "sinkBlock" -> Block.Block(
        params = Map(
          "sumVal" -> ValInit.Floating,
          "intersectVal" -> ValInit.Range,
        ),
        ports = Map(
          "port" -> Port.Library("sinkPort"),
        ),
        constraints = Map(
          "propSumVal" -> ValueExpr.Assign(Ref("port", "sumVal"), ValueExpr.Ref("sumVal")),
          "propIntersectVal" -> ValueExpr.Assign(Ref("port", "intersectVal"), ValueExpr.Ref("intersectVal")),
        )
      ),
    ),
    links = Map(
      "link" -> Link.Link(
        ports = Map(
          "source" -> Port.Library("sourcePort"),
          "sinks" -> Port.Array("sinkPort"),
        ),
        params = Map(
          "sourceFloat" -> ValInit.Floating,
          "sinkSum" -> ValInit.Floating,
          "sinkIntersect" -> ValInit.Range,
        ),
        constraints = Map(
          "calcSourceFloat" -> ValueExpr.Assign(Ref("sourceFloat"), ValueExpr.Ref("source", "floatVal")),
//          "calcSinkSum" -> ValueExpr.Assign(Ref("sinkSum"), ValueExpr.Reduce(Op.SUM,
//            ValueExpr.MapExtract(Ref("sinks"), Ref("sumVal"))
//          )),
//          "calcSinkIntersect" -> ValueExpr.Assign(Ref("sinkIntersect"), ValueExpr.Reduce(Op.INTERSECTION,
//            ValueExpr.MapExtract(Ref("sinks"), Ref("intersectVal"))
//          )),
        )
      ),
    )
  )

  "Compiler on design with assign constraints" should "propagate and evaluate values" in {
    val inputDesign = Design(Block.Block(
      blocks = Map(
        "source" -> Block.Library("sourceBlock"),
        "sink0" -> Block.Library("sinkBlock"),
      ),
      links = Map(
        "link" -> Link.Library("link")
      ),
      constraints = Map(
        "sourceConnect" -> Constraint.Connected(Ref("source", "port"), Ref("link", "source")),
        "sink0Connect" -> Constraint.Connected(Ref("sink0", "port"), Ref.Allocate(Ref("link", "sinks"))),
        "sourceFloatVal" -> Constraint.Assign(Ref("source", "floatVal"), ValueExpr.Literal(3.0)),
        "sink0SumVal" -> Constraint.Assign(Ref("sink0", "sumVal"), ValueExpr.Literal(1.0)),
        "sink0IntersectVal" -> Constraint.Assign(Ref("sink0", "intersectVal"), ValueExpr.Literal(5.0, 7.0)),
      )
    ))
    val compiler = new Compiler(inputDesign, new wir.Library(library))
    compiler.compile()

    // Check one-step prop
    compiler.getValue(IndirectDesignPath.root + "source" + "floatVal") should equal(Some(FloatValue(3.0)))
    compiler.getValue(IndirectDesignPath.root + "sink0" + "sumVal") should equal(Some(FloatValue(1.0)))
    compiler.getValue(IndirectDesignPath.root + "sink0" + "intersectVal") should equal(Some(RangeValue(5.0, 7.0)))

    // Check block port prop
    compiler.getValue(IndirectDesignPath.root + "source" + "port" + "floatVal") should equal(Some(FloatValue(3.0)))
    compiler.getValue(IndirectDesignPath.root + "sink0" + "port" + "sumVal") should equal(Some(FloatValue(1.0)))
    compiler.getValue(IndirectDesignPath.root + "sink0" + "port" + "intersectVal") should equal(Some(RangeValue(5.0, 7.0)))

    // Check link port prop
    compiler.getValue(IndirectDesignPath.root + "link" + "source" + "floatVal") should equal(Some(FloatValue(3.0)))
    compiler.getValue(IndirectDesignPath.root + "link" + "sinks" + "0" + "sumVal") should equal(Some(FloatValue(1.0)))
    compiler.getValue(IndirectDesignPath.root + "link" + "sinks" + "0" + "intersectVal") should equal(Some(RangeValue(5.0, 7.0)))

    // check link reductions

  }
}
