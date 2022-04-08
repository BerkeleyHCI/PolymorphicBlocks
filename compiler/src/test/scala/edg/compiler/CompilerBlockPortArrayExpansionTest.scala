package edg.compiler

import edg.CompilerTestUtil
import edg.ElemBuilder._
import edg.ExprBuilder.{Ref, ValueExpr}
import edg.wir.{DesignPath, IndirectDesignPath, IndirectStep}
import org.scalatest._
import org.scalatest.flatspec.AnyFlatSpec
import org.scalatest.matchers.should.Matchers._


/** Tests compiler PortArray expansion / elaboration and connected constraint allocation with block-side PortArray.
  * Not dependent on generators or parameter propagation.
  */
class CompilerBlockPortArrayExpansionTest extends AnyFlatSpec with CompilerTestUtil {
  val library = Library(
    ports = Seq(
      Port.Port("sourcePort"),
      Port.Port("sinkPort"),
    ),
    blocks = Seq(
      Block.Block("sourceBlock",
        ports = Map(
          "port" -> Port.Library("sourcePort"),
        )
      ),
      Block.Block("baseSinksBlock",
        ports = Map(
          "port" -> Port.Array("sinkPort"),
        )
      ),
      Block.Block("concreteSinksBlock",
        superclasses = Seq("baseSinksBlock"),
        ports = Map(
          "port" -> Port.Array("sinkPort", 2, Port.Library("sinkPort")),
        )
      ),
      Block.Block("emptySinksBlock",
        superclasses = Seq("baseSinksBlock"),
        ports = Map(
          "port" -> Port.Array("sinkPort", 0, Port.Library("sinkPort")),
        )
      ),
      Block.Block("concreteWrapperBlock",
        ports = Map(
          "port" -> Port.Array("sinkPort"),
        ),
        blocks = Map(
          "inner" -> Block.Library("concreteSinksBlock")
        ),
        constraints = Map(
          "export" -> Constraint.ExportedArray(Ref("port"), Ref("inner", "port")),
        )
      ),
      Block.Block("emptyWrapperBlock",
        ports = Map(
          "port" -> Port.Array("sinkPort"),
        ),
        blocks = Map(
          "inner" -> Block.Library("emptySinksBlock")
        ),
        constraints = Map(
          "export" -> Constraint.ExportedArray(Ref("port"), Ref("inner", "port")),
        )
      ),
    ),
    links = Seq(
      Link.Link("link",
        ports = Map(
          "source" -> Port.Library("sourcePort"),
          "sinks" -> Port.Array("sinkPort"),
        )
      ),
    )
  )

  "Compiler on design with abstract source and array sink" should "expand blocks" in {
    val inputDesign = Design(Block.Block("topDesign",
      blocks = Map(
        "source0" -> Block.Library("sourceBlock"),
        "source1" -> Block.Library("sourceBlock"),
        "source2" -> Block.Library("sourceBlock"),
        "sinks" -> Block.Library("baseSinksBlock"),
      ),
      links = Map(
        "link0" -> Link.Library("link"),
        "link1" -> Link.Library("link"),
        "link2" -> Link.Library("link"),
      ),
      constraints = Map(
        "source0Connect" -> Constraint.Connected(Ref("source0", "port"), Ref("link0", "source")),
        "sink0Connect" -> Constraint.Connected(Ref.Allocate(Ref("sinks", "port")), Ref.Allocate(Ref("link0", "sinks"))),
        "source1Connect" -> Constraint.Connected(Ref("source1", "port"), Ref("link1", "source")),
        "sink1Connect" -> Constraint.Connected(Ref.Allocate(Ref("sinks", "port")), Ref.Allocate(Ref("link1", "sinks"))),
        // Also test with a suggested name - in this test because the block port array is abstract
        "source2Connect" -> Constraint.Connected(Ref("source2", "port"), Ref("link2", "source")),
        "sink2Connect" -> Constraint.Connected(Ref.Allocate(Ref("sinks", "port"), Some("named")),
          Ref.Allocate(Ref("link2", "sinks"))),
      )
    ))
    val referenceConstraints = Map(
      "source0Connect" -> Constraint.Connected(Ref("source0", "port"), Ref("link0", "source")),
      "sink0Connect" -> Constraint.Connected(Ref.Allocate(Ref("sinks", "port")), Ref("link0", "sinks", "0")),
      "source1Connect" -> Constraint.Connected(Ref("source1", "port"), Ref("link1", "source")),
      "sink1Connect" -> Constraint.Connected(Ref.Allocate(Ref("sinks", "port")), Ref("link1", "sinks", "0")),
      "source2Connect" -> Constraint.Connected(Ref("source2", "port"), Ref("link2", "source")),
      "sink2Connect" -> Constraint.Connected(Ref.Allocate(Ref("sinks", "port"), Some("named")),
        Ref("link2", "sinks", "0")),
    )
    // this will throw compiler errors, so we don't use the testCompile wrapper
    val compiler = new Compiler(inputDesign, new edg.wir.EdgirLibrary(library))
    val compiled = compiler.compile()

    compiler.getErrors() should not be empty

    compiled.contents.get.constraints should equal(referenceConstraints)

    compiler.getValue(IndirectDesignPath() + "sinks" + "port" + IndirectStep.Allocated) should
        equal(Some(ArrayValue(Seq(TextValue("0"), TextValue("1"), TextValue("named")))))

    val dsv = new DesignStructuralValidate()
    dsv.map(Design(compiled.contents.get)) should equal(Seq(
      CompilerError.UndefinedPortArray(DesignPath() + "sinks" + "port", LibraryPath("sinkPort")),
    ))

    val drv = new DesignRefsValidate()
    drv.validate(Design(compiled.contents.get)) should equal(Seq(
      CompilerError.BadRef(DesignPath() + "sink0Connect", IndirectDesignPath() + "sinks" + "port" + IndirectStep.Allocate()),
      CompilerError.BadRef(DesignPath() + "sink1Connect", IndirectDesignPath() + "sinks" + "port" + IndirectStep.Allocate()),
      CompilerError.BadRef(DesignPath() + "sink2Connect", IndirectDesignPath() + "sinks" + "port" + IndirectStep.Allocate(Some("named")))
    ))
  }

