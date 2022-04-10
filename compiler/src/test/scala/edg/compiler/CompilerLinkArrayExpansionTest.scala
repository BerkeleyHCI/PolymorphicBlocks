package edg.compiler

import edg.CompilerTestUtil
import edg.ElemBuilder._
import edg.ExprBuilder.{Ref, ValInit, ValueExpr}
import edgir.ref.ref
import edg.wir.{IndirectDesignPath, IndirectStep}
import org.scalatest.flatspec.AnyFlatSpec
import org.scalatest.matchers.should.Matchers._


/** Tests compiler LinkArray expansion / elaboration and connected constraint allocation with block-side PortArray.
  * TODO: deduplicate libraries w/ block port array tests?
  */
class CompilerLinkArrayExpansionTest extends AnyFlatSpec with CompilerTestUtil {
  val library = Library(
    ports = Seq(
      Port.Port("sourcePort", params=Map("param" -> ValInit.Integer)),
      Port.Port("sinkPort", params=Map("param" -> ValInit.Integer)),
    ),
    blocks = Seq(
      Block.Block("sourceBlock",  // array elements source
        ports = Map(
          "port" -> Port.Array("sourcePort", Seq("a", "b", "c"), Port.Library("sourcePort")),
        ),
        constraints = Map(
          "port.a" -> Constraint.Assign(Ref("port", "a", "param"), ValueExpr.Literal(1)),
          "port.b" -> Constraint.Assign(Ref("port", "b", "param"), ValueExpr.Literal(2)),
          "port.c" -> Constraint.Assign(Ref("port", "c", "param"), ValueExpr.Literal(3)),
        )
      ),
      Block.Block("sinkBlock",  // array elements sink
        ports = Map(
          "port" -> Port.Array("sinkPort", Seq("a", "b", "c"), Port.Library("sinkPort")),
        ),
        constraints = Map(
          "port.a" -> Constraint.Assign(Ref("port", "a", "param"), ValueExpr.Literal(11)),
          "port.b" -> Constraint.Assign(Ref("port", "b", "param"), ValueExpr.Literal(12)),
          "port.c" -> Constraint.Assign(Ref("port", "c", "param"), ValueExpr.Literal(13)),
        )
      ),
      Block.Block("elasticSinkBlock",  // array elements sink
        ports = Map(
          "port" -> Port.Array("sinkPort"),
        ),
        constraints = Map(
          // Not truly correct but good enough for this test; this really needs a generator
          "elements" -> Constraint.Assign(
            ref.LocalPath(Seq(ref.LocalStep(ref.LocalStep.Step.Name("port")),
              ref.LocalStep(ref.LocalStep.Step.ReservedParam(ref.Reserved.ELEMENTS)))),
            ValueExpr.Ref(ref.LocalPath(Seq(ref.LocalStep(ref.LocalStep.Step.Name("port")),
              ref.LocalStep(ref.LocalStep.Step.ReservedParam(ref.Reserved.ALLOCATED)))))
          ),
        )
      ),
    ),
    links = Seq(
      Link.Link("link",
        ports = Map(
          "source" -> Port.Library("sourcePort"),
          "sinks" -> Port.Array("sinkPort"),
        ),
        params = Map(
          "param" -> ValInit.Integer
        ), constraints = Map(
          "param_set" -> Constraint.Assign(Ref("param"), ValueExpr.Literal(-1)),
        )
      ),
    )
  )

