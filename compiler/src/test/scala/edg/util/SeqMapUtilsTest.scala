package edg.util

import org.scalatest._
import org.scalatest.flatspec.AnyFlatSpec
import matchers.should.Matchers._
import collection.mutable
import collection.SeqMap


class SeqMapUtilsTest extends AnyFlatSpec {
  behavior of "SeqMapUtils"

  it should "replaceInPlace with None to delete, in reverse order" in {
    SeqMapUtils.replaceInPlace(mutable.SeqMap(2 -> 2, 1 -> 1, 0 -> 0), 1, Seq()) should equal(
      mutable.SeqMap(2 -> 2, 0 -> 0)
    )
  }

  it should "replaceInPlace with None to delete" in {
    SeqMapUtils.replaceInPlace(mutable.SeqMap(0 -> 0, 1 -> 1, 2 -> 2), 1, Seq()) should equal(
      mutable.SeqMap(0 -> 0, 2 -> 2)
    )
  }

  it should "replaceInPlace with None in first position" in {
    SeqMapUtils.replaceInPlace(mutable.SeqMap(0 -> 0, 1 -> 1, 2 -> 2), 0, Seq()) should equal(
      mutable.SeqMap(1 -> 1, 2 -> 2)
    )
  }

  it should "replaceInPlace with None in last position" in {
    SeqMapUtils.replaceInPlace(mutable.SeqMap(0 -> 0, 1 -> 1, 2 -> 2), 2, Seq()) should equal(
      mutable.SeqMap(0 -> 0, 1 -> 1)
    )
  }

  it should "replaceInPlace with single element" in {
    SeqMapUtils.replaceInPlace(mutable.SeqMap(0 -> 0, 1 -> 1, 2 -> 2), 1, Seq(1 -> 11)) should equal(
      mutable.SeqMap(0 -> 0, 1 -> 11, 2 -> 2)
    )
  }

  it should "replaceInPlace with multiple elements" in {
    SeqMapUtils.replaceInPlace(mutable.SeqMap(0 -> 0, 1 -> 1, 2 -> 2), 1, Seq(1 -> 11, 4 -> 44)) should equal(
      mutable.SeqMap(0 -> 0, 1 -> 11, 4 -> 44, 2 -> 2)
    )
  }

}
