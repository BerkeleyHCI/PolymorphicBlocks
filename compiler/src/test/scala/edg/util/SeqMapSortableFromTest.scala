package edg.util

import edg.util.SeqMapSortableFrom._
import org.scalatest._
import org.scalatest.flatspec.AnyFlatSpec
import org.scalatest.matchers.should.Matchers._

import scala.collection.SeqMap


class SeqMapSortableFromTest extends AnyFlatSpec {
  behavior of "NamespaceSort"

  it should "preserve order on empty order" in {
    SeqMap(0 -> 0, 1 -> 1, 2 -> 2)
        .sortKeysFrom(Seq())
        .toSeq should equal(Seq((0, 0), (1, 1), (2, 2)))
  }

  it should "resort input map" in {
    SeqMap(0 -> 0, 1 -> 1, 2 -> 2)
        .sortKeysFrom(Seq(0, 1, 2))
        .toSeq should equal(Seq((0, 0), (1, 1), (2, 2)))
  }

  it should "resort input map, input reversed" in {
    SeqMap(0 -> 0, 1 -> 1, 2 -> 2)
        .sortKeysFrom(Seq(2, 1, 0))
        .toSeq should equal(Seq((2, 2), (1, 1), (0, 0)))
  }

  it should "resort input map, input reversed, ignoring extra name elements" in {
    SeqMap(0 -> 0, 1 -> 1, 2 -> 2)
        .sortKeysFrom(Seq(3, 2, 1, 0, -1))
        .toSeq should equal(Seq((2, 2), (1, 1), (0, 0)))
  }
}