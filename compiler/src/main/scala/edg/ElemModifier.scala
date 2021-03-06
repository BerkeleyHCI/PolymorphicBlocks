package edg

import edg.schema.schema
import edg.elem.elem

/** Functions for making small changes to IR trees.
  * Note that these may copy significant parts of the tree. Instead of calling these methods many times,
  * consider instead using a intermediate mutable data structure, like the wir classes.
  */
object ElemModifier {
  /** Returns a copy of the design tree, with fn applied to the block at path.
    * Errors out if path does not resolve to a block.
    */
//  def modifyBlock(path: wir.DesignPath, fn: elem.HierarchyBlock => elem.HierarchyBlock,
//                  design: schema.Design): schema.Design = {
//
//  }
}
