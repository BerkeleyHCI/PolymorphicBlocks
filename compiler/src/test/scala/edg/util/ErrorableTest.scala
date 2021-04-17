package edg.util

import org.scalatest.flatspec.AnyFlatSpec
import org.scalatest.matchers.should.Matchers


class ErrorableTest extends AnyFlatSpec with Matchers {
  behavior of "Errorable"

  it should "chain successes" in {
    val original = Errorable(BigInt(1), "failure1")
    val next2 = original.map("failure2") { _ + 2 }
    val next3 = next2.map { _ + 3 }
    next3 should equal(Errorable.Success(BigInt(6)))
  }

  it should "report null as failure by default" in {
    val err = Errorable(null.asInstanceOf[BigInt], "failure1")
    err should equal(Errorable.Error("failure1"))

    val errUnwrapped = Errorable(null, "failure1")
    errUnwrapped should equal(Errorable.Error("failure1"))
  }

  it should "unpack Option by default" in {
    val option: Option[BigInt] = Some(BigInt(1))
    val err = Errorable(option, "failure1")
    err should equal(Errorable.Success(BigInt(1)))
  }

  it should "report None as failure by default" in {
    val option: Option[BigInt] = None
    val err = Errorable(option, "failure1")
    err should equal(Errorable.Error("failure1"))
  }

  it should "preserve first failure" in {
    val original = Errorable(BigInt(1), "failure1")
    val fail = original.map("failure2") { prev => null.asInstanceOf[BigInt] }
    val fail2 = fail.map { _ + 3 }
    fail2 should equal(Errorable.Error("failure2"))
  }

  it should "chain successes on branching" in {
    val original1 = Errorable(BigInt(1), "failure1")
    val original2 = Errorable(BigInt(2), "failure2")
    val combined = (original1 + original2).map("add") { case (val1, val2) =>
      val1 + val2
    }
    combined should equal(Errorable.Success(BigInt(3)))
  }

  it should "preserve first failure on branching" in {
    val original1 = Errorable(null.asInstanceOf[BigInt], "failure1")
    val original2 = Errorable(BigInt(2), "failure2")
    val combined = (original1 + original2).map("add") { case (val1, val2) =>
      val1 + val2
    }
    combined should equal(Errorable.Error("failure1"))
  }
}
