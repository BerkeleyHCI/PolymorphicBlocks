package edg.wir
import edgir.expr.expr
import edgir.ref.ref

/** Manager for connected constraints, that provides an efficient way of getting constraints by block prefixes.
  * Contains references to and mutates the underlying block / link, which remains the single source of truth.
  * All mutation ops to these connected constraints must go through this object, since this maintains a sorted
  * reference to the underlying constraints.
  */
class ConnectedConstraintManager(container: HasMutableConstraints) {
  container.getConstraints.foreach { case (constrName, constr) => constr.expr match {

  } }

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
  def getByBlockPort(path: Seq[String]): Seq[(String, expr.ValueExpr, expr.ValueExpr.Expr)] = {
    container.getConstraints.map {  // extract expr
      case (constrName, constr) => (constrName, constr.expr)
    }.flatMap { case (constrName, constrExpr) => constrExpr match {
      case expr.ValueExpr.Expr.ExportedArray(exported) if refPrefixMatches(path, exported.getInternalBlockPort) =>
        Some((constrName, exported.getInternalBlockPort, constrExpr))
      case expr.ValueExpr.Expr.ConnectedArray(connected) if refPrefixMatches(path, connected.getBlockPort) =>
        Some((constrName, connected.getBlockPort, constrExpr))
      case expr.ValueExpr.Expr.Exported(exported) if refPrefixMatches(path, exported.getInternalBlockPort) =>
        Some((constrName, exported.getInternalBlockPort, constrExpr))
      case expr.ValueExpr.Expr.Connected(connected) if refPrefixMatches(path, connected.getBlockPort) =>
        Some((constrName, connected.getBlockPort, constrExpr))
      case _ => None
    } }.toSeq
  }
  // Gets all the constraints that involve the specified link-side path (direct reference or allocated) as a prefix,
  // returning the same format as getByBlockPort.
  // If includeExports=true, this also includes exported constraints matched by the internal port
  // (useful within a link context)
  def getByLinkPort(path: Seq[String], includeExports: Boolean):  Seq[(String, expr.ValueExpr, expr.ValueExpr.Expr)] = {
    container.getConstraints.map {  // extract expr
      case (constrName, constr) => (constrName, constr.expr)
    }.flatMap { case (constrName, constrExpr) => constrExpr match {
      case expr.ValueExpr.Expr.ExportedArray(exported)
          if includeExports && refPrefixMatches(path, exported.getInternalBlockPort) =>
        Some((constrName, exported.getInternalBlockPort, constrExpr))
      case expr.ValueExpr.Expr.ConnectedArray(connected) if refPrefixMatches(path, connected.getLinkPort) =>
        Some((constrName, connected.getLinkPort, constrExpr))
      case expr.ValueExpr.Expr.Exported(exported)
          if includeExports && refPrefixMatches(path, exported.getInternalBlockPort) =>
        Some((constrName, exported.getInternalBlockPort, constrExpr))
      case expr.ValueExpr.Expr.Connected(connected) if refPrefixMatches(path, connected.getLinkPort) =>
        Some((constrName, connected.getLinkPort, constrExpr))
      case _ => None
    } }.toSeq
  }
}