  "Compiler on design with link-array" should "expand constraints and link arrays" in {
    val inputDesign = Design(Block.Block("topDesign",
      blocks = Map(
        "source" -> Block.Library("sourceBlock"),
        "sink0" -> Block.Library("sinkBlock"),
        "sink1" -> Block.Library("sinkBlock"),
      ),
      links = Map(
        "link" -> Link.Array("link"),
      ),
      constraints = Map(
        "sourceConnect" -> Constraint.ConnectedArray(Ref("source", "port"), Ref("link", "source")),
        "sink0Connect" -> Constraint.ConnectedArray(Ref("sink0", "port"), Ref.Allocate(Ref("link", "sinks"))),
        "sink1Connect" -> Constraint.ConnectedArray(Ref("sink1", "port"), Ref.Allocate(Ref("link", "sinks"))),
      )
    ))
    val referenceConstraints = Map(  // expected constraints in the top-level design
      "sourceConnect.a" -> Constraint.Connected(Ref("source", "port", "a"), Ref("link", "source", "a")),
      "sourceConnect.b" -> Constraint.Connected(Ref("source", "port", "b"), Ref("link", "source", "b")),
      "sourceConnect.c" -> Constraint.Connected(Ref("source", "port", "c"), Ref("link", "source", "c")),

      "sink0Connect.a" -> Constraint.Connected(Ref("sink0", "port", "a"), Ref("link", "sinks", "0", "a")),
      "sink0Connect.b" -> Constraint.Connected(Ref("sink0", "port", "b"), Ref("link", "sinks", "0", "b")),
      "sink0Connect.c" -> Constraint.Connected(Ref("sink0", "port", "c"), Ref("link", "sinks", "0", "c")),
      "sink1Connect.a" -> Constraint.Connected(Ref("sink1", "port", "a"), Ref("link", "sinks", "1", "a")),
      "sink1Connect.b" -> Constraint.Connected(Ref("sink1", "port", "b"), Ref("link", "sinks", "1", "b")),
      "sink1Connect.c" -> Constraint.Connected(Ref("sink1", "port", "c"), Ref("link", "sinks", "1", "c")),
    )
    val referenceLinkArrayConstraints = Map(  // expected constraints in the link array
      "source.a" -> Constraint.Exported(Ref("source", "a"), Ref("a", "source")),
      "source.b" -> Constraint.Exported(Ref("source", "b"), Ref("b", "source")),
      "source.c" -> Constraint.Exported(Ref("source", "c"), Ref("c", "source")),

      "sinks.0.a" -> Constraint.Exported(Ref("sinks", "0", "a"), Ref("a", "sinks", "0")),
      "sinks.0.b" -> Constraint.Exported(Ref("sinks", "0", "b"), Ref("b", "sinks", "0")),
      "sinks.0.c" -> Constraint.Exported(Ref("sinks", "0", "c"), Ref("c", "sinks", "0")),
      "sinks.1.a" -> Constraint.Exported(Ref("sinks", "1", "a"), Ref("a", "sinks", "1")),
      "sinks.1.b" -> Constraint.Exported(Ref("sinks", "1", "b"), Ref("b", "sinks", "1")),
      "sinks.1.c" -> Constraint.Exported(Ref("sinks", "1", "c"), Ref("c", "sinks", "1")),
    )

    val (compiler, compiled) = testCompile(inputDesign, library)

    compiled.getContents.constraints should equal(referenceConstraints)

    compiler.getValue(IndirectDesignPath() + "link" + IndirectStep.Elements) should
        equal(Some(ArrayValue(Seq(TextValue("a"), TextValue("b"), TextValue("c")))))

    compiler.getValue(IndirectDesignPath() + "link" + "source" + IndirectStep.Elements) should
        equal(Some(ArrayValue(Seq(TextValue("a"), TextValue("b"), TextValue("c")))))
    compiler.getValue(IndirectDesignPath() + "link" + "source" + IndirectStep.Length) should
        equal(Some(IntValue(3)))

    compiler.getValue(IndirectDesignPath() + "link" + "sinks" + IndirectStep.Elements) should
        equal(Some(ArrayValue(Seq(TextValue("0"), TextValue("1")))))
    compiler.getValue(IndirectDesignPath() + "link" + "sinks" + IndirectStep.Length) should
        equal(Some(IntValue(2)))
    Seq("0", "1").foreach { sinkIndex =>
      compiler.getValue(IndirectDesignPath() + "link" + "sinks" + sinkIndex + IndirectStep.Elements) should
          equal(Some(ArrayValue(Seq(TextValue("a"), TextValue("b"), TextValue("c")))))
      compiler.getValue(IndirectDesignPath() + "link" + "sinks" + sinkIndex + IndirectStep.Length) should
          equal(Some(IntValue(3)))
    }

    val linkPb = compiled.getContents.links("link").getArray
    linkPb.constraints should equal(referenceLinkArrayConstraints)

    linkPb.links.keySet should equal(Set("a", "b", "c"))
    Seq("a", "b", "c").foreach { elementIndex =>
      linkPb.links(elementIndex).getLink.getSelfClass should equal(LibraryPath("link"))
      compiler.getValue(IndirectDesignPath() + "link" + elementIndex + "sinks" + IndirectStep.Elements) should
          equal(Some(ArrayValue(Seq(TextValue("0"), TextValue("1")))))
      compiler.getValue(IndirectDesignPath() + "link" + elementIndex + "sinks" + IndirectStep.Length) should
          equal(Some(IntValue(2)))
    }

    // Check parameter propagation
    Map("a" -> 1, "b" -> 2, "c" -> 3).foreach { case (elementIndex, paramValue) =>
      compiler.getValue(IndirectDesignPath() + "link" + "source" + elementIndex + "param") should
          equal(Some(IntValue(paramValue)))
      compiler.getValue(IndirectDesignPath() + "link" + elementIndex + "source" + "param") should
          equal(Some(IntValue(paramValue)))
    }

    Seq("0", "1").foreach { sinkIndex =>
      Map("a" -> 11, "b" -> 12, "c" -> 13).foreach { case (elementIndex, paramValue) =>
        compiler.getValue(IndirectDesignPath() + "link" + "sinks" + sinkIndex + elementIndex + "param") should
            equal(Some(IntValue(paramValue)))
        compiler.getValue(IndirectDesignPath() + "link" + elementIndex + "sinks" + sinkIndex + "param") should
            equal(Some(IntValue(paramValue)))
      }
    }

    Seq("a", "b", "c").foreach { elementIndex =>
      compiler.getValue(IndirectDesignPath() + "source" + "port" + elementIndex + IndirectStep.ConnectedLink + "param") should
          equal(Some(IntValue(-1)))
    }
    Seq("0", "1").foreach { sinkIndex =>
      Seq("a", "b", "c").foreach { elementIndex =>
        compiler.getValue(IndirectDesignPath() + s"sink$sinkIndex" + "port" + elementIndex + IndirectStep.ConnectedLink + "param") should
            equal(Some(IntValue(-1)))
      }
    }
  }

