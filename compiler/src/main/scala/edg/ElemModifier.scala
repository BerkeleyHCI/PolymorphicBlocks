package edg

import edg.wir.ProtoUtil.BlockProtoToSeqMap
import edgir.schema.schema
import edgir.elem.elem


/** Functions for making small changes to IR trees.
  * Note that these may copy significant parts of the tree. Instead of calling these methods many times,
  * consider instead using a intermediate mutable data structure, like the wir classes.
  */
object ElemModifier {
  class ElemModifyResolutionError(msg: String) extends Exception(msg)  // unable to resolve path

  /** Returns a copy of the design tree, with fn applied to the block at path.
    * Errors out if path does not resolve to a block.
    */
  def modifyBlock(path: wir.DesignPath, design: schema.Design)
                 (fn: elem.HierarchyBlock => elem.HierarchyBlock): schema.Design = {
    design.update(
      _.contents := transformBlock(Seq(), path.steps, design.contents.get, fn)
    )
  }

  private def transformBlock(prefix: Seq[String], postfix: Seq[String], curr: elem.HierarchyBlock,
                             fn: elem.HierarchyBlock => elem.HierarchyBlock): elem.HierarchyBlock = {
    postfix match {
      case Seq() =>
        fn(curr)
      case Seq(head, tail @ _*) =>
        val blocks = curr.blocks.toSeqMap
        blocks.get(head) match {
          case Some(headBlock) => headBlock.`type` match {
            case elem.BlockLike.Type.Hierarchy(headBlock) =>
              curr.update(
                _.blocks(head).hierarchy := transformBlock(prefix :+ head, tail, headBlock, fn)
              )
            case other =>
              throw new ElemModifyResolutionError(s"unexpected ${other.getClass} at ${(prefix :+ head).mkString(", ")}")
          }
          case None => throw new ElemModifyResolutionError(s"can't find next $head at ${prefix.mkString(", ")}")
        }
    }
  }
}
