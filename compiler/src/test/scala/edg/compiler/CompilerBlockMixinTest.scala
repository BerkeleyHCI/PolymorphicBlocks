package edg.compiler

import edg.CompilerTestUtil
import edg.ElemBuilder._
import edg.ExprBuilder.Ref
import edg.wir.ProtoUtil.BlockProtoToSeqMap
import edg.wir.{DesignPath, EdgirLibrary, Refinements}
import org.scalatest._
import org.scalatest.flatspec.AnyFlatSpec
import org.scalatest.matchers.should.Matchers._

import scala.collection.SeqMap

/** Test for block expansion with mixins
  */
class CompilerBlockMixinTest extends AnyFlatSpec with CompilerTestUtil {
  val library = Library(
    base = CompilerExpansionTest.library,
    blocks = Seq(
      Block.Block(
        "baseBlock",
        isAbstract = true,
        ports = SeqMap(
          "port" -> Port.Library("sinkPort"),
        )
      ),
      Block.Block(
        "mixin",
        superclasses = Seq("baseBlock"),
        isAbstract = true,
        ports = SeqMap(
          "mixinPort" -> Port.Library("sinkPort"),
        )
      ),
      Block.Block(
        "concreteBaseBlock",
        superclasses = Seq("baseBlock"),
        ports = SeqMap(
          "port" -> Port.Library("sinkPort"),
        )
      ),
      Block.Block(
        "concreteMixinBlock",
        superclasses = Seq("baseBlock", "mixin"),
        ports = SeqMap(
          "port" -> Port.Library("sinkPort"),
          "mixinPort" -> Port.Library("sinkPort"),
        )
      ),
    ),
  )

  val inputDesign = Design(Block.Block(
    "topDesign",
    blocks = SeqMap(
      "source" -> Block.Library("sourceBlock"),
      "mixinSource" -> Block.Library("sourceBlock"),
      "block" -> Block.Library("baseBlock", mixins = Seq("mixin")),
    ),
    links = SeqMap(
      "link" -> Link.Library("link"),
      "mixinLink" -> Link.Library("link"),
    ),
    constraints = SeqMap(
      "sourceConnect" -> Constraint.Connected(Ref("source", "port"), Ref("link", "source")),
      "sinkConnect" -> Constraint.Connected(Ref("block", "port"), Ref("link", "sink")),
      "mixinSourceConnect" -> Constraint.Connected(Ref("mixinSource", "port"), Ref("mixinLink", "source")),
      "mixinSinkConnect" -> Constraint.Connected(Ref("block", "mixinPort"), Ref("mixinLink", "sink")),
    )
  ))

  "Compiler on design with abstract mixin" should "expand blocks and error" in {
    val referenceElaborated = Design(Block.Block(
      "topDesign",
      blocks = SeqMap(
        "source" -> Block.Block(
          selfClass = "sourceBlock",
          ports = SeqMap(
            "port" -> Port.Port(selfClass = "sourcePort"),
          )
        ),
        "mixinSource" -> Block.Block(
          selfClass = "sourceBlock",
          ports = SeqMap(
            "port" -> Port.Port(selfClass = "sourcePort"),
          )
        ),
        "block" -> Block.Block(
          selfClass = "baseBlock",
          isAbstract = true,
          ports = SeqMap(
            "port" -> Port.Port(selfClass = "sinkPort"),
            "mixinPort" -> Port.Port(selfClass = "sinkPort"),
          )
        ),
      ),
      links = SeqMap(
        "link" -> Link.Link(
          selfClass = "link",
          ports = SeqMap(
            "source" -> Port.Port(selfClass = "sourcePort"),
            "sink" -> Port.Port(selfClass = "sinkPort"),
          )
        ),
        "mixinLink" -> Link.Link(
          selfClass = "link",
          ports = SeqMap(
            "source" -> Port.Port(selfClass = "sourcePort"),
            "sink" -> Port.Port(selfClass = "sinkPort"),
          )
        ),
      ),
      constraints = SeqMap(
        "sourceConnect" -> Constraint.Connected(Ref("source", "port"), Ref("link", "source")),
        "sinkConnect" -> Constraint.Connected(Ref("block", "port"), Ref("link", "sink")),
        "mixinSourceConnect" -> Constraint.Connected(Ref("mixinSource", "port"), Ref("mixinLink", "source")),
        "mixinSinkConnect" -> Constraint.Connected(Ref("block", "mixinPort"), Ref("mixinLink", "sink")),
      )
    ))
    val compiler = new Compiler(inputDesign, new EdgirLibrary(library))
    val compiled = compiler.compile()
    compiler.getErrors() shouldBe empty
    new DesignStructuralValidate().map(compiled) should equal(Seq(
      CompilerError.AbstractBlock(new DesignPath(Seq("block")), LibraryPath("baseBlock"))
    ))
    compiled should equal(referenceElaborated)
  }

