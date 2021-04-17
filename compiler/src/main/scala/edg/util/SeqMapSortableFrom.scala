package edg.util

import scala.collection.SeqMap


object SeqMapSortableFrom {
  implicit class MapSortableFrom[K, V](map: Map[K, V]) {
    def sortKeysFrom(order: Seq[K]): SeqMap[K, V] = {
      val sortedSeq = order.flatMap(key => map.get(key).map(key -> _)) ++
          map.toSeq.filter { case (key, value) => !order.contains(key) }
      SeqMap(sortedSeq:_*)
    }
  }
}
