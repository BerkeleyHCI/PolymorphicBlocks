package edg.compiler

import scala.collection.mutable
import scala.collection.Set
import edg.wir._
import edg.expr.expr
import edg.init.init
import edg.util.{DependencyGraph, MutableBiMap}
import edg.ExprBuilder
import edg.compiler.ExprRef


sealed trait DepValue  // TODO better name - dependency graph value

object DepValue {
  case class Param(value: ExprValue) extends DepValue
  case class Array(elts: Seq[String]) extends DepValue
}


case class AssignRecord(target: IndirectDesignPath, root: DesignPath, value: expr.ValueExpr, source: SourceLocator)

case class OverassignRecord(assigns: mutable.Set[(DesignPath, String, expr.ValueExpr)] = mutable.Set(),
                            equals: mutable.Set[IndirectDesignPath] = mutable.Set())

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
  val params = DependencyGraph[ExprRef, DepValue]()
  val paramTypes = new mutable.HashMap[DesignPath, Class[_ <: ExprValue]]  // only record types of authoritative elements

  // Params that have a forced/override value, which must be set before any assign statements are parsed
  // TODO how to handle constraints on parameters from an outer component?
  // Perhaps don't propagate assigns to targets before the param type is parsed?
  val forcedParams = mutable.Set[IndirectDesignPath]()

  // Equality, two entries per equality edge (one per direction / target)
  val equality = mutable.HashMap[IndirectDesignPath, mutable.Buffer[IndirectDesignPath]]()

  // Overassigns, for error tracking
  val overassigns = mutable.HashMap[IndirectDesignPath, OverassignRecord]()

  //
  // Callbacks, to be overridden at instantiation site
  //
  def onParamSolved(param: IndirectDesignPath, value: ExprValue): Unit = { }
  def onArraySolved(array: DesignPath, elts: Seq[String]): Unit = { }


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
    while (params.getReady.nonEmpty) {
      val constrTarget = params.getReady.head.asInstanceOf[ExprRef.Param].path
      val assign = paramAssign(constrTarget)
      new ExprEvaluatePartial(this, assign.root).map(assign.value) match {
        case ExprResult.Result(result) =>
          params.setValue(ExprRef.Param(constrTarget), DepValue.Param(result))
          onParamSolved(constrTarget, result)
          for (constrTargetEquals <- equality.getOrElse(constrTarget, mutable.Buffer())) {
            propagateEquality(constrTargetEquals, constrTarget, result)
          }
        case ExprResult.Missing(missing) =>
          params.addNode(ExprRef.Param(constrTarget), missing.toSeq, update=true)
      }
    }
  }

  protected def propagateEquality(dst: IndirectDesignPath, src: IndirectDesignPath, value: ExprValue): Unit = {
    if (params.getValue(ExprRef.Param(dst)).isDefined) {
      val record = overassigns.getOrElseUpdate(dst, OverassignRecord())
      record.equals.add(src)
      paramSource.get(dst).foreach( record.assigns.add )  // if there are assigns, make sure they are tracked
      equality.get(dst).foreach( equalitySrcs => equalitySrcs.foreach( record.equals.add ) )
      return  // first set "wins"
    }

    params.setValue(ExprRef.Param(dst), DepValue.Param(value))
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
    if (params.nodeDefinedAt(ExprRef.Param(target))) {
      val record = overassigns.getOrElseUpdate(target, OverassignRecord())
      record.assigns.add(paramSource(target))
      record.assigns.add(paramSourceRecord)
      return  // first set "wins"
    }

    val assign = AssignRecord(target, root, targetExpr, sourceLocator)
    paramAssign.put(target, assign)
    paramSource.put(target, paramSourceRecord)

    new ExprEvaluatePartial(this, root).map(targetExpr) match {
      case ExprResult.Result(result) =>
        params.setValue(ExprRef.Param(target), DepValue.Param(result))
        onParamSolved(target, result)
        for (constrTargetEquals <- equality.getOrElse(target, mutable.Buffer())) {
          propagateEquality(constrTargetEquals, target, result)
        }
      case ExprResult.Missing(missing) =>
        params.addNode(ExprRef.Param(target), missing.toSeq)  // explicitly not an update
    }

    update()
  }

  /** Sets a value directly (without the expr)
    */
  def setValue(target: IndirectDesignPath, value: ExprValue, constrName: String = "setValue"): Unit = {
    val paramSourceRecord = (DesignPath(), constrName, ExprBuilder.ValueExpr.Literal(value.toLit))
    if (params.nodeDefinedAt(ExprRef.Param(target))) {
      val record = overassigns.getOrElseUpdate(target, OverassignRecord())
      record.assigns.add(paramSource(target))
      record.assigns.add(paramSourceRecord)
      return  // first set "wins"
    }
    params.setValue(ExprRef.Param(target), DepValue.Param(value))
    paramSource.put(target, paramSourceRecord)
    onParamSolved(target, value)
  }

  /** Sets a value directly, and ignores subsequent assignments.
    * TODO: this still preserve semantics that forbid over-assignment, even if those don't do anything
    */
  def setForcedValue(target: IndirectDesignPath, value: ExprValue, constrName: String = "forcedValue"): Unit = {
    val paramSourceRecord = (DesignPath(), constrName, ExprBuilder.ValueExpr.Literal(value.toLit))
    require(!params.nodeDefinedAt(ExprRef.Param(target)), "forced value must be set before assigns")

    params.setValue(ExprRef.Param(target), DepValue.Param(value))
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
    (params.getValue(ExprRef.Param(param1)), params.getValue(ExprRef.Param(param2))) match {
      case (Some(param1Value), Some(param2Value)) =>
        val record1 = overassigns.getOrElseUpdate(param1, OverassignRecord())
        record1.equals.add(param2)
        paramSource.get(param1).foreach( record1.assigns.add )
        equality.get(param1).foreach( equalitySrcs => equalitySrcs.foreach( record1.equals.add ) )
        val record2 = overassigns.getOrElseUpdate(param2, OverassignRecord())
        record2.equals.add(param1)
        paramSource.get(param2).foreach( record2.assigns.add )
        equality.get(param2).foreach( equalitySrcs => equalitySrcs.foreach( record2.equals.add ) )
        // the equality is ignored otherwise
      case (Some(param1Value), None) => propagateEquality(param2, param1,
                                                          param1Value.asInstanceOf[DepValue.Param].value)
      case (None, Some(param2Value)) => propagateEquality(param1, param2,
                                                          param2Value.asInstanceOf[DepValue.Param].value)
      case (None, None) => // nothing to be done
    }

    update()
  }

  def setArrayElts(target: DesignPath, elts: Seq[String]): Unit = {
    params.setValue(ExprRef.Array(target), DepValue.Array(elts))
    onArraySolved(target, elts)
    update()
  }

  /**
    * Returns the value of a parameter, or None if it does not have a value (yet?).
    * Can be used to check if parameters are resolved yet by testing against None.
    */
  def getValue(param: IndirectDesignPath): Option[ExprValue] = {
    params.getValue(ExprRef.Param(param)).map(_.asInstanceOf[DepValue.Param].value)
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
    params.getValue(ExprRef.Array(target)).map(_.asInstanceOf[DepValue.Array].elts)
  }

  /**
    * Returns all parameters with a definition (eg, ValInit) but missing a concrete assignment.
    * Ignores indirect references.
    */
  def getUnsolved: Set[DesignPath] = {
    paramTypes.keySet -- params.knownValueKeys.collect {
      case ExprRef.Param(param) => param
    }.flatMap(DesignPath.fromIndirectOption)
  }

  def getAllSolved: Map[IndirectDesignPath, ExprValue] = params.toMap.collect {
    case (ExprRef.Param(param), value) => param -> value.asInstanceOf[DepValue.Param].value
  }

  def getErrors: Seq[CompilerError.OverAssign] = overassigns.map { case (target, record) =>
    CompilerError.OverAssign(target,
      assigns=record.assigns.map { case (root, constrName, constr) =>
        (root, constrName, constr)
      }.toSeq, equals = record.equals.map { equals =>
        equals
      }.toSeq)
  }.toSeq
}
