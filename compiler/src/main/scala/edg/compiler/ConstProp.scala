package edg.compiler

import scala.collection.mutable
import scala.collection.Set
import edgir.expr.expr
import edgir.init.init
import edg.wir._
import edg.util.{DependencyGraph, MutableBiMap}
import edg.ExprBuilder
import edgir.ref.ref.LocalPath


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


sealed trait ConnectedLinkRecord  // a record in the connected link directed graph
object ConnectedLinkRecord {
  // a connection that is directly to a link, with the graph value being the path to the link itself
  case class ConnectedLink(port: DesignPath) extends ConnectedLinkRecord
  // for a connect that isn't directly to a link, lowers into ConnectedLink once the final destination is known
  case class Connected(port: DesignPath, nextPortToLink: DesignPath) extends ConnectedLinkRecord
}


sealed trait ConnectedLinkResult  // a result for resolving connected links
object ConnectedLinkResult {
  case class ResolvedPath(path: IndirectDesignPath) extends ConnectedLinkResult
  case class MissingConnectedLink(port: DesignPath) extends ConnectedLinkResult
}


/**
  * Parameter propagation, evaluation, and resolution associated with a single design.
  * General philosophy: this should not refer to any particular design instance, so the design can continue to be
  * transformed (though those transformations must be strictly additive with regards to assignments and assertions)
  *
  * This class resolves CONNECTED_LINK references once the connections are known, though
  * parameters on connected ports must be manually propagated via addEquality.
  * addEquality is idempotent and may be repeated.
  */
class ConstProp {
  // Assign statements logged here on addAssignment
  val paramAssign = mutable.HashMap[IndirectDesignPath, AssignRecord]()
  // Param source, for error tracking
  val paramSource = mutable.HashMap[IndirectDesignPath, (DesignPath, String, expr.ValueExpr)]()

  // Assign statements are added to the dependency graph only when arrays are ready
  // This is the authoritative source for the state of any param - in the graph (and its dependencies), or value solved
  // CONNECTED_LINK has an empty value but indicates that the path was resolved in that data structure
  val params = DependencyGraph[IndirectDesignPath, ExprValue]()
  val paramTypes = new mutable.HashMap[DesignPath, Class[_ <: ExprValue]]  // only record types of authoritative elements

  val connectedLink = DependencyGraph[ConnectedLinkRecord, DesignPath]()  // tracks the port -> link paths

  // Params that have a forced/override value, which must be set before any assign statements are parsed
  // TODO how to handle constraints on parameters from an outer component?
  // Perhaps don't propagate assigns to targets before the param type is parsed?
  val forcedParams = mutable.Set[IndirectDesignPath]()

  // Equality, two entries per equality edge (one per direction / target)
  // This is a very special case, only used for port parameter propagations, and perhaps
  // even that can be replaced with directed assignments
  val equality = mutable.HashMap[IndirectDesignPath, mutable.Buffer[IndirectDesignPath]]()

  // Overassigns, for error tracking
  // This only tracks overassigns that were discarded, not including assigns that took effect.
  // Additional analysis is needed to get the full set of conflicting assigns.
  val discardOverassigns = mutable.HashMap[IndirectDesignPath, OverassignRecord]()

  //
  // Callbacks, to be overridden at instantiation site
  //
  def onParamSolved(param: IndirectDesignPath, value: ExprValue): Unit = { }


  // For some path, return the concrete path resolving CONNECTED_LINK as applicable
  protected def resolveConnectedLink(path: IndirectDesignPath): ConnectedLinkResult = {
    path.splitConnectedLink match {
      case Some((connected, postfix)) =>
        connectedLink.getValue(ConnectedLinkRecord.ConnectedLink(connected)) match {
          case Some(connectedLinkPath) =>
            resolveConnectedLink(connectedLinkPath.asIndirect ++ postfix)
          case None =>
            ConnectedLinkResult.MissingConnectedLink(connected)
        }
      case None => ConnectedLinkResult.ResolvedPath(path)
    }
  }

