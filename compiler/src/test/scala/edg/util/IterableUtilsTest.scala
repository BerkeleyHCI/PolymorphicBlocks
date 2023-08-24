package edg.util

import org.scalatest.flatspec.AnyFlatSpec
import org.scalatest.matchers.should.Matchers._

class IterableUtilsTest extends AnyFlatSpec {
  behavior.of("IterableUtils")

  it should "work for Some" in {
    IterableUtils.getAllDefined(Seq(Some(1))) should equal(Some(Seq(1)))
    IterableUtils.getAllDefined(Seq(Some(1), Some(2))) should equal(Some(Seq(1, 2)))
  }

  it should "work for None" in {
    IterableUtils.getAllDefined(Seq(None)) should equal(None)
    IterableUtils.getAllDefined(Seq(None, None)) should equal(None)
  }

  it should "work for mixed" in {
    IterableUtils.getAllDefined(Seq(Some(1), None)) should equal(None)
    IterableUtils.getAllDefined(Seq(Some(1), None, Some(3))) should equal(None)
  }
}