  "Compiler on design with invalid mixin refinement" should "error" in {
    // don't care about the output here, it's invalid
    val compiler = new Compiler(
      inputDesign,
      new EdgirLibrary(library),
      refinements = Refinements(
        instanceRefinements = Map(new DesignPath(Seq("block")) -> LibraryPath("concreteBaseBlock")),
      )
    )
    val compiled = compiler.compile()
    compiler.getErrors() should equal(Seq(
      CompilerError.RefinementSubclassError(
        new DesignPath(Seq("block")),
        LibraryPath("concreteBaseBlock"),
        LibraryPath("baseBlock")
      )
    ))
    new DesignStructuralValidate().map(compiled) shouldBe empty
    new DesignRefsValidate().validate(compiled) should not be empty // bad connection to mixinPort
    new DesignAssertionCheck(compiler).map(compiled) shouldBe empty
  }

  "Compiler on design with refined mixin" should "expand blocks" in {
    val referenceElaborated = Design(Block.Block(
      "topDesign",
      blocks = SeqMap(
        "source" -> Block.Block(
          selfClass = "sourceBlock",
          ports = SeqMap(
            "port" -> Port.Port(selfClass = "sourcePort"),
          )
        ),
        "mixinSource" -> Block.Block(
          selfClass = "sourceBlock",
          ports = SeqMap(
            "port" -> Port.Port(selfClass = "sourcePort"),
          )
        ),
        "block" -> Block.Block(
          superclasses = Seq("baseBlock", "mixin"),
          prerefine = "baseBlock",
          selfClass = "concreteMixinBlock",
          ports = SeqMap(
            "port" -> Port.Port(selfClass = "sinkPort"),
            "mixinPort" -> Port.Port(selfClass = "sinkPort"),
          )
        ),
      ),
      links = SeqMap(
        "link" -> Link.Link(
          selfClass = "link",
          ports = SeqMap(
            "source" -> Port.Port(selfClass = "sourcePort"),
            "sink" -> Port.Port(selfClass = "sinkPort"),
          )
        ),
        "mixinLink" -> Link.Link(
          selfClass = "link",
          ports = SeqMap(
            "source" -> Port.Port(selfClass = "sourcePort"),
            "sink" -> Port.Port(selfClass = "sinkPort"),
          )
        ),
      ),
      constraints = SeqMap(
        "sourceConnect" -> Constraint.Connected(Ref("source", "port"), Ref("link", "source")),
        "sinkConnect" -> Constraint.Connected(Ref("block", "port"), Ref("link", "sink")),
        "mixinSourceConnect" -> Constraint.Connected(Ref("mixinSource", "port"), Ref("mixinLink", "source")),
        "mixinSinkConnect" -> Constraint.Connected(Ref("block", "mixinPort"), Ref("mixinLink", "sink")),
      )
    ))

    // TODO DELETEME TESTING ONLY
    val compiler = new Compiler(
      inputDesign,
      new EdgirLibrary(library),
      refinements = Refinements(
        instanceRefinements = Map(new DesignPath(Seq("block")) -> LibraryPath("concreteMixinBlock")),
      )
    )
    val compiled = compiler.compile()
    compiled.getContents.blocks.get("block") should equal(referenceElaborated.getContents.blocks.get("block"))

    testCompile(
      inputDesign,
      library,
      refinements = Refinements(
        instanceRefinements = Map(new DesignPath(Seq("block")) -> LibraryPath("concreteMixinBlock")),
      ),
      expectedDesign = Some(referenceElaborated)
    )
  }
}