  "Compiler on design with partially-connected link-arrays" should "work" in {
    val inputDesign = Design(Block.Block("topDesign",
      blocks = Map(
        "source" -> Block.Library("sourceBlock"),
      ),
      links = Map(
        "link" -> Link.Array("link"),
      ),
      constraints = Map(
        "sourceConnect" -> Constraint.ConnectedArray(Ref("source", "port"), Ref("link", "source")),
      )
    ))
    val referenceConstraints = Map(  // expected constraints in the top-level design
      "sourceConnect.a" -> Constraint.Connected(Ref("source", "port", "a"), Ref("link", "source", "a")),
      "sourceConnect.b" -> Constraint.Connected(Ref("source", "port", "b"), Ref("link", "source", "b")),
      "sourceConnect.c" -> Constraint.Connected(Ref("source", "port", "c"), Ref("link", "source", "c")),
    )
    val referenceLinkArrayConstraints = Map(  // expected constraints in the link array
      "source.a" -> Constraint.Exported(Ref("source", "a"), Ref("a", "source")),
      "source.b" -> Constraint.Exported(Ref("source", "b"), Ref("b", "source")),
      "source.c" -> Constraint.Exported(Ref("source", "c"), Ref("c", "source")),
    )

    val (compiler, compiled) = testCompile(inputDesign, library)

    compiled.getContents.constraints should equal(referenceConstraints)

    compiler.getValue(IndirectDesignPath() + "link" + IndirectStep.Elements) should
        equal(Some(ArrayValue(Seq(TextValue("a"), TextValue("b"), TextValue("c")))))

    compiler.getValue(IndirectDesignPath() + "link" + "source" + IndirectStep.Elements) should
        equal(Some(ArrayValue(Seq(TextValue("a"), TextValue("b"), TextValue("c")))))
    compiler.getValue(IndirectDesignPath() + "link" + "source" + IndirectStep.Length) should
        equal(Some(IntValue(3)))

    compiler.getValue(IndirectDesignPath() + "link" + "sinks" + IndirectStep.Elements) should
        equal(Some(ArrayValue(Seq())))
    compiler.getValue(IndirectDesignPath() + "link" + "sinks" + IndirectStep.Length) should
        equal(Some(IntValue(0)))

    val linkPb = compiled.getContents.links("link").getArray
    linkPb.constraints should equal(referenceLinkArrayConstraints)

    linkPb.links.keySet should equal(Set("a", "b", "c"))
    Seq("a", "b", "c").foreach { elementIndex =>
      linkPb.links(elementIndex).getLink.getSelfClass should equal(LibraryPath("link"))
      compiler.getValue(IndirectDesignPath() + "link" + elementIndex + "sinks" + IndirectStep.Elements) should
          equal(Some(ArrayValue(Seq())))
      compiler.getValue(IndirectDesignPath() + "link" + elementIndex + "sinks" + IndirectStep.Length) should
          equal(Some(IntValue(0)))
    }

    // Check parameter propagation
    Map("a" -> 1, "b" -> 2, "c" -> 3).foreach { case (elementIndex, paramValue) =>
      compiler.getValue(IndirectDesignPath() + "link" + "source" + elementIndex + "param") should
          equal(Some(IntValue(paramValue)))
      compiler.getValue(IndirectDesignPath() + "link" + elementIndex + "source" + "param") should
          equal(Some(IntValue(paramValue)))
    }

    Seq("a", "b", "c").foreach { elementIndex =>
      compiler.getValue(IndirectDesignPath() + "source" + "port" + elementIndex + IndirectStep.ConnectedLink + "param") should
          equal(Some(IntValue(-1)))
    }
  }

