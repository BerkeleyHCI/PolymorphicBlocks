package edg.compiler

import edg.wir._
import edg.expr.expr
import edg.lit.lit
import edg.ref.ref

sealed trait ExprValue

// These should be consistent with what is in init.proto
case class FloatValue(value: Float) extends ExprValue
case class IntValue(value: BigInt) extends ExprValue
case class BooleanValue(value: Boolean) extends ExprValue
case class TextValue(value: String) extends ExprValue


/**
  * ValueExpr transform that returns the dependencies as parameters.
  */
class GetExprDependencies(root: DesignPath) extends ValueExprMap[Set[DesignPath]] {
  override def mapLiteral(literal: lit.ValueLit): Set[DesignPath] = Set()

  override def mapBinary(binary: expr.BinaryExpr, lhs: Set[DesignPath], rhs: Set[DesignPath]): Set[DesignPath] =
    lhs ++ rhs

  override def mapReduce(reduce: expr.ReductionExpr, vals: Set[DesignPath]): Set[DesignPath] = vals

  override def mapStruct(struct: expr.StructExpr, vals: Map[String, Set[DesignPath]]): Set[DesignPath] =
    vals.values.flatten.toSet

  override def mapRange(range: expr.RangeExpr, minimum: Set[DesignPath], maximum: Set[DesignPath]): Set[DesignPath] =
    minimum ++ maximum

  override def mapIfThenElse(ite: expr.IfThenElseExpr, cond: Set[DesignPath],
                             tru: Set[DesignPath], fal: Set[DesignPath]): Set[DesignPath] =
    cond ++ tru ++ fal

  override def mapExtract(extract: expr.ExtractExpr,
                          container: Set[DesignPath], index: Set[DesignPath]): Set[DesignPath] =
    ???  // TODO need all elements of the container to be ready?

  override def mapMapExtract(mapExtract: expr.MapExtractExpr, container: Set[DesignPath]): Set[DesignPath] =
    ???  // TODO actually get all elements

  // connected and exported not overridden and to fail noisily
  // assign also not overridden and to fail noisily

  // TODO: how to resolve things like connected_link, is_connected?
  // Pass in connect map, and resolve to link?
  // Use connect edge facility?
  def mapRef(path: ref.LocalPath): Set[DesignPath] =
    throw new UnimplementedValueExprNode(s"Undefined mapRef for $path")
}


// Source locator class, wrapper around the proto. TODO: should this just be the proto when it exists?
class SourceLocator {
}


/**
  * Parameter propagation, evaluation, and resolution associated with a single design.
  * General philosophy: this should not refer to any particular design instance, so the design can continue to be
  * transformed (though those transformations must be strictly additive with regards to assignments and assertions)
  *
  * Handling aliased ports / indirect references (eg, link-side ports, CONNECTED_LINK):
  * Aliased ports and indirect references will have their own nodes in the graph.
  * Connected (block-link) and exported (block-block) port pairs will have an entry in a bidirectional connect map.
  * Assignments will check their port components against the connect map, and recursively assign to those nodes.
  *   Note: this requires structured paths (block/link/port/parameter components) for efficient matching.
  *   Since connect edges are bidirectional, the algorithm must avoid back-edges. Must also be acyclic otherwise.
  *
  * For now, assignments will just create entries in a connect map. Assume parameters will have connect entries before
  * they are used (design tree preorder traversal). Optional check that no existing parameters have the entry prefixes.
  *
  * Note, alternative options:
  * - Instead of connect maps, add bidirectional parameter-parameter edges. But this could be inefficient,
  * and requires the contents of elements to be known to generate these edges.
  * - Alias the ports and resolve to canonical references as constraints are being parsed. Simple, but discards design
  * data if the ConstProp object is to be used to generate debugging / tracing data. Requires the connects to be
  * processed before parameters are used. Likely still requires structured path data, though perhaps not everywhere.
  */
class ConstProp {
  // Adds an assignment (param <- expr) and propagates
  def addAssignment(root: DesignPath, target: ref.LocalPath, expr: expr.AssignExpr, sourceLocator: SourceLocator)

  // Returns the value of a parameter, or None if it does not have a value.
  // Can be used to check if parameters are resolved yet by testing against None.
  // Raises an exception if path does not resolve (including for a partial design tree),
  // or does not resolve to a parameter.
  def getValue(root: DesignPath, param: ref.LocalPath): Option[ExprValue]

  // Returns the type (as a class of ExprValue) of a parameter.
  // Same exception behavior as getValue.
  def getValueType(root: DesignPath, param: ref.LocalPath): Class[ExprValue]

  // Returns all parameters with a definition (eg, ValInit) but missing a concrete assignment.
  def getUnsolved(): Seq[DesignPath]

  // Adds an assertion (any expr that evaluates to a boolean).
  // Assertions are only checked on calling checkAssertions.
  def addAssertion(root: DesignPath, expr: expr.ValueExpr, sourceLocator: SourceLocator)

  // Checks all assertions, returning a list of failing assertions.
  // Expressions that do not evaluate are ignored. TODO: is this desired? but checks would be redundant w/ getUnsolved
  def checkAssertions(): Seq[(DesignPath, expr.ValueExpr, SourceLocator)]
}
