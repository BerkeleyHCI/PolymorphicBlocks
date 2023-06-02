package edg.compiler

import org.scalatest._
import org.scalatest.flatspec.AnyFlatSpec
import matchers.should.Matchers._
import edg.ElemBuilder._
import edg.ExprBuilder._
import edg.wir.DesignPath

import scala.collection.SeqMap

class DesignStructuralValidateTest extends AnyFlatSpec {
  behavior.of("DesignStructuralValidate")

  it should "return no errors on a elaborated design" in {
    val dsv = new DesignStructuralValidate()
    val dut = Design(Block.Block(
      "topDesign",
      blocks = SeqMap(
        "source" -> Block.Block(
          selfClass = "sourceContainerBlock",
          ports = SeqMap(
            "port" -> Port.Port(selfClass = "sourcePort"),
          ),
          blocks = SeqMap(
            "inner" -> Block.Block(
              selfClass = "sourceBlock",
              ports = SeqMap(
                "port" -> Port.Port(selfClass = "sourcePort"),
              )
            )
          ),
          constraints = SeqMap(
            "export" -> Constraint.Exported(Ref("port"), Ref("inner", "port"))
          )
        ),
        "sink" -> Block.Block(
          selfClass = "sinkContainerBlock",
          ports = SeqMap(
            "port" -> Port.Port(selfClass = "sinkPort"),
          ),
          blocks = SeqMap(
            "inner" -> Block.Block(
              selfClass = "sinkBlock",
              ports = SeqMap(
                "port" -> Port.Port(selfClass = "sinkPort"),
              )
            )
          ),
          constraints = SeqMap(
            "export" -> Constraint.Exported(Ref("port"), Ref("inner", "port"))
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
        )
      ),
      constraints = SeqMap(
        "sourceConnect" -> Constraint.Connected(Ref("source", "port"), Ref("link", "source")),
        "sinkConnect" -> Constraint.Connected(Ref("sink", "port"), Ref("link", "sink")),
      )
    ))
    dsv.map(dut) should equal(Seq())
  }

  it should "return errors on block libraries" in {
    val dsv = new DesignStructuralValidate()
    val dut = Design(Block.Block(
      "topDesign",
      blocks = SeqMap(
        "test" -> Block.Library("testBlock"),
      )
    ))
    dsv.map(dut) should equal(Seq(
      CompilerError.LibraryElement(DesignPath() + "test", LibraryPath("testBlock")),
    ))
  }

  it should "return errors on port and link libraries" in {
    val dsv = new DesignStructuralValidate()
    val dut = Design(Block.Block(
      "topDesign",
      blocks = SeqMap(
        "test" -> Block.Block(
          selfClass = "testBlock",
          ports = SeqMap(
            "port" -> Port.Library("testPort"),
          ),
          links = SeqMap(
            "link" -> Link.Library("testLink"),
          ),
        ),
      )
    ))
    dsv.map(dut) should equal(Seq(
      CompilerError.LibraryElement(DesignPath() + "test" + "port", LibraryPath("testPort")),
      CompilerError.LibraryElement(DesignPath() + "test" + "link", LibraryPath("testLink")),
    ))
  }
}