  "Compiler on design with block-side-allocated link-arrays" should "work" in {
    val inputDesign = Design(Block.Block("topDesign",
      blocks = Map(
        "source0" -> Block.Library("sourceBlock"),
        "source1" -> Block.Library("sourceBlock"),
        "sink" -> Block.Library("elasticSinkBlock"),
      ),
      links = Map(
        "link0" -> Link.Array("link"),
        "link1" -> Link.Array("link"),
      ),
      constraints = Map(
        "source0Connect" -> Constraint.ConnectedArray(Ref("source0", "port"), Ref("link0", "source")),
        "source1Connect" -> Constraint.ConnectedArray(Ref("source1", "port"), Ref("link1", "source")),
        "sinkConnect0" -> Constraint.ConnectedArray(Ref.Allocate(Ref("sink", "port")), Ref.Allocate(Ref("link0", "sinks"))),
        "sinkConnect1" -> Constraint.ConnectedArray(Ref.Allocate(Ref("sink", "port")), Ref.Allocate(Ref("link1", "sinks"))),
      )
    ))
    val referenceConstraints = Map(  // expected constraints in the top-level design
      "source0Connect.a" -> Constraint.Connected(Ref("source0", "port", "a"), Ref("link0", "source", "a")),
      "source0Connect.b" -> Constraint.Connected(Ref("source0", "port", "b"), Ref("link0", "source", "b")),
      "source0Connect.c" -> Constraint.Connected(Ref("source0", "port", "c"), Ref("link0", "source", "c")),
      "source1Connect.a" -> Constraint.Connected(Ref("source1", "port", "a"), Ref("link1", "source", "a")),
      "source1Connect.b" -> Constraint.Connected(Ref("source1", "port", "b"), Ref("link1", "source", "b")),
      "source1Connect.c" -> Constraint.Connected(Ref("source1", "port", "c"), Ref("link1", "source", "c")),
      "sinkConnect0.a" -> Constraint.Connected(Ref("sink", "port", "0"), Ref("link0", "sinks", "0", "a")),
      "sinkConnect0.b" -> Constraint.Connected(Ref("sink", "port", "1"), Ref("link0", "sinks", "0", "b")),
      "sinkConnect0.c" -> Constraint.Connected(Ref("sink", "port", "2"), Ref("link0", "sinks", "0", "c")),
      "sinkConnect1.a" -> Constraint.Connected(Ref("sink", "port", "3"), Ref("link1", "sinks", "0", "a")),
      "sinkConnect1.b" -> Constraint.Connected(Ref("sink", "port", "4"), Ref("link1", "sinks", "0", "b")),
      "sinkConnect1.c" -> Constraint.Connected(Ref("sink", "port", "5"), Ref("link1", "sinks", "0", "c")),
    )

    val (compiler, compiled) = testCompile(inputDesign, library)

    compiled.getContents.constraints should equal(referenceConstraints)

    compiler.getValue(IndirectDesignPath() + "link0" + IndirectStep.Elements) should
        equal(Some(ArrayValue(Seq(TextValue("a"), TextValue("b"), TextValue("c")))))
    compiler.getValue(IndirectDesignPath() + "link1" + IndirectStep.Elements) should
        equal(Some(ArrayValue(Seq(TextValue("a"), TextValue("b"), TextValue("c")))))

    // Don't need to test ELEMENTS, that is out of scope
    compiler.getValue(IndirectDesignPath() + "sink" + "port" + IndirectStep.Allocated) should
        equal(Some(ArrayValue(Seq(
          TextValue("0"), TextValue("1"), TextValue("2"),
          TextValue("3"), TextValue("4"), TextValue("5")
        ))))

    Seq("0", "1", "2", "3", "4", "5").foreach { elementIndex =>
      compiler.getValue(IndirectDesignPath() + "sink" + "port" + elementIndex + IndirectStep.ConnectedLink + "param") should
          equal(Some(IntValue(-1)))
    }
  }