  "Compiler on design with concrete source and array sink" should "expand blocks" in {
    val inputDesign = Design(Block.Block("topDesign",
      blocks = Map(
        "source0" -> Block.Library("sourceBlock"),
        "source1" -> Block.Library("sourceBlock"),
        "sinks" -> Block.Library("concreteSinksBlock"),
      ),
      links = Map(
        "link0" -> Link.Library("link"),
        "link1" -> Link.Library("link"),
      ),
      constraints = Map(
        "source0Connect" -> Constraint.Connected(Ref("source0", "port"), Ref("link0", "source")),
        "sink0Connect" -> Constraint.Connected(Ref.Allocate(Ref("sinks", "port")), Ref.Allocate(Ref("link0", "sinks"))),
        "source1Connect" -> Constraint.Connected(Ref("source1", "port"), Ref("link1", "source")),
        "sink1Connect" -> Constraint.Connected(Ref.Allocate(Ref("sinks", "port")), Ref.Allocate(Ref("link1", "sinks"))),
      )
    ))
    val referenceConstraints = Map(
      "source0Connect" -> Constraint.Connected(Ref("source0", "port"), Ref("link0", "source")),
      "sink0Connect" -> Constraint.Connected(Ref("sinks", "port", "0"), Ref("link0", "sinks", "0")),
      "source1Connect" -> Constraint.Connected(Ref("source1", "port"), Ref("link1", "source")),
      "sink1Connect" -> Constraint.Connected(Ref("sinks", "port", "1"), Ref("link1", "sinks", "0")),
    )
    val (compiler, compiled) = testCompile(inputDesign, library)

    val dsv = new DesignStructuralValidate()
    dsv.map(Design(compiled.contents.get)) should equal(Seq())

    val drv = new DesignRefsValidate()
    drv.validate(Design(compiled.contents.get)) should equal(Seq())

    compiled.contents.get.constraints should equal(referenceConstraints)

    compiler.getValue(IndirectDesignPath() + "sinks" + "port" + IndirectStep.Length) should
        equal(Some(IntValue(2)))
    compiler.getValue(IndirectDesignPath() + "sinks" + "port" + IndirectStep.Elements) should
        equal(Some(ArrayValue(Seq(TextValue("0"), TextValue("1")))))

    compiler.getValue(IndirectDesignPath() + "sinks" + "port" + "0" + IndirectStep.IsConnected) should
        equal(Some(BooleanValue(true)))
    compiler.getValue(IndirectDesignPath() + "sinks" + "port" + "1" + IndirectStep.IsConnected) should
        equal(Some(BooleanValue(true)))
  }

