package edg.util

import scala.collection.mutable

/** Mutable bidirectional map, abstractly a set of pairs of types (K1, K2) which can be indexed by either. Implemented
  * internally with mutable HashMaps.
  */
class MutableBiMap[KeyType] {
  private val fwdMap = mutable.HashMap[KeyType, KeyType]()
  private val bwdMap = mutable.HashMap[KeyType, KeyType]()

  def put(key: KeyType, value: KeyType): Unit = {
    require(!fwdMap.isDefinedAt(key))
    require(!bwdMap.isDefinedAt(value))
    fwdMap.put(key, value)
    bwdMap.put(value, key)
  }

  def get(key: KeyType): Option[KeyType] = {
    (fwdMap.get(key), bwdMap.get(key)) match {
      case (Some(fwdValue), Some(bwdValue)) =>
        require(fwdValue == bwdValue)
        Some(fwdValue)
      case (Some(fwdValue), _) => Some(fwdValue)
      case (None, Some(bwdValue)) => Some(bwdValue)
      case (None, None) => None
    }
  }

  def apply(key: KeyType): KeyType = get(key).get

  def remove(key: KeyType): Option[KeyType] = {
    (fwdMap.get(key), bwdMap.get(key)) match {
      case (Some(fwdValue), Some(bwdValue)) =>
        require(fwdValue == bwdValue)
        bwdMap.remove(key).get // get as an assertion that the other value was removed
        Some(fwdMap.remove(key).get)
      case (Some(fwdValue), _) =>
        bwdMap.remove(fwdValue).get
        Some(fwdMap.remove(key).get)
      case (None, Some(bwdValue)) =>
        fwdMap.remove(bwdValue).get
        Some(bwdMap.remove(key).get)
      case (None, None) => None
    }
  }
}

object MutableBiMap {
  def apply[T](): MutableBiMap[T] = new MutableBiMap[T]
}
