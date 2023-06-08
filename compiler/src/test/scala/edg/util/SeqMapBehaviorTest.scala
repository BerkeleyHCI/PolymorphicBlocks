package edg.util

import org.scalatest.flatspec.AnyFlatSpec
import org.scalatest.matchers.should.Matchers._

import scala.collection.SeqMap

class SeqMapBehaviorTest extends AnyFlatSpec {
  behavior.of("SeqMap")

  it should "maintain sortedness through .view.mapValues" in {
    (0 until 32).map(x => (x, x)).to(SeqMap).view.mapValues(2 * _).toSeq should equal(
      (0 until 32).map(x => (x, 2 * x))
    )
    (0 until 32).reverse.map(x => (x, x)).to(SeqMap).view.mapValues(2 * _).toSeq should equal(
      (0 until 32).reverse.map(x => (x, 2 * x))
    )

    (0 until 32).reverse.map(x => (x, x)).to(SeqMap).view.mapValues(2 * _).toSeq shouldNot equal(
      (0 until 32).map(x => (x, 2 * x))
    )
  }

  it should "maintain sortedness of keys" in {
    (0 until 32).map(x => (x, x)).to(SeqMap).keys should equal(
      0 until 32
    )
    (0 until 32).reverse.map(x => (x, x)).to(SeqMap).keys should equal(
      (0 until 32).reverse
    )

    (0 until 32).reverse.map(x => (x, x)).to(SeqMap).keys shouldNot equal(
      0 until 32
    )
  }

  it should "compare sortedness when converted back to Seq" in {
    (0 until 32).map(x => (x, x)).to(SeqMap).toSeq shouldNot equal(
      (0 until 32).reverse.map(x => (x, x)).to(SeqMap).toSeq
    )
  }
}