  //
  // Processing Code
  //
  // Repeated does propagations as long as there is work to do, including both array available and param available.
  protected def update(): Unit = {
    while (connectedLink.getReady.nonEmpty) {
      val ready = connectedLink.getReady.head
      ready match {
        case ConnectedLinkRecord.Connected(port, nextPortToLink) => // propagate connected link
          connectedLink.setValue(ConnectedLinkRecord.ConnectedLink(port),
            connectedLink.getValue(ConnectedLinkRecord.ConnectedLink(nextPortToLink)).get)
          params.setValue(port.asIndirect + IndirectStep.ConnectedLink, BooleanValue(false))  // dummy value
        case _ => throw new IllegalArgumentException()
      }
      connectedLink.setValue(ready, DesignPath())
    }

    while (params.getReady.nonEmpty) {
      val constrTarget = params.getReady.head
      val assign = paramAssign(constrTarget)
      new ExprEvaluatePartial(this, assign.root).map(assign.value) match {
        case ExprResult.Result(result) =>
          params.setValue(constrTarget, result)
          onParamSolved(constrTarget, result)
          for (constrTargetEquals <- equality.getOrElse(constrTarget, mutable.Buffer())) {
            propagateEquality(constrTargetEquals, constrTarget, result)
          }
        case ExprResult.Missing(missing) =>  // account for CONNECTED_LINK prefix
          val missingCorrected = missing.map { path => resolveConnectedLink(path) match {
            case ConnectedLinkResult.ResolvedPath(path) => path
            case ConnectedLinkResult.MissingConnectedLink(portPath) => portPath.asIndirect + IndirectStep.ConnectedLink
          } }
          params.addNode(constrTarget, missingCorrected.toSeq, update = true)
      }
    }
  }

