package edg

import edgir.ref.ref
import edgir.expr.expr

object EdgirUtils {
  implicit class SimpleLibraryPath(path: ref.LibraryPath) {
    def toFullString: String = {
      path.target.map(_.step) match {
        case Some(ref.LocalStep.Step.Name(step)) => step
        case Some(ref.LocalStep.Step.Allocate(_)) => s"(unexpected allocate)"
        case Some(ref.LocalStep.Step.ReservedParam(step)) => s"(unexpected reserved_param ${step.toString})"
        case Some(ref.LocalStep.Step.Empty) => "(empty LocalStep)"
        case None => "(empty LibraryPath)"
      }
    }

    def toSimpleString: String = {
      toFullString.split('.').last
    }
  }

  // Provides a standardized way to access connection-type exprs (Array/Connected/Export)
  implicit class ConnectionExprUtils(connection: expr.ValueExpr) {
    // Extracts both endpoints from a connection expr as a list of ValueExpr.
    // May contain complex endpoints, eg MapExtract.
    def extractRefs: Seq[expr.ValueExpr] = connection.expr match {
      case expr.ValueExpr.Expr.Connected(connected) => Seq(connected.getBlockPort, connected.getLinkPort)
      case expr.ValueExpr.Expr.Exported(exported) => Seq(exported.getExteriorPort, exported.getInternalBlockPort)
      case expr.ValueExpr.Expr.ConnectedArray(connected) => Seq(connected.getBlockPort, connected.getLinkPort)
      case expr.ValueExpr.Expr.ExportedArray(exported) => Seq(exported.getExteriorPort, exported.getInternalBlockPort)
      case _ => throw new IllegalArgumentException
    }

    // Returns a new connection with the find endpoint replaced with replace. For single connects only.
    def connectWithReplacedRef(find: expr.ValueExpr, replace: expr.ValueExpr): expr.ValueExpr = connection.expr match {
      case expr.ValueExpr.Expr.Connected(connected) => Seq(connected.getBlockPort, connected.getLinkPort)
      case expr.ValueExpr.Expr.Exported(exported) => Seq(exported.getExteriorPort, exported.getInternalBlockPort)
      case _ => throw new IllegalArgumentException
    }

    // Returns a new connection with the find endpoint replaced with replace. For array connects only.
    def arrayWithReplacedRef(find: expr.ValueExpr, replace: expr.ValueExpr): expr.ValueExpr = connection.expr match {
      case expr.ValueExpr.Expr.ConnectedArray(connected) => Seq(connected.getBlockPort, connected.getLinkPort)
      case expr.ValueExpr.Expr.ExportedArray(exported) => Seq(exported.getExteriorPort, exported.getInternalBlockPort)
      case _ => throw new IllegalArgumentException
    }

    // For an ArrayConnect or ArrayExport, returns the single connection version (Connect, Export),
    // with endpoints unchanged.
    def asSingleConnection: expr.ValueExpr = connection.expr match {
      case expr.ValueExpr.Expr.ConnectedArray(connected) =>
        connection.withConnected(connected)
      case expr.ValueExpr.Expr.ExportedArray(exported) =>
        connection.withExported(exported)
      case _ => throw new IllegalArgumentException
    }
  }
}
