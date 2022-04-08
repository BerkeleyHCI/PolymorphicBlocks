package edg.compiler

import edg.CompilerTestUtil
import edg.ElemBuilder._
import edg.ExprBuilder.Ref
import edg.wir.{DesignPath, IndirectDesignPath, IndirectStep}
import org.scalatest.flatspec.AnyFlatSpec
import org.scalatest.matchers.should.Matchers._


/** Tests compiler LinkArray expansion / elaboration and connected constraint allocation with block-side PortArray.
  * TODO: deduplicate libraries w/ block port array tests?
  */
class CompilerLinkArrayExpansionTest extends AnyFlatSpec with CompilerTestUtil {
  val library = Library(
    ports = Seq(
      Port.Port("sourcePort"),
      Port.Port("sinkPort"),
    ),
    blocks = Seq(
      Block.Block("sourceBlock",  // array elements source
        ports = Map(
          "port" -> Port.Array("sourcePort", 3, Port.Library("sinkPort")),
        )
      ),
      Block.Block("sinkBlock",  // array elements sink
        ports = Map(
          "port" -> Port.Array("sinkPort"),
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
        "source" -> Block.Library("sourceBlock"),
        "sink0" -> Block.Library("sinkBlock"),
        "sink1" -> Block.Library("sinkBlock"),
      ),
      links = Map(
        "link" -> Link.Array("link"),
      ),
      constraints = Map(
        "sourceConnect" -> Constraint.ConnectedArray(Ref("source", "port"), Ref("link", "source")),
//        "sink0Connect" -> Constraint.ConnectedArray(Ref("sink0", "port"), Ref.Allocate(Ref("link", "sinks"))),
//        "sink1Connect" -> Constraint.ConnectedArray(Ref("sink1", "port"), Ref.Allocate(Ref("link", "sinks"))),
      )
    ))
    val referenceConstraints = Map(  // expected constraints in the top-level design
      "sourceConnect.0" -> Constraint.Connected(Ref("source", "port", "0"), Ref("link", "source", "0")),
      "sourceConnect.1" -> Constraint.Connected(Ref("source", "port", "1"), Ref("link", "source", "1")),

//      "sink0Connect.0" -> Constraint.Connected(Ref("sink0", "port", "0"), Ref("link", "sinks", "0", "0")),
//      "sink0Connect.1" -> Constraint.Connected(Ref("sink0", "port", "1"), Ref("link", "sinks", "0", "1")),
//      "sink1Connect.0" -> Constraint.Connected(Ref("sink1", "port", "0"), Ref("link", "sinks", "1", "0")),
//      "sink1Connect.1" -> Constraint.Connected(Ref("sink1", "port", "1"), Ref("link", "sinks", "1", "1")),
    )
    val referenceLinkArrayConstraints = Map(  // expected constraints in the link array
      "source.0" -> Constraint.Exported(Ref("source", "0"), Ref("0", "source")),
      "source.1" -> Constraint.Exported(Ref("source", "1"), Ref("1", "source")),

//      "sink.0.0" -> Constraint.Exported(Ref("sinks", "0", "0"), Ref("0", "sinks", "0")),
//      "sink.0.1" -> Constraint.Exported(Ref("sinks", "0", "1"), Ref("1", "sinks", "0")),
//      "sink.1.0" -> Constraint.Exported(Ref("sinks", "1", "0"), Ref("0", "sinks", "1")),
//      "sink.1.0" -> Constraint.Exported(Ref("sinks", "1", "1"), Ref("1", "sinks", "1")),
    )

    val (compiler, compiled) = testCompile(inputDesign, library)

    val dsv = new DesignStructuralValidate()
    dsv.map(Design(compiled.contents.get)) should equal(Seq())

    val drv = new DesignRefsValidate()
    drv.validate(Design(compiled.contents.get)) should equal(Seq())

    compiled.contents.get.constraints should equal(referenceConstraints)
  }
}