  "Compiler on design with block-side-named-allocated link-arrays" should "work" in {
    val inputDesign = Design(Block.Block("topDesign",
      blocks = Map(
        "source0" -> Block.Library("sourceBlock"),
        "source1" -> Block.Library("sourceBlock"),
        "sink" -> Block.Library("elasticSinkBlock"),
      ),
      links = Map(
        "link0" -> Link.Array("link"),
        "link1" -> Link.Array("link"),
      ),
      constraints = Map(
        "source0Connect" -> Constraint.ConnectedArray(Ref("source0", "port"), Ref("link0", "source")),
        "source1Connect" -> Constraint.ConnectedArray(Ref("source1", "port"), Ref("link1", "source")),
        "sinkConnect0" -> Constraint.ConnectedArray(Ref.Allocate(Ref("sink", "port"), Some("n0")), Ref.Allocate(Ref("link0", "sinks"))),
        "sinkConnect1" -> Constraint.ConnectedArray(Ref.Allocate(Ref("sink", "port"), Some("n1")), Ref.Allocate(Ref("link1", "sinks"))),
      )
    ))
    val referenceConstraints = Map(  // expected constraints in the top-level design
      "source0Connect.a" -> Constraint.Connected(Ref("source0", "port", "a"), Ref("link0", "source", "a")),
      "source0Connect.b" -> Constraint.Connected(Ref("source0", "port", "b"), Ref("link0", "source", "b")),
      "source0Connect.c" -> Constraint.Connected(Ref("source0", "port", "c"), Ref("link0", "source", "c")),
      "source1Connect.a" -> Constraint.Connected(Ref("source1", "port", "a"), Ref("link1", "source", "a")),
      "source1Connect.b" -> Constraint.Connected(Ref("source1", "port", "b"), Ref("link1", "source", "b")),
      "source1Connect.c" -> Constraint.Connected(Ref("source1", "port", "c"), Ref("link1", "source", "c")),
      "sinkConnect0.a" -> Constraint.Connected(Ref("sink", "port", "n0.a"), Ref("link0", "sinks", "0", "a")),
      "sinkConnect0.b" -> Constraint.Connected(Ref("sink", "port", "n0.b"), Ref("link0", "sinks", "0", "b")),
      "sinkConnect0.c" -> Constraint.Connected(Ref("sink", "port", "n0.c"), Ref("link0", "sinks", "0", "c")),
      "sinkConnect1.a" -> Constraint.Connected(Ref("sink", "port", "n1.a"), Ref("link1", "sinks", "0", "a")),
      "sinkConnect1.b" -> Constraint.Connected(Ref("sink", "port", "n1.b"), Ref("link1", "sinks", "0", "b")),
      "sinkConnect1.c" -> Constraint.Connected(Ref("sink", "port", "n1.c"), Ref("link1", "sinks", "0", "c")),
    )

    val (compiler, compiled) = testCompile(inputDesign, library)

    compiled.getContents.constraints should equal(referenceConstraints)

    compiler.getValue(IndirectDesignPath() + "link0" + IndirectStep.Elements) should
        equal(Some(ArrayValue(Seq(TextValue("a"), TextValue("b"), TextValue("c")))))
    compiler.getValue(IndirectDesignPath() + "link1" + IndirectStep.Elements) should
        equal(Some(ArrayValue(Seq(TextValue("a"), TextValue("b"), TextValue("c")))))

    // Don't need to test ELEMENTS, that is out of scope - typically would be handled by a generator
    compiler.getValue(IndirectDesignPath() + "sink" + "port" + IndirectStep.Allocated) should
        equal(Some(ArrayValue(Seq(
          TextValue("n0.a"), TextValue("n0.b"), TextValue("n0.c"),
          TextValue("n1.a"), TextValue("n1.b"), TextValue("n1.c")
        ))))

    Seq("n0.a", "n0.b", "n0.c", "n1.a", "n1.b", "n1.c").foreach { elementIndex =>
      compiler.getValue(IndirectDesignPath() + "sink" + "port" + elementIndex + IndirectStep.ConnectedLink + "param") should
          equal(Some(IntValue(-1)))
    }
  }
}
