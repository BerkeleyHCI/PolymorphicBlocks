package edg.util

import org.scalatest._
import org.scalatest.flatspec.AnyFlatSpec
import org.scalatest.matchers.should.Matchers._


class SingleWriteHashMapTest extends AnyFlatSpec {
  behavior of "SingleWriteHashMap"

  it should "return None on nonexistent value" in {
    val map = SingleWriteHashMap[Int, Int]()
    map.get(1) should equal(None)
    assertThrows[NoSuchElementException] {
      map(1)
    }
  }

  it should "put and get by key" in {
    val map = SingleWriteHashMap[Int, Int]()
    map.put(1, 11)
    map.put(2, 22)
    map.get(1) should equal(Some(11))
    map(1) should equal(11)
    map.get(2) should equal(Some(22))
    map(2) should equal(22)
    map.get(1) should equal(Some(11))
    map(1) should equal(11)
  }

  it should "disallow repeated puts" in {
    val map = SingleWriteHashMap[Int, Int]()
    map.put(1, 11)
    assertThrows[IllegalArgumentException] {
      map.put(1, 11)
    }
  }
}
