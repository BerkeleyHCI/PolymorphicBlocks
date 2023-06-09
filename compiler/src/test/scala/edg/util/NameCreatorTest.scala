package edg.util

import org.scalatest.flatspec.AnyFlatSpec
import org.scalatest.matchers.should.Matchers

class NameCreatorTest extends AnyFlatSpec with Matchers {
  behavior.of("NameCreator")

  it should "return a new name" in {
    val nameCreator = new NameCreator(Set())
    nameCreator.newName("test") should equal("test")
  }

  it should "deconflict with initial names" in {
    val nameCreator = new NameCreator(Set("test"))
    nameCreator.newName("test") should equal("test2")
  }

  it should "deconflict with previously returned names" in {
    val nameCreator = new NameCreator(Set())
    nameCreator.newName("test") should equal("test")
    nameCreator.newName("test") should equal("test2")
    nameCreator.newName("test") should equal("test3")

    nameCreator.newName("test2") should equal("test22")
    nameCreator.newName("test2") should equal("test23")
  }
}
