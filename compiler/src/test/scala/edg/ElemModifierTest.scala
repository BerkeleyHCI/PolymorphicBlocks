package edg

import edg.ElemBuilder._
import edg.wir.DesignPath
import edg.wir.ProtoUtil._
import edgir.schema.schema
import org.scalatest._
import org.scalatest.flatspec.AnyFlatSpec
import org.scalatest.matchers.should.Matchers._

import scala.collection.SeqMap


class ElemModifierTest extends AnyFlatSpec {
  behavior of "ElemModifier"

  val design: schema.Design = Design(Block.Block("topDesign",
    blocks = SeqMap(
      "inner" -> Block.Block(selfClass="original")
    )
  ).getHierarchy)

  it should "be able to add blocks in design root" in {
    val inserted = Block.Block(selfClass="new")
    val transformed = ElemModifier.modifyBlock(DesignPath(), design) { block =>
      block.update(
        _.blocks :+= ("testInserted", inserted).toPb
      )
    }
    transformed.getContents.blocks("testInserted") should equal(inserted)
    // make sure it didn't touch the original one
    transformed.getContents.blocks("inner") should equal(design.getContents.blocks("inner"))
  }

  it should "be able to add blocks in nested blocks" in {
    val inserted = Block.Block(selfClass="new")
    val transformed = ElemModifier.modifyBlock(DesignPath() + "inner", design) { block =>
      block.update(
        _.blocks :+= ("innerInserted", inserted).toPb
      )
    }
    transformed.getContents.blocks("inner").getHierarchy.blocks("innerInserted") should equal(inserted)
    transformed.getContents.blocks("inner").getHierarchy.getSelfClass should equal(
      design.getContents.blocks("inner").getHierarchy.getSelfClass)
  }
}
