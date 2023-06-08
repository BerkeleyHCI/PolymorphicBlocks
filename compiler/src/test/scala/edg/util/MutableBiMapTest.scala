package edg.util

import org.scalatest._
import org.scalatest.flatspec.AnyFlatSpec
import matchers.should.Matchers._

class MutableBiMapTest extends AnyFlatSpec {
  behavior.of("MutableBiMap")

  it should "return None on nonexistent value" in {
    val biMap = MutableBiMap[Int]()
    biMap.get(1) should equal(None)
  }

  it should "insert and get by key" in {
    val biMap = MutableBiMap[Int]()
    biMap.put(1, 11)
    biMap.put(2, 22)
    biMap.get(1) should equal(Some(11))
    biMap.get(2) should equal(Some(22))
  }

  it should "insert and get in reverse" in {
    val biMap = MutableBiMap[Int]()
    biMap.put(1, 11)
    biMap.put(2, 22)
    biMap.get(11) should equal(Some(1))
    biMap.get(22) should equal(Some(2))
  }

  it should "insert and remove by key" in {
    val biMap = MutableBiMap[Int]()
    biMap.put(1, 11)
    biMap.put(2, 22)
    biMap.remove(11) should equal(Some(1))
    biMap.get(1) should equal(None)
    biMap.get(11) should equal(None)
    biMap.get(2) should equal(Some(22))
    biMap.get(22) should equal(Some(2))
    biMap.remove(22) should equal(Some(2))
    biMap.get(2) should equal(None)
    biMap.get(22) should equal(None)
  }

  it should "insert and remove in reverse" in {
    val biMap = MutableBiMap[Int]()
    biMap.put(1, 11)
    biMap.put(2, 22)
    biMap.remove(1) should equal(Some(11))
    biMap.get(1) should equal(None)
    biMap.get(11) should equal(None)
    biMap.get(2) should equal(Some(22))
    biMap.get(22) should equal(Some(2))
    biMap.remove(2) should equal(Some(22))
    biMap.get(2) should equal(None)
    biMap.get(22) should equal(None)
  }
}
