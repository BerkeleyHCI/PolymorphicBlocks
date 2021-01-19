package edg.compiler

import scala.collection.mutable
import scala.collection.Set
import edg.wir._
import edg.expr.expr
import edg.init.init
import edg.util.{DependencyGraph, MutableBiMap}


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

  // Assign statements are added to the dependency graph only when arrays are ready
  val params = DependencyGraph[IndirectDesignPath, ExprValue]()
  val paramTypes = new mutable.HashMap[DesignPath, Class[_ <: ExprValue]]  // only record types of authoritative elements

  // Equality, two entries per equality edge (one per direction / target)
  val equality = mutable.HashMap[IndirectDesignPath, mutable.Buffer[IndirectDesignPath]]()

  // Arrays are currently only defined on ports, and this is set once the array's length is known
  val arrayElts = DependencyGraph[IndirectDesignPath, Seq[String]]  // empty means not yet known


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
        for (constrTargetEquals <- equality.getOrElse(constrTarget, mutable.Buffer())) {
          propagateEquality(constrTargetEquals, constrTarget, value)
        }
      }
    }
  }

  protected def propagateEquality(dst: IndirectDesignPath, src: IndirectDesignPath, value: ExprValue): Unit = {
    require(params.getValue(dst).isEmpty, s"redefinition of $dst via equality from $src = $value")
    params.setValue(dst, value)
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
                    root: DesignPath, targetExpr: expr.ValueExpr, sourceLocator: SourceLocator): Unit = {
    require(!paramAssign.isDefinedAt(target), s"redefinition of $target via assignment")
    val assign = AssignRecord(target, root, targetExpr, sourceLocator)
    paramAssign.put(target, assign)

    val arrayDeps = new ExprArrayDependencies(root).map(targetExpr).map(IndirectDesignPath.fromDesignPath(_))
    arrayElts.addNode(target, arrayDeps.toSeq)

    update()
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
    arrayElts.setValue(IndirectDesignPath.fromDesignPath(target), elts)

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
    getValue(IndirectDesignPath.fromDesignPath(param))
  }

  /**
    * Returns the type (as a class of ExprValue) of a parameter.
    */
  def getType(param: DesignPath): Option[Class[_ <: ExprValue]] = {
    paramTypes.get(param)
  }

  def getArrayElts(target: DesignPath): Option[Seq[String]] = {
    arrayElts.getValue(IndirectDesignPath.fromDesignPath(target))
  }

  /**
    * Returns all parameters with a definition (eg, ValInit) but missing a concrete assignment.
    * Ignores indirect references.
    */
  def getUnsolved: Set[DesignPath] = {
    paramTypes.keySet -- params.knownValueKeys.flatMap(DesignPath.fromIndirectOption)
  }
}
