package edg.util

import edg.wir.ProtoUtil.{BlockProtoToSeqMap, ConstraintProtoToSeqMap, LinkProtoToSeqMap, ParamProtoToSeqMap, PortProtoToSeqMap}

import scala.collection.mutable
import edgir.elem.elem


object NameCreator {
  def fromBlock(block: elem.HierarchyBlock): NameCreator = {
    new NameCreator((block.blocks.toSeqMap.keySet ++ block.ports.toSeqMap.keySet ++ block.links.toSeqMap.keySet ++
        block.params.toSeqMap.keySet ++ block.constraints.toSeqMap.keySet).toSet)
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
