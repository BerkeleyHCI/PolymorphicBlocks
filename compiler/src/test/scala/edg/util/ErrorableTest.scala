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
    // without .asInstanceOf[BigInt], this dispatches into the Option case and requires() out
    val err = Errorable(null.asInstanceOf[BigInt], "failure1")
    err should equal(Errorable.Error("failure1"))
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

  it should "map error messages" in {
    val ok = Errorable(BigInt(1), "ok").mapErr(msg => f"context1: $msg")
    ok should equal(Errorable.Success(BigInt(1)))
    val bad = Errorable(None, "failure").mapErr(msg => f"context2: $msg")
    bad should equal(Errorable.Error("context2: failure"))
  }
}
