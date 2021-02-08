package edg.util

import scala.collection.SeqMap


object SeqMapSortableFrom {
  implicit class MapSortableFrom[K, V](map: Map[K, V]) {
    def sortKeysFrom(order: Seq[K]): SeqMap[K, V] = {
      val sortedSeq = map.toSeq.sortWith { case ((k1, v1), (k2, v2)) => // true means _1 strictly before _2
        (order.indexOf(k1), order.indexOf(k2)) match {
          case (-1, _) | (_, -1) => false
          case (k1Index, k2Index) => k1Index < k2Index
        }
      }
      SeqMap(sortedSeq:_*)
    }
  }
}
