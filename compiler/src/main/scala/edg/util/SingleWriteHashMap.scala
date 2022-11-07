package edg.util
import scala.collection.mutable

/** A HashMap where entries can be written only once.
  */
class SingleWriteHashMap[K, V] {
  protected val map = mutable.HashMap[K, V]()

  def apply(key: K): V = map(key)

  def get(key: K): Option[V] = map.get(key)

  def getOrElseUpdate(key: K, default: V): V = map.getOrElseUpdate(key, default)

  def contains(key: K): Boolean = map.contains(key)

  def put(key: K, value: V): Unit = {
    require(!map.contains(key), s"repeated put for key $key with existing value ${map(key)} and new value $value")
    map.put(key, value)
  }

  def addAll(that: SingleWriteHashMap[K, V]): Unit = {
    that.map.keys foreach { key =>
      require(!map.contains(key))
    }
    map.addAll(that.map)
  }
}

object SingleWriteHashMap {
  def apply[K, V](): SingleWriteHashMap[K, V] = new SingleWriteHashMap[K, V]()
}
