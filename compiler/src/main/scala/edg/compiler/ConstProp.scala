package edg.compiler

import scala.collection.mutable
import scala.collection.Set
import edg.wir._
import edg.expr.expr
import edg.init.init
import edg.util.{DependencyGraph, MutableBiMap}
import edg.ExprBuilder


case class OverassignError(target: IndirectDesignPath,
                           oldAssign: (DesignPath, String, expr.ValueExpr),
                           newAssign: (DesignPath, String, expr.ValueExpr)
                          ) extends Exception(
  s"Redefinition of $target: old assign $oldAssign, new assign $newAssign"
)


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
  // Assign statements logged here on addAssignment
  val paramAssign = mutable.HashMap[IndirectDesignPath, AssignRecord]()
  // Param source, for error tracking
  val paramSource = mutable.HashMap[IndirectDesignPath, (DesignPath, String, expr.ValueExpr)]()

  // Assign statements are added to the dependency graph only when arrays are ready
  // This is the authoritative source for the state of any param - in the graph (and its dependencies), or value solved
  val params = DependencyGraph[IndirectDesignPath, ExprValue]()
  val paramTypes = new mutable.HashMap[DesignPath, Class[_ <: ExprValue]]  // only record types of authoritative elements

  // Params that have a forced/override value, which must be set before any assign statements are parsed
  // TODO how to handle constraints on parameters from an outer component?
  // Perhaps don't propagate assigns to targets before the param type is parsed?
  val forcedParams = mutable.Set[IndirectDesignPath]()

  // Equality, two entries per equality edge (one per direction / target)
  val equality = mutable.HashMap[IndirectDesignPath, mutable.Buffer[IndirectDesignPath]]()

  // Arrays are currently only defined on ports, and this is set once the array's length is known
  val arrayElts = DependencyGraph[IndirectDesignPath, Seq[String]]  // empty means not yet known


  //
  // Callbacks, to be overridden at instantiation site
  //
  def onParamSolved(param: IndirectDesignPath, value: ExprValue): Unit = { }
  def onArraySolved(array: IndirectDesignPath, elts: Seq[String]): Unit = { }


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

  // Repeated does propagations as long as there is work to do, including both array available and param available.
  protected def update(): Unit = {
    while (arrayElts.getReady.nonEmpty || params.getReady.nonEmpty) {
      for (constrTarget <- arrayElts.getReady) {
        // TODO avoid null hack - but it allows things to fail noisily and should never be used
        arrayElts.setValue(constrTarget, null)  // remove from ready queue
        val assign = paramAssign(constrTarget)
        val deps = new ExprRefDependencies(this, assign.root).map(assign.value)
        params.addNode(constrTarget, deps.toSeq)
      }
      for (constrTarget <- params.getReady) {
        val assign = paramAssign(constrTarget)
        val value = new ExprEvaluate(this, assign.root).map(assign.value)
        params.setValue(constrTarget, value)
        onParamSolved(constrTarget, value)
        for (constrTargetEquals <- equality.getOrElse(constrTarget, mutable.Buffer())) {
          propagateEquality(constrTargetEquals, constrTarget, value)
        }
      }
    }
  }

  protected def propagateEquality(dst: IndirectDesignPath, src: IndirectDesignPath, value: ExprValue): Unit = {
    require(params.getValue(dst).isEmpty, s"redefinition of $dst via equality from $src = $value")
    params.setValue(dst, value)
    onParamSolved(dst, value)
    for (dstEquals <- equality.getOrElse(dst, mutable.Buffer())) {
      if (dstEquals != src) {  // ignore the backedge for propagation
        propagateEquality(dstEquals, dst, value)
      }
    }
  }

  /**
    * Adds a directed assignment (param <- expr) and propagates as needed
    */
  def addAssignment(target: IndirectDesignPath,
                    root: DesignPath, targetExpr: expr.ValueExpr,
                    constrName: String = "", sourceLocator: SourceLocator = new SourceLocator()): Unit = {
    if (forcedParams.contains(target)) {
      return  // ignore forced params
    }
    val paramSourceRecord = (root, constrName, targetExpr)
    if (params.nodeDefinedAt(target)) {
      throw OverassignError(target, paramSource(target), paramSourceRecord)
    }

    val assign = AssignRecord(target, root, targetExpr, sourceLocator)
    paramAssign.put(target, assign)
    paramSource.put(target, paramSourceRecord)

    val arrayDeps = new ExprArrayDependencies(root).map(targetExpr).map(_.asIndirect)
    arrayElts.addNode(target, arrayDeps.toSeq)

    update()
  }

  /** Sets a value directly (without the expr)
    */
  def setValue(target: IndirectDesignPath, value: ExprValue, constrName: String = "setValue"): Unit = {
    val paramSourceRecord = (DesignPath(), constrName, ExprBuilder.ValueExpr.Literal(value.toLit))
    if (params.nodeDefinedAt(target)) {
      throw OverassignError(target, paramSource(target), paramSourceRecord)
    }
    params.setValue(target, value)
    paramSource.put(target, paramSourceRecord)
    onParamSolved(target, value)
  }

  /** Sets a value directly, and ignores subsequent assignments.
    * TODO: this still preserve semantics that forbid over-assignment, even if those don't do anything
    */
  def setForcedValue(target: IndirectDesignPath, value: ExprValue, constrName: String = "forcedValue"): Unit = {
    val paramSourceRecord = (DesignPath(), constrName, ExprBuilder.ValueExpr.Literal(value.toLit))
    if (params.nodeDefinedAt(target)) {
      throw OverassignError(target, paramSource(target), paramSourceRecord)
    }
    params.setValue(target, value)
    paramSource.put(target, paramSourceRecord)
    forcedParams += target
    onParamSolved(target, value)
  }

  /**
    * Adds a bidirectional equality (param1 == param2) and propagates as needed.
    * Equality cycles (ignoring backedges) will cause infinite recursion and is currently not checked.
    * TODO: detect cycles
    */
  def addEquality(param1: IndirectDesignPath, param2: IndirectDesignPath): Unit = {
    equality.getOrElseUpdate(param1, mutable.Buffer()) += param2
    equality.getOrElseUpdate(param2, mutable.Buffer()) += param1

    // the initial propagation (if applicable) is tricky
    // we assume that propagations between param1 and its equal nodes, and param2 and its equal nodes, are done prior
    (params.getValue(param1), params.getValue(param2)) match {
      case (Some(param1Value), Some(param2Value)) =>
        // TODO better exception type?
        throw new IllegalArgumentException(s"equality between $param1 = $param1Value <-> $param2 = $param2Value with both values already defined")
      case (Some(param1Value), None) => propagateEquality(param2, param1, param1Value)
      case (None, Some(param2Value)) => propagateEquality(param1, param2, param2Value)
      case (None, None) => // nothing to be done
    }

    update()
  }

  def setArrayElts(target: DesignPath, elts: Seq[String]): Unit = {
    val indirectTarget = target.asIndirect
    arrayElts.setValue(indirectTarget, elts)
    onArraySolved(indirectTarget, elts)

    update()
  }

  /**
    * Returns the value of a parameter, or None if it does not have a value (yet?).
    * Can be used to check if parameters are resolved yet by testing against None.
    */
  def getValue(param: IndirectDesignPath): Option[ExprValue] = {
    params.getValue(param)
  }
  def getValue(param: DesignPath): Option[ExprValue] = {
    // TODO should this be an implicit conversion?
    getValue(param.asIndirect)
  }

  /**
    * Returns the type (as a class of ExprValue) of a parameter.
    */
  def getType(param: DesignPath): Option[Class[_ <: ExprValue]] = {
    paramTypes.get(param)
  }

  def getArrayElts(target: DesignPath): Option[Seq[String]] = {
    arrayElts.getValue(target.asIndirect)
  }

  /**
    * Returns all parameters with a definition (eg, ValInit) but missing a concrete assignment.
    * Ignores indirect references.
    */
  def getUnsolved: Set[DesignPath] = {
    paramTypes.keySet -- params.knownValueKeys.flatMap(DesignPath.fromIndirectOption)
  }

  def getAllSolved: Map[IndirectDesignPath, ExprValue] = params.toMap
}
