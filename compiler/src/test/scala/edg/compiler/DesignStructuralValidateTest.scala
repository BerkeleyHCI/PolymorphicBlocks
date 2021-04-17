package edg.compiler

import org.scalatest._
import org.scalatest.flatspec.AnyFlatSpec
import matchers.should.Matchers._
import edg.ElemBuilder._
import edg.ExprBuilder._
import edg.wir.DesignPath


class DesignStructuralValidateTest extends AnyFlatSpec {
  behavior of "DesignStructuralValidate"

  it should "return no errors on a elaborated design" in {
    val dsv = new DesignStructuralValidate()
    val dut = Design(Block.Block(
      blocks = Map(
        "source" -> Block.Block(superclass="sourceContainerBlock",
          ports = Map(
            "port" -> Port.Port(superclass="sourcePort"),
          ),
          blocks = Map(
            "inner" -> Block.Block(superclass="sourceBlock",
              ports = Map(
                "port" -> Port.Port(superclass="sourcePort"),
              )
            )
          ),
          constraints = Map(
            "export" -> Constraint.Exported(Ref("port"), Ref("inner", "port"))
          )
        ),
        "sink" -> Block.Block(superclass="sinkContainerBlock",
          ports = Map(
            "port" -> Port.Port(superclass="sinkPort"),
          ),
          blocks = Map(
            "inner" -> Block.Block(superclass="sinkBlock",
              ports = Map(
                "port" -> Port.Port(superclass="sinkPort"),
              )
            )
          ),
          constraints = Map(
            "export" -> Constraint.Exported(Ref("port"), Ref("inner", "port"))
          )
        ),
      ),
      links = Map(
        "link" -> Link.Link(superclass="link",
          ports = Map(
            "source" -> Port.Port(superclass="sourcePort"),
            "sink" -> Port.Port(superclass="sinkPort"),
          )
        )
      ),
      constraints = Map(
        "sourceConnect" -> Constraint.Connected(Ref("source", "port"), Ref("link", "source")),
        "sinkConnect" -> Constraint.Connected(Ref("sink", "port"), Ref("link", "sink")),
      )
    ))
    dsv.map(dut) should equal(Seq())
  }

  it should "return errors on block libraries" in {
    val dsv = new DesignStructuralValidate()
    val dut = Design(Block.Block(
      blocks = Map(
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
      blocks = Map(
        "test" -> Block.Block(superclass="testBlock",
          ports = Map(
            "port" -> Port.Library("testPort"),
          ),
          links = Map(
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
