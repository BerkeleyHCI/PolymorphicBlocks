package edg.wir

import org.scalatest._
import org.scalatest.flatspec.AnyFlatSpec
import matchers.should.Matchers._

import scala.collection.SeqMap


class MapSortTest extends AnyFlatSpec {
  behavior of "NamespaceSort"

  it should "preserve order on empty order" in {
    MapSort(
      SeqMap(0 -> 0, 1 -> 1, 2 -> 2), Seq()
    ).toSeq should equal(Seq((0, 0), (1, 1), (2, 2)))
  }

  it should "resort input map" in {
    MapSort(
      SeqMap(0 -> 0, 1 -> 1, 2 -> 2), Seq(0, 1, 2)
    ).toSeq should equal(Seq((0, 0), (1, 1), (2, 2)))
  }

  it should "resort input map, input reversed" in {
    MapSort(
      SeqMap(0 -> 0, 1 -> 1, 2 -> 2), Seq(2, 1, 0)
    ).toSeq should equal(Seq((2, 2), (1, 1), (0, 0)))
  }

  it should "resort input map, input reversed, ignoring extra name elements" in {
    MapSort(
      SeqMap(0 -> 0, 1 -> 1, 2 -> 2), Seq(3, 2, 1, 0, -1)
    ).toSeq should equal(Seq((2, 2), (1, 1), (0, 0)))
  }
}