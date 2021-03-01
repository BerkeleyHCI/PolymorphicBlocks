package edg.wir

import edg.elem.elem
import edg.ref.ref


object DesignBlockAnalysis {
  /** Returns the link-side top-level port names and types of connected elements.
    * Local analysis only, does not guarantee these ultimately resolve to a block port (may be a dangling export).
    * Works on both fully expanded as well as non-expanded (with ALLOCATEs) designs.
    *
    * If linkName is invalid, returns empty.
    */
  def connectsToLink(block: elem.HierarchyBlock, linkName: String): Seq[(String, ref.LibraryPath)] = {

  }
}