  "Compiler on design with nested sink" should "expand across levels of hierarchy" in {
    val inputDesign = Design(Block.Block("topDesign",
      blocks = Map(
        "source0" -> Block.Library("sourceBlock"),
        "source1" -> Block.Library("sourceBlock"),
        "sinks" -> Block.Library("concreteWrapperBlock"),
      ),
      links = Map(
        "link0" -> Link.Library("link"),
        "link1" -> Link.Library("link"),
      ),
      constraints = Map(
        "source0Connect" -> Constraint.Connected(Ref("source0", "port"), Ref("link0", "source")),
        "sink0Connect" -> Constraint.Connected(Ref.Allocate(Ref("sinks", "port")), Ref.Allocate(Ref("link0", "sinks"))),
        "source1Connect" -> Constraint.Connected(Ref("source1", "port"), Ref("link1", "source")),
        "sink1Connect" -> Constraint.Connected(Ref.Allocate(Ref("sinks", "port")), Ref.Allocate(Ref("link1", "sinks"))),
      )
    ))
    val referenceConstraints = Map(
      "source0Connect" -> Constraint.Connected(Ref("source0", "port"), Ref("link0", "source")),
      "sink0Connect" -> Constraint.Connected(Ref("sinks", "port", "0"), Ref("link0", "sinks", "0")),
      "source1Connect" -> Constraint.Connected(Ref("source1", "port"), Ref("link1", "source")),
      "sink1Connect" -> Constraint.Connected(Ref("sinks", "port", "1"), Ref("link1", "sinks", "0")),
    )
    val (compiler, compiled) = testCompile(inputDesign, library)

    val dsv = new DesignStructuralValidate()
    dsv.map(Design(compiled.contents.get)) should equal(Seq())

    val drv = new DesignRefsValidate()
    drv.validate(Design(compiled.contents.get)) should equal(Seq())

    compiled.contents.get.constraints should equal(referenceConstraints)

    compiler.getValue(IndirectDesignPath() + "sinks" + "port" + IndirectStep.Length) should
        equal(Some(IntValue(2)))
    compiler.getValue(IndirectDesignPath() + "sinks" + "port" + IndirectStep.Elements) should
        equal(Some(ArrayValue(Seq(TextValue("0"), TextValue("1")))))

    compiler.getValue(IndirectDesignPath() + "sinks" + "inner" + "port" + IndirectStep.Length) should
        equal(Some(IntValue(2)))
    compiler.getValue(IndirectDesignPath() + "sinks" + "inner" + "port" + IndirectStep.Elements) should
        equal(Some(ArrayValue(Seq(TextValue("0"), TextValue("1")))))

    compiler.getValue(IndirectDesignPath() + "sinks" + "port" + "0" + IndirectStep.IsConnected) should
        equal(Some(BooleanValue(true)))
    compiler.getValue(IndirectDesignPath() + "sinks" + "port" + "1" + IndirectStep.IsConnected) should
        equal(Some(BooleanValue(true)))
    compiler.getValue(IndirectDesignPath() + "sinks" + "inner" + "port" + "0" + IndirectStep.IsConnected) should
        equal(Some(BooleanValue(true)))
    compiler.getValue(IndirectDesignPath() + "sinks" + "inner" + "port" + "1" + IndirectStep.IsConnected) should
        equal(Some(BooleanValue(true)))
  }

  "Compiler on design with partially connected ports" should "work" in {
    val inputDesign = Design(Block.Block("topDesign",
      blocks = Map(
        "source0" -> Block.Library("sourceBlock"),
        "sinks" -> Block.Library("concreteSinksBlock"),
      ),
      links = Map(
        "link0" -> Link.Library("link"),
        "link1" -> Link.Library("link"),
      ),
      constraints = Map(
        "source0Connect" -> Constraint.Connected(Ref("source0", "port"), Ref("link0", "source")),
        "sink0Connect" -> Constraint.Connected(Ref.Allocate(Ref("sinks", "port")), Ref.Allocate(Ref("link0", "sinks"))),
      )
    ))
    val referenceConstraints = Map(
      "source0Connect" -> Constraint.Connected(Ref("source0", "port"), Ref("link0", "source")),
      "sink0Connect" -> Constraint.Connected(Ref("sinks", "port", "0"), Ref("link0", "sinks", "0")),
    )
    val (compiler, compiled) = testCompile(inputDesign, library)

    val dsv = new DesignStructuralValidate()
    dsv.map(Design(compiled.contents.get)) should equal(Seq())

    val drv = new DesignRefsValidate()
    drv.validate(Design(compiled.contents.get)) should equal(Seq())

    compiled.contents.get.constraints should equal(referenceConstraints)

    compiler.getValue(IndirectDesignPath() + "sinks" + "port" + IndirectStep.Length) should
        equal(Some(IntValue(2)))
    compiler.getValue(IndirectDesignPath() + "sinks" + "port" + IndirectStep.Elements) should
        equal(Some(ArrayValue(Seq(TextValue("0"), TextValue("1")))))

    compiler.getValue(IndirectDesignPath() + "sinks" + "port" + "0" + IndirectStep.IsConnected) should
        equal(Some(BooleanValue(true)))
    compiler.getValue(IndirectDesignPath() + "sinks" + "port" + "1" + IndirectStep.IsConnected) should
        equal(Some(BooleanValue(false)))
  }

  "Compiler on design with empty nested sink" should "not fail" in {
    val inputDesign = Design(Block.Block("topDesign",
      blocks = Map(
        "sinks" -> Block.Library("emptyWrapperBlock"),
      ),
      links = Map(),
      constraints = Map()
    ))
    val (compiler, compiled) = testCompile(inputDesign, library)

    val dsv = new DesignStructuralValidate()
    dsv.map(Design(compiled.contents.get)) should equal(Seq())

    val drv = new DesignRefsValidate()
    drv.validate(Design(compiled.contents.get)) should equal(Seq())

    compiled.contents.get.constraints shouldBe empty
  }
}
