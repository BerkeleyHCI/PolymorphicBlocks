package edg.util

import collection.mutable
import collection.SeqMap

object SeqMapUtils {

  /** Replaces an index in a mutable SeqMap with a SeqMap of values. TODO this could be a lot more efficient!
    */
  def replaceInPlace[K, V](map: mutable.SeqMap[K, V], index: K, values: Seq[(K, V)]): map.type = {
    val keys = map.keysIterator.toSeq
    val nameIndex = keys.indexOf(index)
    require(nameIndex >= 0, s"no $index in $map")
    val (_, post) = map.splitAt(nameIndex)
    for ((key, _) <- post) {
      map.remove(key)
    }
    post.remove(index) // drop index after the index has been deleted from map
    map ++= values ++= post
  }
}
