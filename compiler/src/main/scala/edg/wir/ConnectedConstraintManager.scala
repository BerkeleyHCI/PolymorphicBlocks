package edg.wir
import edgir.expr.expr
import edgir.ref.ref

import collection.mutable


sealed trait PortConnections

object PortConnections {
  case object NotConnected extends PortConnections
  case class SingleConnect(constrName: String, constr: expr.ValueExpr) extends PortConnections  // single direct connection, fully resolved
  case class ArrayConnect(constrName: String, constr: expr.ValueExpr) extends PortConnections  // array direct connection (without allocate)
  case class AllocatedConnect(singleConnects: Seq[(Option[String], String, expr.ValueExpr)],
                              arrayConnects: Seq[(Option[String], String, expr.ValueExpr)]
                             ) extends PortConnections  // all allocated connections, including single and array, as (allocated, constrName, constr)

  // Returns the PortConnections from the output of ConnectedConstraintManager.getBy(Block|Link)Port
  def apply(portPath: Seq[String], constrs: Seq[(String, expr.ValueExpr, expr.ValueExpr)]): PortConnections = {
    import edg.ExprBuilder.ValueExpr
    val constrsWithExprs = constrs.map {
      case (constrName, ref, constr) => (constrName, ref, constr, constr.expr)
    }
    val PortRef = ValueExpr.Ref(portPath: _*)

    constrsWithExprs match {
      case Seq() => NotConnected
      case Seq((constrName, PortRef, constr, expr.ValueExpr.Expr.Connected(_))) =>
        SingleConnect(constrName, constr)
      case Seq((constrName, PortRef, constr, expr.ValueExpr.Expr.Exported(_))) =>
        SingleConnect(constrName, constr)
      case Seq((constrName, PortRef, constr, expr.ValueExpr.Expr.ConnectedArray(_))) =>
        ArrayConnect(constrName, constr)
      case Seq((constrName, PortRef, constr, expr.ValueExpr.Expr.ExportedArray(_))) =>
        ArrayConnect(constrName, constr)
      case seq if seq.forall(elt => elt._2.expr.isRef && elt._2.getRef.steps.init == PortRef.getRef.steps &&
          elt._2.getRef.steps.last.step.isAllocate) =>
        val singleConnects = mutable.ListBuffer[(Option[String], String, expr.ValueExpr)]()
        val arrayConnects = mutable.ListBuffer[(Option[String], String, expr.ValueExpr)]()
        seq foreach { case (constrName, ref, constr, constrExpr) =>
          val allocateOption = if (ref.getRef.steps.last.getAllocate.isEmpty) None else Some(ref.getRef.steps.last.getAllocate)
          constrExpr match {
            case expr.ValueExpr.Expr.Connected(_) =>
              singleConnects.addOne((allocateOption, constrName, constr))
            case expr.ValueExpr.Expr.Exported(_) =>
              singleConnects.addOne((allocateOption, constrName, constr))
            case expr.ValueExpr.Expr.ConnectedArray(_) =>
              arrayConnects.addOne((allocateOption, constrName, constr))
            case expr.ValueExpr.Expr.ExportedArray(_) =>
              arrayConnects.addOne((allocateOption, constrName, constr))
            case _ =>
              throw new NotImplementedError(s"unknown connected form $constr")
          }
        }
        AllocatedConnect(singleConnects.toSeq, arrayConnects.toSeq)
      case seq => throw new NotImplementedError(s"unknown connections $seq")
    }
  }
}


/** Manager for connected constraints, that provides an efficient way of getting constraints by block prefixes.
  * Contains references to and mutates the underlying block / link, which remains the single source of truth.
  * All mutation ops to these connected constraints must go through this object, since this maintains a sorted
  * reference to the underlying constraints.
  */
class ConnectedConstraintManager(container: HasMutableConstraints) {
  // Returns true if the ref is considered a prefix of the path
  protected def refPrefixMatches(path: Seq[String], constrRef: expr.ValueExpr): Boolean = {
    val pathAsLocalSteps = path.map { step =>
      ref.LocalStep(step = ref.LocalStep.Step.Name(step))
    }
    constrRef.expr match {
      case expr.ValueExpr.Expr.Ref(ref) => ref.steps.startsWith(pathAsLocalSteps)
      case _ => throw new NotImplementedError("unknown connected ref")
    }
  }

  // Gets all the constraints that involve the specified block-side path (direct reference or allocated) as a prefix,
  // returning the constraint name, block-side reference, and entire constraint expression.
  // This includes all exported constraints, matching by the internal port.
  // TODO this can be optimized by pre-building an index of references involved in constraints
  def getByBlockPort(path: Seq[String]): Seq[(String, expr.ValueExpr, expr.ValueExpr)] = {
    container.getConstraints.map {  // extract expr
      case (constrName, constr) => (constrName, constr, constr.expr)
    }.flatMap { case (constrName, constr, constrExpr) => constrExpr match {
      case expr.ValueExpr.Expr.ExportedArray(exported) if refPrefixMatches(path, exported.getInternalBlockPort) =>
        Some((constrName, exported.getInternalBlockPort, constr))
      case expr.ValueExpr.Expr.ConnectedArray(connected) if refPrefixMatches(path, connected.getBlockPort) =>
        Some((constrName, connected.getBlockPort, constr))
      case expr.ValueExpr.Expr.Exported(exported) if refPrefixMatches(path, exported.getInternalBlockPort) =>
        Some((constrName, exported.getInternalBlockPort, constr))
      case expr.ValueExpr.Expr.Connected(connected) if refPrefixMatches(path, connected.getBlockPort) =>
        Some((constrName, connected.getBlockPort, constr))
      case _ => None
    } }.toSeq
  }
  // Gets all the constraints that involve the specified link-side path (direct reference or allocated) as a prefix,
  // returning the same format as getByBlockPort.
  // If includeExports=true, this also includes exported constraints matched by the internal port
  // (useful within a link context)
  def getByLinkPort(path: Seq[String], includeExports: Boolean):  Seq[(String, expr.ValueExpr, expr.ValueExpr)] = {
    container.getConstraints.map {  // extract expr
      case (constrName, constr) => (constrName, constr, constr.expr)
    }.flatMap { case (constrName, constr, constrExpr) => constrExpr match {
      case expr.ValueExpr.Expr.ExportedArray(exported)
          if includeExports && refPrefixMatches(path, exported.getInternalBlockPort) =>
        Some((constrName, exported.getInternalBlockPort, constr))
      case expr.ValueExpr.Expr.ConnectedArray(connected) if refPrefixMatches(path, connected.getLinkPort) =>
        Some((constrName, connected.getLinkPort, constr))
      case expr.ValueExpr.Expr.Exported(exported)
          if includeExports && refPrefixMatches(path, exported.getInternalBlockPort) =>
        Some((constrName, exported.getInternalBlockPort, constr))
      case expr.ValueExpr.Expr.Connected(connected) if refPrefixMatches(path, connected.getLinkPort) =>
        Some((constrName, connected.getLinkPort, constr))
      case _ => None
    } }.toSeq
  }

  def connectionsByBlockPort(path: Seq[String]): PortConnections =
    PortConnections(path, getByBlockPort(path))

  def connectionsByLinkPort(path: Seq[String], includeExports: Boolean): PortConnections =
    PortConnections(path, getByLinkPort(path, includeExports))
}
