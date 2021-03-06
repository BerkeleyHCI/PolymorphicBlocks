package edg.wir

import org.scalatest._
import org.scalatest.flatspec.AnyFlatSpec
import matchers.should.Matchers._
import edg.ElemBuilder._
import edg.ExprBuilder.Ref
import edg.wir


class GeneratorMockupTest extends AnyFlatSpec {
  behavior of "Block"

  it should "dedup generator protos" in {
    val blockPb = Block.Block(
      ports = Map(
        "port" -> Port.Library("outerSourcePort"),
      )
    )
    val block = new wir.Block(blockPb.getHierarchy, Seq(LibraryPath("block")), None)

    val generatorExample = Block.Block(
      ports = Map(
        "port" -> Port.Library("outerSourcePort"),
      ),
      blocks = Map(
        "inner" -> Block.Library("sourceBlock"),
      ),
      constraints = Map(
        "export" -> Constraint.Exported(Ref("port"), Ref("inner", "port"))
      )
    )

    val expectedDiff = Block.Block(
      blocks = Map(
        "inner" -> Block.Library("sourceBlock"),
      ),
      constraints = Map(
        "export" -> Constraint.Exported(Ref("port"), Ref("inner", "port"))
      )
    )
    block.dedupGeneratorPb(generatorExample.getHierarchy) should equal(expectedDiff.getHierarchy)
  }

}
