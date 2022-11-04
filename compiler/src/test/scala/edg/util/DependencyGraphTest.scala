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
    dep.nodeMissing(1) should equal(Set(0))
    dep.setValue(0, 0)
    dep.getReady should equal(Set(1))
    dep.nodeMissing(1) should equal(Set())
  }

  it should "track multiple dependencies, and add to ready when all set" in {
    val dep = DependencyGraph[Int, Int]()
    dep.addNode(3, Seq(0, 1, 2))
    dep.getReady shouldBe empty
    dep.nodeMissing(3) should equal(Set(0, 1, 2))
    dep.setValue(0, 0)
    dep.getReady shouldBe empty
    dep.nodeMissing(3) should equal(Set(1, 2))
    dep.setValue(1, 0)
    dep.getReady shouldBe empty
    dep.nodeMissing(3) should equal(Set(2))
    dep.setValue(2, 0)
    dep.getReady should equal(Set(3))
    dep.nodeMissing(3) should equal(Set())
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

  it should "prevent reinsertion of a node" in {
    val dep = DependencyGraph[Int, Int]()
    assertThrows[IllegalArgumentException] {
      dep.addNode(1, Seq(0))
      dep.addNode(1, Seq(0))
    }
  }

  it should "prevent reinsertion of a node, after initial set" in {
    val dep = DependencyGraph[Int, Int]()
    assertThrows[IllegalArgumentException] {
      dep.setValue(1, 1)
      dep.addNode(1, Seq(0))
    }
  }

  it should "prevent reinsertion of a node, after resolution and set" in {
    val dep = DependencyGraph[Int, Int]()
    assertThrows[IllegalArgumentException] {
      dep.addNode(1, Seq(0))
      dep.setValue(0, 0)
      dep.setValue(1, 1)
      dep.setValue(1, 1)
    }
  }

  it should "allow update with explicit update" in {
    val dep = DependencyGraph[Int, Int]()
    dep.addNode(10, Seq(0))
    dep.addNode(10, Seq(0, 1), update=true)
    dep.setValue(0, 0)
    dep.getReady should equal(Set())  // should still be blocked on 1

    dep.addNode(10, Seq(1, 2), update=true)  // 0 should no longer be required

    dep.setValue(1, 1)
    dep.getReady should equal(Set())
    dep.setValue(2, 2)
    dep.getReady should equal(Set(10))

    dep.addNode(10, Seq(1, 2), update=true)  // should be a nop
    dep.getReady should equal(Set(10))

    dep.addNode(10, Seq(3), update=true)
    dep.getReady should equal(Set())  // should no longer be ready
  }

  it should "return nodeDefinedAt and valueDefinedAt for dependencies" in {
    val dep = DependencyGraph[Int, Int]()
    dep.addNode(1, Seq(0))
    dep.nodeDefinedAt(1) should equal(true)
    dep.valueDefinedAt(1) should equal(false)
    dep.nodeDefinedAt(2) should equal(false)
    dep.addNode(2, Seq(0))
    dep.nodeDefinedAt(1) should equal(true)
    dep.valueDefinedAt(1) should equal(false)
    dep.nodeDefinedAt(2) should equal(true)
    dep.setValue(1, 1)
    dep.nodeDefinedAt(1) should equal(true)
    dep.valueDefinedAt(1) should equal(true)
    dep.nodeDefinedAt(2) should equal(true)
  }

  it should "track a single dependency separately with initFrom" in {
    val dep1 = DependencyGraph[Int, Int]()
    dep1.addNode(1, Seq(0))
    dep1.getReady shouldBe empty
    val dep2 = DependencyGraph[Int, Int]()
    dep2.initFrom(dep1)
    dep2.getReady shouldBe empty
    dep2.nodeMissing(1) should equal(Set(0))

    dep1.setValue(0, 0)
    dep1.getReady should equal(Set(1))
    dep1.nodeMissing(1) should equal(Set())
    dep2.getReady shouldBe empty
    dep2.nodeMissing(1) should equal(Set(0))

    dep2.setValue(0, 0)
    dep2.getReady should equal(Set(1))
    dep2.nodeMissing(1) should equal(Set())
  }
}
