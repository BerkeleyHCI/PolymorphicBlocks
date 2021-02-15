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


/** Utilities for graphs structured as adjacency matrices (typed Map[T, Iterable[T]]),
  * which may have back-edges
  */
class AdjacencyMatrix[T](mat: Map[T, Iterable[T]]) {
  /** Returns the set of nodes (matrix keys) reachable from some starting key.
    */
  def connectedSet(starting: T): Set[T] = {
    val setBuilder = mutable.Set[T]()
    def traverse(node: T): Unit = {
      if (setBuilder.contains(node)) {
        return
      }
      setBuilder.add(node)
      for (child <- mat.getOrElse(node, Seq())) {
        traverse(child)
      }
    }
    traverse(starting)
    setBuilder.toSet
  }
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
  // This only tracks overassigns that were discarded, not including assigns that took effect.
  // Additional analysis is needed to get the full set of conflicting assigns.
  val discardOverassigns = mutable.HashMap[IndirectDesignPath, OverassignRecord]()

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
      val record = discardOverassigns.getOrElseUpdate(dst, OverassignRecord())
      record.equals.add(src)
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
      val record = discardOverassigns.getOrElseUpdate(target, OverassignRecord())
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
      val record = discardOverassigns.getOrElseUpdate(target, OverassignRecord())
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
      case (Some(param1Value), Some(param2Value)) if param1Value == param2Value =>  // nop, already propagated
        // TODO: are these good semantics?
        // TODO: should this be recorded for debugging purposes / w/e?
      case (Some(param1Value), Some(param2Value)) =>
        val record1 = discardOverassigns.getOrElseUpdate(param1, OverassignRecord())
        record1.equals.add(param2)
        val record2 = discardOverassigns.getOrElseUpdate(param2, OverassignRecord())
        record2.equals.add(param1)
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

  def getErrors: Seq[CompilerError] = {
    // For all the overassigns, return the top-level "first" canonicalized path (merging the equalities)
    val equalityWithDiscard = equality map { case (target, sources) =>
      sources.toSeq ++ (discardOverassigns.get(target) match {
        case Some(record) => record.equals.toSeq
        case None => Seq()
      })
    }
    val equalityGraph = new AdjacencyMatrix(equality.toMap)
    val topPaths = discardOverassigns.map { case (target, record) =>
      val all = equalityGraph.connectedSet(target).toSeq.sortBy(_.steps.head.toString).sortBy(_.steps.length)
      all.head
    }.toSet.toSeq//.toSet.toSeq.sortBy(_.steps.head.toString)
       // .sortBy(_.steps.length)

    val overassignErrors = topPaths.map { topTarget =>
      val seen = mutable.Set[IndirectDesignPath]()
      val assignBuilder = mutable.ListBuffer[CompilerError.OverAssignCause]()
      def processNode(node: IndirectDesignPath): Unit = {  // traverse in DFS
        // insert propagated assigns first
        paramSource.get(node).foreach { case (root, constrName, value) =>
          assignBuilder += CompilerError.OverAssignCause.Assign(node, root, constrName, value)
        }
        // then insert non-propagated assigns
        discardOverassigns.get(node).foreach { record =>
          record.assigns.foreach { case (root, constrName, value) =>
            assignBuilder += CompilerError.OverAssignCause.Assign(node, root, constrName, value)
          }
        }
        // then iterate to propagated equalities
        for (child <- equality.getOrElse(node, mutable.Seq())) {
          if (!seen.contains(child)) {
            seen += child
            assignBuilder += CompilerError.OverAssignCause.Equal(node, child)
            processNode(child)
          }
        }
        // then non-propagated equalities
        discardOverassigns.get(node).foreach { record =>
          record.equals.foreach { child =>
            if (!seen.contains(child)) {
              seen += child
              assignBuilder += CompilerError.OverAssignCause.Equal(node, child)
              processNode(child)
            }
          }
        }
      }
      seen += topTarget
      processNode(topTarget)
      CompilerError.OverAssign(topTarget, assignBuilder.toSeq)
    }

    // Also get all empty range assignments
    val emptyRangeErrors = params.toMap.collect {
      case (ExprRef.Param(targetPath), DepValue.Param(range: RangeValue)) if range.isEmpty =>
        paramSource.get(targetPath).map { case (root, constrName, value) =>
          CompilerError.EmptyRange(targetPath, root, constrName, value)
        }
    }.flatten.toSeq

    overassignErrors ++ emptyRangeErrors
  }
}
