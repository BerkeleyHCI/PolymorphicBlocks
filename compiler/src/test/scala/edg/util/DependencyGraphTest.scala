package edg.util

import org.scalatest._
import org.scalatest.flatspec.AnyFlatSpec
import matchers.should.Matchers._


class DependencyGraphTest extends AnyFlatSpec {
  behavior of "DependencyGraph"

  it should "return empty ready on init" in {
    val dep = DependencyGraph[Int, Int]()
    dep.getReady shouldBe empty
  }

  it should "indicate a node with no dependencies is ready" in {
    val dep = DependencyGraph[Int, Int]()
    dep.addNode(1, Seq())
    dep.getReady should equal(Set(1))
  }

  it should "clear ready when value is set" in {
    val dep = DependencyGraph[Int, Int]()
    dep.addNode(1, Seq())
    dep.setValue(1, 1)
    dep.getReady shouldBe empty
  }

  it should "return set values" in {
    val dep = DependencyGraph[Int, Int]()
    dep.getValue(0) should equal(None)
    dep.toMap should equal(Map())
    dep.setValue(0, 10)
    dep.getValue(0) should equal(Some(10))
    dep.toMap should equal(Map(0 -> 10))
  }

  it should "track a single dependency, and add it to ready when set" in {
    val dep = DependencyGraph[Int, Int]()
    dep.addNode(1, Seq(0))
    dep.getReady shouldBe empty
    dep.setValue(0, 0)
    dep.getReady should equal(Set(1))
  }

  it should "track multiple dependencies, and add to ready when all set" in {
    val dep = DependencyGraph[Int, Int]()
    dep.addNode(3, Seq(0, 1, 2))
    dep.getReady shouldBe empty
    dep.setValue(0, 0)
    dep.getReady shouldBe empty
    dep.setValue(1, 0)
    dep.getReady shouldBe empty
    dep.setValue(2, 0)
    dep.getReady should equal(Set(3))
  }

  it should "track a chain of dependencies" in {
    val dep = DependencyGraph[Int, Int]()
    dep.addNode(1, Seq(0))
    dep.addNode(2, Seq(1))
    dep.addNode(3, Seq(2))
    dep.getReady shouldBe empty
    dep.setValue(0, 0)
    dep.getReady should equal(Set(1))
    dep.setValue(1, 0)
    dep.getReady should equal(Set(2))
    dep.setValue(2, 0)
    dep.getReady should equal(Set(3))
  }

  it should "track a chain of dependencies, inserted in reverse order" in {
    val dep = DependencyGraph[Int, Int]()
    dep.addNode(3, Seq(2))
    dep.addNode(2, Seq(1))
    dep.addNode(1, Seq(0))
    dep.getReady shouldBe empty
    dep.setValue(0, 0)
    dep.getReady should equal(Set(1))
    dep.setValue(1, 0)
    dep.getReady should equal(Set(2))
    dep.setValue(2, 0)
    dep.getReady should equal(Set(3))
  }

  it should "not include value set in ready" in {
    val dep = DependencyGraph[Int, Int]()
    dep.setValue(1, 0)
    dep.getReady shouldBe empty
    dep.addNode(1, Seq(0))
    dep.getReady shouldBe empty
  }


  it should "return knownValueKeys" in {
    val dep = DependencyGraph[Int, Int]()
    dep.knownValueKeys shouldBe empty
    dep.addNode(1, Seq(0))
    dep.knownValueKeys shouldBe empty
    dep.setValue(1, 1)
    dep.knownValueKeys should equal(Set(1))
  }

  it should "return getMissing" in {
    val dep = DependencyGraph[Int, Int]()
    dep.getMissing shouldBe empty
    dep.addNode(1, Seq(0))
    dep.getMissing should equal(Set(1))
    dep.setValue(1, 1)
    dep.getMissing shouldBe empty
  }
}
