package edg.compiler

import scala.collection.mutable
import scala.collection.Set

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
class GetExprDependencies(root: IndirectDesignPath) extends ValueExprMap[Set[IndirectDesignPath]] {
  override def mapLiteral(literal: lit.ValueLit): Set[IndirectDesignPath] = Set()

  override def mapBinary(binary: expr.BinaryExpr,
                         lhs: Set[IndirectDesignPath], rhs: Set[IndirectDesignPath]): Set[IndirectDesignPath] =
    lhs ++ rhs

  override def mapReduce(reduce: expr.ReductionExpr, vals: Set[IndirectDesignPath]): Set[IndirectDesignPath] = vals

  override def mapStruct(struct: expr.StructExpr, vals: Map[String, Set[IndirectDesignPath]]): Set[IndirectDesignPath] =
    vals.values.flatten.toSet

  override def mapRange(range: expr.RangeExpr,
                        minimum: Set[IndirectDesignPath], maximum: Set[IndirectDesignPath]): Set[IndirectDesignPath] =
    minimum ++ maximum

  override def mapIfThenElse(ite: expr.IfThenElseExpr, cond: Set[IndirectDesignPath],
                             tru: Set[IndirectDesignPath], fal: Set[IndirectDesignPath]): Set[IndirectDesignPath] =
    cond ++ tru ++ fal

  override def mapExtract(extract: expr.ExtractExpr,
                          container: Set[IndirectDesignPath], index: Set[IndirectDesignPath]): Set[IndirectDesignPath] =
    ???  // TODO need all elements of the container to be ready?

  override def mapMapExtract(mapExtract: expr.MapExtractExpr, container: Set[IndirectDesignPath]): Set[IndirectDesignPath] =
    ???  // TODO actually get all elements

  // connected and exported not overridden and to fail noisily
  // assign also not overridden and to fail noisily

  override def mapRef(path: ref.LocalPath): Set[IndirectDesignPath] = {
    Set(root ++ path)
  }
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
  val paramValues = new mutable.HashMap[IndirectDesignPath, ExprValue]  // empty means not yet known
  val paramTypes = new mutable.HashMap[DesignPath, Class[ExprValue]]  // only record types of authoritative elements

  val equalityEdges = new mutable.HashMap[IndirectDesignPath, IndirectDesignPath]  // bidirectional, two entries per edge

  val paramExpr = new mutable.HashMap[IndirectDesignPath, (DesignPath, expr.ValueExpr, SourceLocator)]  // value as root, expr
  val paramUsedIn = new mutable.HashMap[IndirectDesignPath, IndirectDesignPath]  // source param -> dest param where source is part of the expr

  //
  // Utility methods
  //
  /**
    * Evaluates the value of an ValueExpr at some DesignPath in some Design to a ExprValue.
    * Throws an exception if dependent parameters are missing values.
    */
  protected def evaluate(param: IndirectDesignPath): ExprValue = {

  }

  //
  // API methods
  //
  /**
    * Adds an assignment (param <- expr) and propagates
    */
  def addAssignment(target: IndirectDesignPath,
                    root: DesignPath, expr: expr.AssignExpr, sourceLocator: SourceLocator): Unit = {

    // TODO add to table and propagate
  }

  def addEquality(param1: IndirectDesignPath, param2: IndirectDesignPath): Unit = {
    // TODO add to table and propagate
  }

  /**
    * Returns the value of a parameter, or None if it does not have a value (yet?).
    * Can be used to check if parameters are resolved yet by testing against None.
    */
  //
  def getValue(param: IndirectDesignPath): Option[ExprValue] = {
    paramValues.get(param)
  }

  /**
    * Returns the type (as a class of ExprValue) of a parameter.
    */
  def getValueType(param: DesignPath): Option[Class[ExprValue]] = {
    paramTypes.get(param)
  }

  /**
    * Returns all parameters with a definition (eg, ValInit) but missing a concrete assignment.
    * Ignores indirect references.
    */
  def getUnsolved: Set[DesignPath] = {
    paramTypes.keySet -- paramValues.keySet.map(DesignPath.fromIndirect)
  }
}
