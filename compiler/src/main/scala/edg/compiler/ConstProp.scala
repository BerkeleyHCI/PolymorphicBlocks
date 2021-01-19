package edg.compiler

import scala.collection.mutable
import scala.collection.Set

import edg.wir._
import edg.expr.expr
import edg.init.init


case class AssignRecord(target: IndirectDesignPath, root: DesignPath, value: expr.ValueExpr, source: SourceLocator)

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
  val paramTypes = new mutable.HashMap[DesignPath, Class[_ <: ExprValue]]  // only record types of authoritative elements

  val equalityEdges = new mutable.HashMap[IndirectDesignPath, mutable.Set[IndirectDesignPath]]  // bidirectional, two entries per edge

  // Assign statements are logged here before hitting paramExpr/paramUsedIn if waiting on an array
  val arrayUsedIn = new mutable.HashMap[DesignPath, mutable.Buffer[AssignRecord]]

  // Assign statements are logged here only when arrays are ready
  val paramExpr = new mutable.HashMap[IndirectDesignPath, AssignRecord]  // TODO case class?
  val paramUsedIn = new mutable.HashMap[IndirectDesignPath, mutable.Set[IndirectDesignPath]]  // source param -> dest param where source is part of the expr

  // Arrays are currently only defined on ports, and this is set once the array's length is known
  val arrayElts = new mutable.HashMap[DesignPath, Seq[String]]  // empty means not yet known

  //
  // Utility methods
  //
  /** Returns true if the parameter is ready to evaluate and propagate.
    * Returns false if dependencies are missing or the parameter has already been evaluated. */
  protected def isReadyToEvaluate(param: IndirectDesignPath): Boolean = {
    if (paramValues.isDefinedAt(param)) {
      return false
    }
    val assign = paramExpr(param)
    require(assign.target == param)
    val deps = new ExprRefDependencies(this, assign.root).map(assign.value)
    deps.forall(paramValues.isDefinedAt)
  }

  /** Evaluates the value of an ValueExpr at some DesignPath in some Design to a ExprValue, and propagates.
    * Throws an exception if dependent parameters are missing values.
    *
    * paramValues(param) should currently not resolve.
    * paramExpr and paramUsedIn must be filled in.
    */
  protected def evaluate(param: IndirectDesignPath): Unit = {
    require(!paramValues.isDefinedAt(param))
    val assign = paramExpr(param)
    require(assign.target == param)
    val eval = new ExprEvaluate(this, assign.root)
    assignAndPropagate(param, eval.map(assign.value))
  }

  /** Once all of a param's dependencies have been resolved, evaluate and propagate it.
    * Must only be called once per parameter, on assignment.
    */
  protected def assignAndPropagate(param: IndirectDesignPath, value: ExprValue, backedge: Option[IndirectDesignPath] = None): Unit = {
    require(!paramValues.isDefinedAt(param))
    paramValues.put(param, value)

    // Propagate along equality edges
    val paramValue = paramValues(param)
    equalityEdges.getOrElse(param, Set()).foreach { equalParam =>
      if (backedge.orNull != equalParam) {
        require(!paramValues.isDefinedAt(equalParam), s"redefinition of $equalParam via equality")
        assignAndPropagate(equalParam, paramValue, Some(param))
      }
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
  def addDeclaration(target: DesignPath, decl: init.ValInit): Unit = {
    require(!paramTypes.isDefinedAt(target), s"redeclaration of $target")
    val paramType = decl.`val` match {
      case init.ValInit.Val.Floating(_) => classOf[FloatValue]
      case init.ValInit.Val.Integer(_) => classOf[IntValue]
      case init.ValInit.Val.Boolean(_) => classOf[BooleanValue]
      case init.ValInit.Val.Text(_) => classOf[TextValue]
      case init.ValInit.Val.Range(_) => classOf[RangeValue]
      case _ => throw new NotImplementedError(s"Unknown param declaration / init $decl")
    }
    paramTypes.put(target, paramType)
  }

  protected def addAssignmentPostArray(assign: AssignRecord): Unit = {
    val deps = new ExprRefDependencies(this, assign.root).map(assign.value)
    deps.foreach { dep =>
      paramUsedIn.getOrElseUpdate(dep, mutable.Set()) += assign.target
    }

    paramExpr.put(assign.target, assign)
    if (isReadyToEvaluate(assign.target)) {
      evaluate(assign.target)
    }
  }

  /**
    * Adds a directed assignment (param <- expr) and propagates as needed
    */
  def addAssignment(target: IndirectDesignPath,
                    root: DesignPath, targetExpr: expr.ValueExpr, sourceLocator: SourceLocator): Unit = {
    require(!paramExpr.isDefinedAt(target), s"redefinition of $target via assignment")
    val assign = AssignRecord(target, root, targetExpr, sourceLocator)

    val arrayDeps = new ExprArrayDependencies(root).map(targetExpr)
    arrayDeps.foreach { arrayDep =>
      arrayUsedIn.getOrElseUpdate(arrayDep, mutable.Buffer()) += assign
    }

    if ((arrayDeps -- arrayElts.keySet).isEmpty) {  // only continue if is ready
      addAssignmentPostArray(assign)
    }
  }

  /**
    * Adds a bidirectional equality (param1 == param2) and propagates as needed.
    * Equality cycles (ignoring backedges) will cause infinite recursion and is currently not checked.
    * TODO: detect cycles
    */
  def addEquality(param1: IndirectDesignPath, param2: IndirectDesignPath): Unit = {
    // Store the pre-propagation values, so the parameters don't propagate forward then back
    val param1Value = paramValues.get(param1)
    val param2Value = paramValues.get(param2)
    // TODO maybe need guard against cyclic deps?
    // TODO maybe also detect against merging?

    param1Value match {
      case Some(param1Value) =>
        require(!paramValues.isDefinedAt(param2), s"redefinition of $param2 via equality")
        assignAndPropagate(param2, param1Value, Some(param1))
      case None => // do nothing
    }
    param2Value match {
      case Some(param2Value) =>
        require(!paramValues.isDefinedAt(param1), s"redefinition of $param1 via equality")
        assignAndPropagate(param1, param2Value, Some(param2))
      case None => // do nothing
    }

    // The back edges are skipped by the equality prop algorithm so we can delay adding those
    equalityEdges.getOrElseUpdate(param1, mutable.Set()) += param2
    equalityEdges.getOrElseUpdate(param2, mutable.Set()) += param1
  }

  def setArrayElts(target: DesignPath, elts: Seq[String]): Unit = {
    assert(arrayElts.getOrElse(target, elts) == elts)  // make sure overwrites are at least consistent
    arrayElts.put(target, elts)

    arrayUsedIn.getOrElse(target, mutable.Buffer()).foreach { assign =>
      val arrayDeps = new ExprArrayDependencies(assign.root).map(assign.value)
      if ((arrayDeps -- arrayElts.keySet).isEmpty) {  // only continue if is ready
        addAssignmentPostArray(assign)
      }
    }
  }

  /**
    * Returns the value of a parameter, or None if it does not have a value (yet?).
    * Can be used to check if parameters are resolved yet by testing against None.
    */
  def getValue(param: IndirectDesignPath): Option[ExprValue] = {
    paramValues.get(param)
  }
  def getValue(param: DesignPath): Option[ExprValue] = {
    // TODO should this be an implicit conversion?
    paramValues.get(IndirectDesignPath.fromDesignPath(param))
  }

  /**
    * Returns the type (as a class of ExprValue) of a parameter.
    */
  def getType(param: DesignPath): Option[Class[_ <: ExprValue]] = {
    paramTypes.get(param)
  }

  def getArrayElts(target: DesignPath): Option[Seq[String]] = {
    arrayElts.get(target)
  }

  /**
    * Returns all parameters with a definition (eg, ValInit) but missing a concrete assignment.
    * Ignores indirect references.
    */
  def getUnsolved: Set[DesignPath] = {
    paramTypes.keySet -- paramValues.keys.flatMap(DesignPath.fromIndirectOption)
  }
}
