package edg.util

import edg.elem.elem
import scala.collection.mutable


object NameCreator {
  def fromBlock(block: elem.HierarchyBlock): NameCreator = {
    new NameCreator(block.blocks.keySet ++ block.ports.keySet ++ block.links.keySet ++
        block.params.keySet ++ block.constraints.keySet)
  }
}


/** A class that returns new (unique) names.
  * Tracks new names returned to avoid returning duplicates on subsequent calls. Stateful.
  */
class NameCreator(initialNames: Set[String]) {
  private val names: mutable.Set[String] = initialNames.to(mutable.Set)

  def newName(prefix: String): String = {
    if (!names.contains(prefix)) {
      names += prefix
      prefix
    } else {  // need to add numbers
      var i: Int = 2
      while (names.contains(s"$prefix$i")) {
        i = i + 1
      }
      val name = s"$prefix$i"
      require(!names.contains(name))
      names += name
      name
    }
  }
}
