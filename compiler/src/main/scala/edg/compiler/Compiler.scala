package edg.compiler

import scala.collection.mutable
import edg.schema.schema
import edg.wir.DesignPath
import edg.wir


/** Compiler for a particular design, with an associated library to elaborate references from.
  * TODO also needs a Python interface for generators, somewhere.
  *
  * During the compilation process, internal data structures are mutated.
  */
class Compiler(inputDesignPb: schema.Design, library: edg.wir.Library) {
  private val pending = mutable.Set[DesignPath]()  // block-likes pending elaboration
  private val constProp = new ConstProp()

  // Seed compilation with the root
  //
  private val root = wir.Block(inputDesignPb.contents.get)
  def getBlock(path: DesignPath): wir.Block = root.resolve(path.steps).asInstanceOf[wir.Block]
  def getLink(path: DesignPath): wir.Link = root.resolve(path.steps).asInstanceOf[wir.Link]

  for (rootBlockName <- root.pb.blocks.keys) {
    pending += DesignPath.root + rootBlockName
  }
  for (rootLinkName <- root.pb.links.keys) {
    pending += DesignPath.root + rootLinkName
  }


  /** Elaborate the unelaborated block at path (but where the parent has been elaborated and is reachable from root),
    * and adds it to the parent and replaces the lib_elem proto entry with a placeholder unknown.
    * Adds children to the pending queue, and adds constraints to constProp.
    */
  protected def elaborateBlock(path: DesignPath): Unit = {
    val parent = getBlock(path.parent)

  }

  /** Elaborate the unelaborated link at path (but where the parent has been elaborated and is reachable from root),
    * and adds it to the parent and replaces the lib_elem proto entry with a placeholder unknown.
    * Adds children to the pending queue, and adds constraints to constProp.
    */
  protected def elaborateLink(path: DesignPath): Unit = {

  }

  /** Performs full compilation and returns the resulting design. Might take a while.
    */
  def compile(): schema.Design = {

  }
}
