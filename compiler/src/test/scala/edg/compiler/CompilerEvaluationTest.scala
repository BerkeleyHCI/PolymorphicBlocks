package edg.compiler

import org.scalatest._
import org.scalatest.flatspec.AnyFlatSpec
import matchers.should.Matchers._
import edg.ElemBuilder._
import edg.ExprBuilder.{Ref, ValInit, ValueExpr}
import edg.wir
import edg.wir.{IndirectDesignPath, IndirectStep}


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
      "sourceContainerBlock" -> Block.Block(
        params = Map(
          "floatVal" -> ValInit.Floating,
        ),
        ports = Map(
          "port" -> Port.Library("sourcePort"),
        ),
        blocks = Map(
          "inner" -> Block.Library("sourceBlock")
        ),
        constraints = Map(
          "export" -> Constraint.Exported(Ref("port"), Ref("inner", "port")),
          "floatAssign" -> Constraint.Assign(Ref("inner", "floatVal"), ValueExpr.Ref("floatVal")),
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
          "calcSinkSum" -> ValueExpr.Assign(Ref("sinkSum"), ValueExpr.Reduce(Op.SUM,
            ValueExpr.MapExtract(Ref("sinks"), Ref("sumVal"))
          )),
          "calcSinkIntersect" -> ValueExpr.Assign(Ref("sinkIntersect"), ValueExpr.Reduce(Op.INTERSECTION,
            ValueExpr.MapExtract(Ref("sinks"), Ref("intersectVal"))
          )),
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
    val compiler = new Compiler(inputDesign, new wir.EdgirLibrary(library))
    compiler.compile()

    // Check one-step prop
    compiler.getValue(IndirectDesignPath() + "source" + "floatVal") should equal(Some(FloatValue(3.0)))
    compiler.getValue(IndirectDesignPath() + "sink0" + "sumVal") should equal(Some(FloatValue(1.0)))
    compiler.getValue(IndirectDesignPath() + "sink0" + "intersectVal") should equal(Some(RangeValue(5.0, 7.0)))

    // Check block port prop
    compiler.getValue(IndirectDesignPath() + "source" + "port" + "floatVal") should equal(Some(FloatValue(3.0)))
    compiler.getValue(IndirectDesignPath() + "sink0" + "port" + "sumVal") should equal(Some(FloatValue(1.0)))
    compiler.getValue(IndirectDesignPath() + "sink0" + "port" + "intersectVal") should equal(Some(RangeValue(5.0, 7.0)))

    // Check link port prop
    compiler.getValue(IndirectDesignPath() + "link" + "source" + "floatVal") should equal(Some(FloatValue(3.0)))
    compiler.getValue(IndirectDesignPath() + "link" + "sinks" + "0" + "sumVal") should equal(Some(FloatValue(1.0)))
    compiler.getValue(IndirectDesignPath() + "link" + "sinks" + "0" + "intersectVal") should equal(Some(RangeValue(5.0, 7.0)))

    // check link reductions
    compiler.getValue(IndirectDesignPath() + "link" + "sourceFloat") should equal(Some(FloatValue(3.0)))
    compiler.getValue(IndirectDesignPath() + "link" + "sinkSum") should equal(Some(FloatValue(1.0)))
    compiler.getValue(IndirectDesignPath() + "link" + "sinkIntersect") should equal(Some(RangeValue(5.0, 7.0)))

    // check CONNECTED_LINK
    val linkThroughSource = IndirectDesignPath() + "source" + "port" + IndirectStep.ConnectedLink
    compiler.getValue(linkThroughSource + "sourceFloat") should equal(Some(FloatValue(3.0)))
    compiler.getValue(linkThroughSource + "sinkSum") should equal(Some(FloatValue(1.0)))
    compiler.getValue(linkThroughSource + "sinkIntersect") should equal(Some(RangeValue(5.0, 7.0)))

    val linkThroughSink0 = IndirectDesignPath() + "sink0" + "port" + IndirectStep.ConnectedLink
    compiler.getValue(linkThroughSink0 + "sourceFloat") should equal(Some(FloatValue(3.0)))
    compiler.getValue(linkThroughSink0 + "sinkSum") should equal(Some(FloatValue(1.0)))
    compiler.getValue(linkThroughSink0 + "sinkIntersect") should equal(Some(RangeValue(5.0, 7.0)))

    // check IS_CONNECTED
    compiler.getValue(IndirectDesignPath() + "source" + "port" + IndirectStep.IsConnected) should equal(
      Some(BooleanValue(true)))
    compiler.getValue(IndirectDesignPath() + "sink0" + "port" + IndirectStep.IsConnected) should equal(
      Some(BooleanValue(true)))
    compiler.getValue(IndirectDesignPath() + "link" + "source" + IndirectStep.IsConnected) should equal(
      Some(BooleanValue(true)))
    compiler.getValue(IndirectDesignPath() + "link" + "sinks" + "0" + IndirectStep.IsConnected) should equal(
      Some(BooleanValue(true)))
  }

  "Compiler on design with assign constraints and multiple connects to link" should "propagate and evaluate values" in {
    val inputDesign = Design(Block.Block(
      blocks = Map(
        "source" -> Block.Library("sourceBlock"),
        "sink0" -> Block.Library("sinkBlock"),
        "sink1" -> Block.Library("sinkBlock"),
        "sink2" -> Block.Library("sinkBlock"),
      ),
      links = Map(
        "link" -> Link.Library("link")
      ),
      constraints = Map(
        "sourceConnect" -> Constraint.Connected(Ref("source", "port"), Ref("link", "source")),
        "sink0Connect" -> Constraint.Connected(Ref("sink0", "port"), Ref.Allocate(Ref("link", "sinks"))),
        "sink1Connect" -> Constraint.Connected(Ref("sink1", "port"), Ref.Allocate(Ref("link", "sinks"))),
        "sink2Connect" -> Constraint.Connected(Ref("sink2", "port"), Ref.Allocate(Ref("link", "sinks"))),

        "sourceFloatVal" -> Constraint.Assign(Ref("source", "floatVal"), ValueExpr.Literal(3.0)),

        "sink0SumVal" -> Constraint.Assign(Ref("sink0", "sumVal"), ValueExpr.Literal(1.0)),
        "sink0IntersectVal" -> Constraint.Assign(Ref("sink0", "intersectVal"), ValueExpr.Literal(4.0, 7.0)),
        "sink1SumVal" -> Constraint.Assign(Ref("sink1", "sumVal"), ValueExpr.Literal(2.0)),
        "sink1IntersectVal" -> Constraint.Assign(Ref("sink1", "intersectVal"), ValueExpr.Literal(5.0, 8.0)),
        "sink2SumVal" -> Constraint.Assign(Ref("sink2", "sumVal"), ValueExpr.Literal(3.0)),
        "sink2IntersectVal" -> Constraint.Assign(Ref("sink2", "intersectVal"), ValueExpr.Literal(6.0, 9.0)),
      )
    ))
    val compiler = new Compiler(inputDesign, new wir.EdgirLibrary(library))
    compiler.compile()

    // check link reductions
    compiler.getValue(IndirectDesignPath() + "link" + "sourceFloat") should equal(Some(FloatValue(3.0)))
    compiler.getValue(IndirectDesignPath() + "link" + "sinkSum") should equal(Some(FloatValue(6.0)))
    compiler.getValue(IndirectDesignPath() + "link" + "sinkIntersect") should equal(Some(RangeValue(6.0, 7.0)))

    // check CONNECTED_LINK
    val linkThroughSink0 = IndirectDesignPath() + "sink0" + "port" + IndirectStep.ConnectedLink
    compiler.getValue(linkThroughSink0 + "sourceFloat") should equal(Some(FloatValue(3.0)))
    compiler.getValue(linkThroughSink0 + "sinkSum") should equal(Some(FloatValue(6.0)))
    compiler.getValue(linkThroughSink0 + "sinkIntersect") should equal(Some(RangeValue(6.0, 7.0)))

    val linkThroughSink1 = IndirectDesignPath() + "sink1" + "port" + IndirectStep.ConnectedLink
    compiler.getValue(linkThroughSink1 + "sourceFloat") should equal(Some(FloatValue(3.0)))
    compiler.getValue(linkThroughSink1 + "sinkSum") should equal(Some(FloatValue(6.0)))
    compiler.getValue(linkThroughSink1 + "sinkIntersect") should equal(Some(RangeValue(6.0, 7.0)))

    val linkThroughSink2 = IndirectDesignPath() + "sink2" + "port" + IndirectStep.ConnectedLink
    compiler.getValue(linkThroughSink2 + "sourceFloat") should equal(Some(FloatValue(3.0)))
    compiler.getValue(linkThroughSink2 + "sinkSum") should equal(Some(FloatValue(6.0)))
    compiler.getValue(linkThroughSink2 + "sinkIntersect") should equal(Some(RangeValue(6.0, 7.0)))

    // check IS_CONNECTED
    compiler.getValue(IndirectDesignPath() + "source" + "port" + IndirectStep.IsConnected) should equal(
      Some(BooleanValue(true)))
    compiler.getValue(IndirectDesignPath() + "sink0" + "port" + IndirectStep.IsConnected) should equal(
      Some(BooleanValue(true)))
    compiler.getValue(IndirectDesignPath() + "sink1" + "port" + IndirectStep.IsConnected) should equal(
      Some(BooleanValue(true)))
    compiler.getValue(IndirectDesignPath() + "sink2" + "port" + IndirectStep.IsConnected) should equal(
      Some(BooleanValue(true)))
    compiler.getValue(IndirectDesignPath() + "link" + "source" + IndirectStep.IsConnected) should equal(
      Some(BooleanValue(true)))
    compiler.getValue(IndirectDesignPath() + "link" + "sinks" + "0" + IndirectStep.IsConnected) should equal(
      Some(BooleanValue(true)))
    compiler.getValue(IndirectDesignPath() + "link" + "sinks" + "1" + IndirectStep.IsConnected) should equal(
      Some(BooleanValue(true)))
    compiler.getValue(IndirectDesignPath() + "link" + "sinks" + "2" + IndirectStep.IsConnected) should equal(
      Some(BooleanValue(true)))
  }

  "Compiler on design with exports" should "propagate and evaluate values" in {
    val inputDesign = Design(Block.Block(
      blocks = Map(
        "source" -> Block.Library("sourceContainerBlock"),
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
    val compiler = new Compiler(inputDesign, new wir.EdgirLibrary(library))
    compiler.compile()

    // check CONNECTED_LINK through outer (direct connection)
    val linkThroughSource = IndirectDesignPath() + "source" + "port" + IndirectStep.ConnectedLink
    compiler.getValue(linkThroughSource + "sourceFloat") should equal(Some(FloatValue(3.0)))
    compiler.getValue(linkThroughSource + "sinkSum") should equal(Some(FloatValue(1.0)))
    compiler.getValue(linkThroughSource + "sinkIntersect") should equal(Some(RangeValue(5.0, 7.0)))

    // check CONNECTED_LINK through inner (via exports)
    val linkThroughInnerSource = IndirectDesignPath() + "source" + "inner" + "port" + IndirectStep.ConnectedLink
    compiler.getValue(linkThroughInnerSource + "sourceFloat") should equal(Some(FloatValue(3.0)))
    compiler.getValue(linkThroughInnerSource + "sinkSum") should equal(Some(FloatValue(1.0)))
    compiler.getValue(linkThroughInnerSource + "sinkIntersect") should equal(Some(RangeValue(5.0, 7.0)))

    // check IS_CONNECTED
    compiler.getValue(IndirectDesignPath() + "source" + "port" + IndirectStep.IsConnected) should equal(
      Some(BooleanValue(true)))
    compiler.getValue(IndirectDesignPath() + "source" + "inner" + "port" + IndirectStep.IsConnected) should equal(
      Some(BooleanValue(true)))
  }

  "Compiler on design with disconnected ports" should "indicate disconnected" in {
    val inputDesign = Design(Block.Block(
      blocks = Map(
        "source" -> Block.Library("sourceBlock"),
      ),
      constraints = Map(
        // to not give an unsolved parameter error
        "sourceFloatVal" -> Constraint.Assign(Ref("source", "floatVal"), ValueExpr.Literal(3.0)),
      )
    ))
    val compiler = new Compiler(inputDesign, new wir.EdgirLibrary(library))
    compiler.compile()

    // check IS_CONNECTED
    compiler.getValue(IndirectDesignPath() + "source" + "port" + IndirectStep.IsConnected) should equal(
      Some(BooleanValue(false)))
  }

  "Compiler on design with disconnected exported ports" should "indicate disconnected" in {
    val inputDesign = Design(Block.Block(
      blocks = Map(
        "source" -> Block.Library("sourceContainerBlock"),
      ),
      constraints = Map(
        // to not give an unsolved parameter error
        "sourceFloatVal" -> Constraint.Assign(Ref("source", "floatVal"), ValueExpr.Literal(3.0)),
      )
    ))
    val compiler = new Compiler(inputDesign, new wir.EdgirLibrary(library))
    compiler.compile()

    // check IS_CONNECTED
    compiler.getValue(IndirectDesignPath() + "source" + "port" + IndirectStep.IsConnected) should equal(
      Some(BooleanValue(false)))
    compiler.getValue(IndirectDesignPath() + "source" + "inner" + "port" + IndirectStep.IsConnected) should equal(
      Some(BooleanValue(false)))
  }

  "Compiler on design with assign constraints" should "resolve if-then-else without defined non-taken branch" in {
    val inputDesign = Design(Block.Block(
      params = Map(
        "condTrue" -> ValInit.Boolean,
        "condFalse" -> ValInit.Boolean,
        "defined" -> ValInit.Integer,
        "undefined" -> ValInit.Integer,
        "ifTrue" -> ValInit.Integer,
        "ifFalse" -> ValInit.Integer,
        "ifUndef" -> ValInit.Integer,
      ),
      constraints = Map(
        "condTrue" -> Constraint.Assign(Ref("condTrue"), ValueExpr.Literal(true)),
        "condFalse" -> Constraint.Assign(Ref("condFalse"), ValueExpr.Literal(false)),
        "defined" -> Constraint.Assign(Ref("defined"), ValueExpr.Literal(45)),
        "ifTrue" -> Constraint.Assign(Ref("ifTrue"),
          ValueExpr.IfThenElse(ValueExpr.Ref("condTrue"), ValueExpr.Ref("defined"), ValueExpr.Ref("undefined"))
        ),
        "ifFalse" -> Constraint.Assign(Ref("ifFalse"),
          ValueExpr.IfThenElse(ValueExpr.Ref("condFalse"), ValueExpr.Ref("undefined"), ValueExpr.Ref("defined"))
        ),
        "ifUndef" -> Constraint.Assign(Ref("ifUndef"),
          ValueExpr.IfThenElse(ValueExpr.Ref("condFalse"), ValueExpr.Ref("defined"), ValueExpr.Ref("undefined"))
        ),
      )
    ))
    val compiler = new Compiler(inputDesign, new wir.EdgirLibrary(library))
    compiler.compile()

    compiler.getValue(IndirectDesignPath() + "ifUndef") should equal(None)
    compiler.getValue(IndirectDesignPath() + "ifTrue") should equal(Some(IntValue(45)))
    compiler.getValue(IndirectDesignPath() + "ifFalse") should equal(Some(IntValue(45)))
  }
}
