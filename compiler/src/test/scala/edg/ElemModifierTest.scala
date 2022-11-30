package edg

import org.scalatest._
import org.scalatest.flatspec.AnyFlatSpec
import matchers.should.Matchers._
import edgir.schema.schema
import edgir.elem.elem
import edg.ElemBuilder._
import edg.wir.DesignPath
import edg.wir.ProtoUtil.BlockProtoToSeqMap

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
        _.blocks :+= elem.NamedBlockLike("testInserted", Some(inserted))
      )
    }
    transformed.getContents.blocks.toSeqMap("testInserted") should equal(inserted)
    // make sure it didn't touch the original one
    transformed.getContents.blocks.toSeqMap("inner") should equal(design.getContents.blocks.toSeqMap("inner"))
  }

  it should "be able to add blocks in nested blocks" in {
    val inserted = Block.Block(selfClass="new")
    val transformed = ElemModifier.modifyBlock(DesignPath() + "inner", design) { block =>
      block.update(
        _.blocks :+= elem.NamedBlockLike("innerInserted", Some(inserted))
      )
    }
    transformed.getContents.blocks.toSeqMap("inner").getHierarchy.blocks.toSeqMap("innerInserted") should equal(inserted)
    transformed.getContents.blocks.toSeqMap("inner").getHierarchy.getSelfClass should equal(
      design.getContents.blocks.toSeqMap("inner").getHierarchy.getSelfClass)
  }
}
