package edg.compiler

import edg.wir._
import edg.expr.expr

sealed trait ExprValue

// These should be consistent with what is in init.proto
case class FloatValue(value: Float) extends ExprValue
case class IntValue(value: BigInt) extends ExprValue
case class BooleanValue(value: Boolean) extends ExprValue
case class TextValue(value: String) extends ExprValue


// Source locator class, wrapper around the proto. TODO: should this just be the proto when it exists?
class SourceLocator {
}


/**
  * Parameter propagation, evaluation, and resolution associated with a single design.
  * General philosophy: this should not refer to any particular design instance, so the design can continue to be
  * transformed (though those transformations must be strictly additive with regards to assignments and assertions)
  */
class ConstProp {
  // Adds an assignment (param <- expr) and propagates
  def addAssignment(path: DesignPath, expr: expr.AssignExpr, sourceLocator: SourceLocator)

  // Returns the value of a parameter, or None if it does not have a value.
  // Can be used to check if parameters are resolved yet by testing against None.
  // Raises an exception if path does not resolve (including for a partial design tree),
  // or does not resolve to a parameter.
  def getValue(path: DesignPath): Option[ExprValue]

  // Returns the type (as a class of ExprValue) of a parameter.
  // Same exception behavior as getValue.
  def getValueType(path: DesignPath): Class[ExprValue]

  // Returns all parameters with a definition (eg, ValInit) but missing a concrete assignment.
  def getUnsolved(): Seq[DesignPath]

  // Adds an assertion (any expr that evaluates to a boolean).
  // Assertions are only checked on calling checkAssertions.
  def addAssertion(path: DesignPath, expr: expr.ValueExpr, sourceLocator: SourceLocator)

  // Checks all assertions, returning a list of failing assertions.
  // Expressions that do not evaluate are ignored. TODO: is this desired? but checks would be redundant w/ getUnsolved
  def checkAssertions(): Seq[(DesignPath, expr.ValueExpr, SourceLocator)]
}
