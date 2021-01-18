package edg.compiler

import org.scalatest._
import org.scalatest.flatspec.AnyFlatSpec
import matchers.should.Matchers._
import edg.ElemBuilder._
import edg.ExprBuilder.Ref
import edg.wir


/** Tests compiler PortArray expansion / elaboration and connected constraint allocation with link-side PortArray only.
  * Not dependent on generators or parameter propagation.
  */
class CompilerPortArrayExpansionTest extends AnyFlatSpec {
  val library = Library(
    ports = Map(
      "sourcePort" -> Port.Port(),
      "sinkPort" -> Port.Port(),
    ),
    blocks = Map(
      "sourceBlock" -> Block.Block(
        ports = Map(
          "port" -> Port.Library("sourcePort"),
        )
      ),
      "sinkBlock" -> Block.Block(
        ports = Map(
          "port" -> Port.Library("sinkPort"),
        )
      ),
      "sourceContainerBlock" -> Block.Block(
        ports = Map(
          "port" -> Port.Library("sourcePort"),
        ),
        blocks = Map(
          "inner" -> Block.Library("sourceBlock")
        ),
        constraints = Map(
          "export" -> Constraint.Exported(Ref("port"), Ref("inner", "port"))
        )
      ),
      "sinkContainerBlock" -> Block.Block(
        ports = Map(
          "port" -> Port.Library("sinkPort"),
        ),
        blocks = Map(
          "inner" -> Block.Library("sinkBlock")
        ),
        constraints = Map(
          "export" -> Constraint.Exported(Ref("port"), Ref("inner", "port"))
        )
      ),
    ),
    links = Map(
      "link" -> Link.Link(
        ports = Map(
          "source" -> Port.Library("sourcePort"),
          "sink" -> Port.Library("sinkPort"),
        )
      ),
    )
  )

  "Compiler on design with source and array sink" should "expand blocks" in {

  }
}