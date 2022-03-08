package edg.compiler

import edg.CompilerTestUtil
import edg.ElemBuilder._
import edg.ExprBuilder.{Ref, ValueExpr}
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
        "sink" -> Block.Library("baseSinksBlock"),
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

    compiled.contents.get.constraints should equal(referenceConstraints)

    // TODO This should expand but throw an error because the parts don't exist
  }

  "Compiler on design with concrete source and array sink" should "expand blocks" in {
    val inputDesign = Design(Block.Block("topDesign",
      blocks = Map(
        "source0" -> Block.Library("sourceBlock"),
        "source1" -> Block.Library("sourceBlock"),
        "sink" -> Block.Library("concreteSinksBlock"),
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

    compiled.contents.get.constraints should equal(referenceConstraints)
  }
}
