package edg.util

import scala.collection.mutable


/** A dependency graph data structure, containing Key -> Key directed edges can be added, and Key -> Value mappings.
  * A node is "ready" when all its input edges have values.
  * Will not detect cyclic dependencies, but can tolerate them.
  * Tracks the frontier, so getReady() is fast.
  */
class DependencyGraph[KeyType, ValueType] {
  private val values = mutable.HashMap[KeyType, ValueType]()
  private val inverseDeps = mutable.HashMap[KeyType, mutable.Set[KeyType]]()
  private val deps = mutable.HashMap[KeyType, mutable.Set[KeyType]]()  // cache structure tracking undefined deps
  private val ready = mutable.Set[KeyType]()

  // Copies data from another dependency graph into this one, like a shallow clone
  def initFrom(that: DependencyGraph[KeyType, ValueType]): Unit = {
    require(values.isEmpty && inverseDeps.isEmpty && deps.isEmpty && ready.isEmpty)
    values.addAll(that.values)
    inverseDeps.addAll(that.inverseDeps.map { case (key, value) => // these require a deep copy
      key -> value.clone()
    })
    deps.addAll(that.deps.map { case (key, value) =>
      key -> value.clone()
    })
    ready.addAll(that.ready)
  }

  // Adds a node in the graph. May only be called once per node.
  def addNode(node: KeyType, dependencies: Seq[KeyType], update: Boolean = false): Unit = {
    deps.get(node) match {
      case Some(prevDeps) =>
        require(update, s"reinsertion of dependency for node $node <- $dependencies without update=true")
        // TODO can this requirement be eliminated?
        require(prevDeps.subsetOf(dependencies.toSet), "update of dependencies without being a superset of prior")
      case None =>  // nothing if no previous dependencies
    }
    require(!values.isDefinedAt(node), s"reinsertion of dependency for node with value $node = ${values(node)} <- $dependencies")
    val remainingDeps = (dependencies.toSet -- values.keySet).to(mutable.Set)

    deps.put(node, remainingDeps)
    for (dependency <- remainingDeps) {
      inverseDeps.getOrElseUpdate(dependency, mutable.Set()) += node
    }

    if (update && ready.contains(node)) {
      ready -= node
    }
    if (remainingDeps.isEmpty && !values.isDefinedAt(node)) {
      ready += node
    }
  }

  // Returns true if a node has been inserted for some key, whether a value has been set or not
  def nodeDefinedAt(node: KeyType): Boolean = deps.isDefinedAt(node)
  // Returns true if a value is available for some key, whether a node has been defined or not
  def valueDefinedAt(node: KeyType): Boolean = values.isDefinedAt(node)

  // Returns missing dependencies for a node, or empty if the node is ready or has a value assigned
  // Node must exist, or this will exception out
  def nodeMissing(node: KeyType): Set[KeyType] = deps(node).toSet

  // Sets the value of a node. May not overwrite values.
  def setValue(node: KeyType, value: ValueType): Unit = {
    require(!values.isDefinedAt(node), s"redefinition of $node (prior value ${values(node)}, new value $value)")
    deps.put(node, mutable.Set())
    values.put(node, value)
    if (ready.contains(node)) {
      ready -= node
    }

    // See if the update caused anything else to be ready
    for (inverseDep <- inverseDeps.getOrElse(node, mutable.Set())) {
      val remainingDeps = deps(inverseDep) -= node
      if (remainingDeps.isEmpty && !values.isDefinedAt(inverseDep)) {
        ready += inverseDep
      }
    }
  }

  def getValue(node: KeyType): Option[ValueType] = {
    values.get(node)
  }

  // Returns all the KeyTypes that don't have values and have satisfied dependencies.
  def getReady: Set[KeyType] = {
    ready.toSet
  }

  // Returns all the KeyTypes that have no values. NOT a fast operation.
  def getMissing: Set[KeyType] = {
    deps.keySet.toSet -- values.keySet
  }

  def knownValueKeys: Iterable[KeyType] = {
    values.keys
  }

  def toMap: Map[KeyType, ValueType] = values.toMap
}

object DependencyGraph {
  def apply[KeyType, ValueType](): DependencyGraph[KeyType, ValueType] = new DependencyGraph[KeyType, ValueType]
}