  protected def propagateEquality(dst: IndirectDesignPath, src: IndirectDesignPath, value: ExprValue): Unit = {
    if (params.getValue(dst).isDefined) {
      val record = discardOverassigns.getOrElseUpdate(dst, OverassignRecord())
      record.equals.add(src)
      return  // first set "wins"
    }

    params.setValue(dst, value)
    onParamSolved(dst, value)
    for (dstEquals <- equality.getOrElse(dst, mutable.Buffer())) {
      if (dstEquals != src) {  // ignore the backedge for propagation
        propagateEquality(dstEquals, dst, value)
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
      case init.ValInit.Val.Range(_) => classOf[RangeType]
      case init.ValInit.Val.Array(arrayType) => arrayType.`val` match {
        case init.ValInit.Val.Floating(_) => classOf[ArrayValue[FloatValue]]
        case init.ValInit.Val.Integer(_) => classOf[ArrayValue[IntValue]]
        case init.ValInit.Val.Boolean(_) => classOf[ArrayValue[BooleanValue]]
        case init.ValInit.Val.Text(_) => classOf[ArrayValue[TextValue]]
        case init.ValInit.Val.Range(_) => classOf[ArrayValue[RangeType]]
        case _ => throw new NotImplementedError(s"Unknown init array-type $decl")
      }
      case _ => throw new NotImplementedError(s"Unknown param declaration / init $decl")
    }
    paramTypes.put(target, paramType)
  }

  def setConnectedLink(linkPath: DesignPath, portPath: DesignPath): Unit = {
    connectedLink.setValue(ConnectedLinkRecord.ConnectedLink(portPath), linkPath)
    params.setValue(portPath.asIndirect + IndirectStep.ConnectedLink, BooleanValue(false))  // dummy value

    update()
  }

  def setConnection(toLinkPortPath: DesignPath, toBlockPortPath: DesignPath): Unit = {
    connectedLink.addNode(ConnectedLinkRecord.Connected(toBlockPortPath, toLinkPortPath),
      Seq(ConnectedLinkRecord.ConnectedLink(toLinkPortPath)))

    update()
  }

  /**
    * Adds a directed assignment (param <- expr) and propagates as needed
    */
  def addAssignExpr(target: IndirectDesignPath, targetExpr: expr.ValueExpr,
                    root: DesignPath, constrName: String,
                    sourceLocator: SourceLocator = new SourceLocator()): Unit = {
    require(target.splitConnectedLink.isEmpty, "cannot set CONNECTED_LINK")
    if (forcedParams.contains(target)) {
      return  // ignore forced params
    }
    val paramSourceRecord = (root, constrName, targetExpr)
    if (params.nodeDefinedAt(target)) {
      val record = discardOverassigns.getOrElseUpdate(target, OverassignRecord())
      record.assigns.add(paramSourceRecord)
      return  // first set "wins"
    }

    val assign = AssignRecord(target, root, targetExpr, sourceLocator)
    paramAssign.put(target, assign)
    paramSource.put(target, paramSourceRecord)
    params.addNode(target, Seq())  // first add is not update=True, actual processing happens in update()

    update()
  }

  /** Sets a value directly (without the expr), convenience wrapper around addAssignment
    */
  def addAssignValue(target: IndirectDesignPath, value: ExprValue,
                     root: DesignPath, constrName: String): Unit = {
    addAssignExpr(target, ExprBuilder.ValueExpr.Literal(value.toLit), root, constrName)
  }

  /** Adds a directed assignment (param1 <- param2), checking for root reachability
    */
  def addAssignEqual(target: IndirectDesignPath, source: IndirectDesignPath,
                     root: DesignPath, constrName: String): Unit = {
    val pathPrefix = root.asIndirect.toLocalPath.steps
    val (sourcePrefix, sourcePostfix) = source.toLocalPath.steps.splitAt(pathPrefix.length)
    require(sourcePrefix == pathPrefix)
    addAssignExpr(target, ExprBuilder.ValueExpr.Ref(LocalPath(steps = sourcePostfix)),
      root, constrName=constrName)
  }

  /** Sets a value directly, and ignores subsequent assignments.
    * TODO: this still preserve semantics that forbid over-assignment, even if those don't do anything
    */
  def setForcedValue(target: DesignPath, value: ExprValue, constrName: String): Unit = {
    val targetIndirect = target.asIndirect
    require(!params.nodeDefinedAt(targetIndirect), s"forced value must be set before assigns, prior ${paramSource(targetIndirect)}")
    addAssignValue(targetIndirect, value, DesignPath(), constrName)
    forcedParams += targetIndirect
  }

  /**
    * Adds a bidirectional equality (param1 == param2) and propagates as needed.
    * Equality cycles (ignoring backedges) will cause infinite recursion and is currently not checked.
    * TODO: detect cycles
    */
  def addEquality(param1: IndirectDesignPath, param2: IndirectDesignPath): Unit = {
    require(param1.splitConnectedLink.isEmpty, "cannot set CONNECTED_LINK")
    require(param2.splitConnectedLink.isEmpty, "cannot set CONNECTED_LINK")
    equality.getOrElseUpdate(param1, mutable.Buffer()) += param2
    equality.getOrElseUpdate(param2, mutable.Buffer()) += param1

    // the initial propagation (if applicable) is tricky
    // we assume that propagations between param1 and its equal nodes, and param2 and its equal nodes, are done prior
    (params.getValue(param1), params.getValue(param2)) match {
      case (Some(param1Value), Some(param2Value)) if param1Value == param2Value =>  // nop, already propagated
        // TODO: are these good semantics?
        // TODO: should this be recorded for debugging purposes / w/e?
      case (Some(param1Value), Some(param2Value)) =>
        val record1 = discardOverassigns.getOrElseUpdate(param1, OverassignRecord())
        record1.equals.add(param2)
        val record2 = discardOverassigns.getOrElseUpdate(param2, OverassignRecord())
        record2.equals.add(param1)
        // the equality is ignored otherwise
      case (Some(param1Value), None) => propagateEquality(param2, param1, param1Value)
      case (None, Some(param2Value)) => propagateEquality(param1, param2, param2Value)
      case (None, None) => // nothing to be done
    }

    update()
  }

  /**
    * Returns the value of a parameter, or None if it does not have a value (yet?).
    * Can be used to check if parameters are resolved yet by testing against None.
    */
  def getValue(param: IndirectDesignPath): Option[ExprValue] = {
    resolveConnectedLink(param) match {
      case ConnectedLinkResult.ResolvedPath(path) => params.getValue(path)
      case ConnectedLinkResult.MissingConnectedLink(missing) => None
    }

  }
  def getValue(param: DesignPath): Option[ExprValue] = {
    // TODO should this be an implicit conversion?
    getValue(param.asIndirect)
  }

  def getConnectedLink(port: DesignPath): Option[DesignPath] = {
    connectedLink.getValue(ConnectedLinkRecord.ConnectedLink(port))
  }

  /**
    * Returns the type (as a class of ExprValue) of a parameter.
    */
  def getType(param: DesignPath): Option[Class[_ <: ExprValue]] = {
    paramTypes.get(param)
  }

  /**
    * Returns all parameters with a definition (eg, ValInit) but missing a concrete assignment.
    * Ignores indirect references.
    */
  def getUnsolved: Set[DesignPath] = {
    paramTypes.keySet.toSet -- params.knownValueKeys.flatMap(DesignPath.fromIndirectOption)
  }

  def getAllSolved: Map[IndirectDesignPath, ExprValue] = params.toMap

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
      case (targetPath, RangeEmpty) =>
        paramSource.get(targetPath).map { case (root, constrName, value) =>
          CompilerError.EmptyRange(targetPath, root, constrName, value)
        }
    }.flatten.toSeq

    overassignErrors ++ emptyRangeErrors
  }
}
