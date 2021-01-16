package edg.compiler

import scala.collection.mutable
import scala.collection.Set

import edg.wir._
import edg.expr.expr
import edg.lit.lit
import edg.ref.ref


/**
  * ValueExpr transform that returns the dependencies as parameters.
  */
class ExprRefDependencies(refs: ConstProp, root: IndirectDesignPath) extends ValueExprMap[Set[IndirectDesignPath]] {
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
    container ++ index

  override def mapMapExtract(mapExtract: expr.MapExtractExpr): Set[IndirectDesignPath] = {
    val container = mapExtract.container.get.expr.ref.getOrElse(  // TODO restrict allowed types in proto
      throw new ExprEvaluateException(s"Non-ref container type in mapExtract $mapExtract")
    )
    val containerPath = IndirectDesignPath.root ++ container
    val elts = refs.getArrayElts(containerPath).getOrElse(
      throw new ExprEvaluateException(s"Array elts not known for $container from $mapExtract")
    )
    elts.map { elt =>
      containerPath ++ Seq(elt) ++ mapExtract.path.get
    }
  }

  // connected and exported not overridden and to fail noisily
  // assign also not overridden and to fail noisily

  override def mapRef(path: ref.LocalPath): Set[IndirectDesignPath] = {
    Set(root ++ path)
  }
}


/**
  * Parameter propagation, evaluation, and resolution associated with a single design.
  * General philosophy: this should not refer to any particular design instance, so the design can continue to be
  * transformed (though those transformations must be strictly additive with regards to assignments and assertions)
  *
  * Handling aliased ports / indirect references (eg, link-side ports, CONNECTED_LINK):
  * addEquality must be called between the individual parameters and will immediately propagate.
  * addEquality is idempotent and may be repeated.
  */
class ConstProp {
  val paramValues = new mutable.HashMap[IndirectDesignPath, ExprValue]  // empty means not yet known
  val paramTypes = new mutable.HashMap[DesignPath, Class[ExprValue]]  // only record types of authoritative elements

  val equalityEdges = new mutable.HashMap[IndirectDesignPath, mutable.Set[IndirectDesignPath]]  // bidirectional, two entries per edge

  val paramExpr = new mutable.HashMap[IndirectDesignPath, (DesignPath, expr.ValueExpr, SourceLocator)]  // TODO case class?
  val paramUsedIn = new mutable.HashMap[IndirectDesignPath, Set[IndirectDesignPath]]  // source param -> dest param where source is part of the expr

  // Arrays are currently only defined on ports, and this is set once the array's length is known
  val arrayElts = new mutable.HashMap[IndirectDesignPath, Set[String]]  // empty means not yet known

  //
  // Utility methods
  //
  /** Returns true if the parameter is ready to evaluate and propagate.
    * Returns false if dependencies are missing or the parameter has already been evaluated. */
  protected def isReadyToEvaluate(param: IndirectDesignPath): Boolean = {
    if (paramValues.isDefinedAt(param)) {
      return false
    }
    val (root, expr, _) = paramExpr(param)
    val deps = new ExprRefDependencies(this, IndirectDesignPath.fromDesignPath(root)).map(expr)
    deps.forall(paramValues.isDefinedAt)
  }

  /** Evaluates the value of an ValueExpr at some DesignPath in some Design to a ExprValue, and propagates.
    * Throws an exception if dependent parameters are missing values.
    *
    * paramValues(param) should currently not resolve.
    * paramExpr and paramUsedIn must be filled in.
    */
  protected def evaluate(param: IndirectDesignPath: Unit = {
    require(!paramValues.isDefinedAt(param))
    val (root, expr, _) = paramExpr(param)

    val eval = new ExprEvaluate(this, IndirectDesignPath.fromDesignPath(root))
    assignAndPropagate(param, eval.map(expr))
  }

  /** Once all of a param's dependencies have been resolved, evaluate and propagate it.
    * Must only be called once per parameter, on assignment.
    */
  protected def assignAndPropagate(param: IndirectDesignPath, value: ExprValue): Unit = {
    require(!paramValues.isDefinedAt(param))
    paramValues.put(param, value)

    // Propagate along equality edges
    val paramValue = paramValues(param)
    equalityEdges.getOrElse(param, Set()).foreach { equalParam =>
      require(!paramValues.isDefinedAt(equalParam), s"redefinition of $equalParam via equality")
      paramValues.put(equalParam, paramValue)
      assignAndPropagate(equalParam)
    }

    // Propagate along dependent expressions
    paramUsedIn.getOrElse(param, Set()).foreach { dependent =>
      if (isReadyToEvaluate(dependent)) {
        evaluate(dependent)
      }
    }
  }

  //
  // API methods
  //
  /**
    * Adds a directed assignment (param <- expr) and propagates as needed
    */
  def addAssignment(target: IndirectDesignPath,
                    root: DesignPath, expr: expr.ValueExpr, sourceLocator: SourceLocator): Unit = {
    require(!paramExpr.isDefinedAt(target), s"redefinition of $target via assignment")

    paramExpr.put(target, (root, expr, sourceLocator))
    if (isReadyToEvaluate(target)) {
      evaluate(target)
    }
  }

  /**
    * Adds a bidirectional equality (param1 == param2) and propagates as needed
    */
  def addEquality(param1: IndirectDesignPath, param2: IndirectDesignPath): Unit = {
    equalityEdges.getOrElseUpdate(param1, mutable.Set()) += param2
    paramValues.get(param1) match {
      case Some(param1Value) =>
        require(!paramValues.isDefinedAt(param2), s"redefinition of $param2 via equality")
        assignAndPropagate(param2, param1Value)
      case None => // do nothing
    }

    equalityEdges.getOrElseUpdate(param2, mutable.Set()) += param1
    paramValues.get(param2) match {
      case Some(param2Value) =>
        require(!paramValues.isDefinedAt(param1), s"redefinition of $param1 via equality")
        assignAndPropagate(param1, param2Value)
      case None => // do nothing
    }
  }

  def setArrayElts(target: IndirectDesignPath, elts: Set[String]): Unit = {
    assert(arrayElts.getOrElse(target, elts) == elts)  // make sure overwrites are at least consistent
    arrayElts.put(target, elts)
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

  def getArrayElts(target: IndirectDesignPath): Option[Set[String]] = {
    arrayElts.get(target)
  }

  /**
    * Returns all parameters with a definition (eg, ValInit) but missing a concrete assignment.
    * Ignores indirect references.
    */
  def getUnsolved: Set[DesignPath] = {
    paramTypes.keySet -- paramValues.keySet.map(DesignPath.fromIndirect)
  }
}
