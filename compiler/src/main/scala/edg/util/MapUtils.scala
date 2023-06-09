package edg.util

import scala.collection.SeqMap

object MapUtils {

  /** Merges the argument maps, erroring out if there are duplicate names
    */
  def mergeSeqMapSafe[K, V](maps: SeqMap[K, V]*): SeqMap[K, V] = {
    val allKeys = maps.flatMap(_.keys)
    require(allKeys.distinct == allKeys, "maps containing members with duplicate keys")
    maps.flatten.to(SeqMap)
  }

  def mergeMapSafe[K, V](maps: Map[K, V]*): Map[K, V] = {
    val allKeys = maps.flatMap(_.keys)
    require(allKeys.distinct == allKeys, "maps containing members with duplicate keys")
    maps.flatten.toMap
  }
}
