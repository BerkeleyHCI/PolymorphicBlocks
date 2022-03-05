package edg.util
import scala.collection.mutable

/** A HashMap where entries can be written only once.
  */
class SingleWriteHashMap[K, V] {
  protected val map = mutable.HashMap[K, V]()

  def apply(key: K): V = map(key)

  def get(key: K): Option[V] = map.get(key)

  def put(key: K, value: V): Unit = {
    require(!map.contains(key), s"repeated put for key $key with existing value ${map(key)} and new value $value")
    map.put(key, value)
  }
}

object SingleWriteHashMap {
  def apply[K, V](): SingleWriteHashMap[K, V] = new SingleWriteHashMap[K, V]()
}
