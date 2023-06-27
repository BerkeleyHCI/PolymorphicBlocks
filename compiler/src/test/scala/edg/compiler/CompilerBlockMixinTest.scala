package edg.compiler

import edg.CompilerTestUtil
import edg.ElemBuilder._
import edg.ExprBuilder.Ref
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
        "mixinBaseBlock",
        isAbstract = true,
        ports = SeqMap(
          "port" -> Port.Library("sinkPort"),
        )
      ),
      Block.Block(
        "mixin",
        superclasses = Seq("mixinBaseBlock"),
        isAbstract = true,
        ports = SeqMap(
          "mixinPort" -> Port.Library("sinkPort"),
        )
      ),
      Block.Block(
        "concreteMixinBlock",
        superclasses = Seq("mixinBaseBlock", "mixin"),
        ports = SeqMap(
          "port" -> Port.Library("sinkPort"),
          "mixinPort" -> Port.Library("sinkPort"),
        )
      ),
    ),
  )

  "Compiler on design with mixin" should "expand blocks" in {
    val inputDesign = Design(Block.Block(
      "topDesign",
      blocks = SeqMap(
        "source" -> Block.Library("sourceBlock"),
        "mixinSource" -> Block.Library("sourceBlock"),
        "block" -> Block.Library("mixinBaseBlock", mixins = Seq("mixin")),
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
          selfClass = "mixinBaseBlock",
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
      CompilerError.AbstractBlock(new DesignPath(Seq("block")), LibraryPath("mixinBaseBlock"))
    ))
    compiled should equal(referenceElaborated)
  }

  "Compiler on design with refined mixin" should "expand blocks" in {
    val inputDesign = Design(Block.Block(
      "topDesign",
      blocks = SeqMap(
        "source" -> Block.Library("sourceBlock"),
        "mixinSource" -> Block.Library("sourceBlock"),
        "block" -> Block.Library("mixinBaseBlock", mixins = Seq("mixin")),
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
          selfClass = "mixinBaseBlock",
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
