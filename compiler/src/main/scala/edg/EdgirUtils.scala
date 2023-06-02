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
    // Returns the mapped port reference, where the function is defined at exactly one port reference
    def connectMapRef[T](fn: PartialFunction[expr.ValueExpr, T]): T = connection.expr match {
      case expr.ValueExpr.Expr.Connected(connected) =>
        (fn.isDefinedAt(connected.getBlockPort), fn.isDefinedAt(connected.getLinkPort)) match {
          case (true, false) => fn(connected.getBlockPort)
          case (false, true) => fn(connected.getLinkPort)
          case (true, true) => throw new IllegalArgumentException("block and link both matched")
          case (false, false) => throw new IllegalArgumentException("neither block nor link matched")
        }
      case expr.ValueExpr.Expr.Exported(exported) =>
        (fn.isDefinedAt(exported.getExteriorPort), fn.isDefinedAt(exported.getInternalBlockPort)) match {
          case (true, false) => fn(exported.getExteriorPort)
          case (false, true) => fn(exported.getInternalBlockPort)
          case (true, true) => throw new IllegalArgumentException("exterior and interior both matched")
          case (false, false) => throw new IllegalArgumentException("neither interior nor exterior matched")
        }
      case expr.ValueExpr.Expr.ExportedTunnel(exported) =>
        (fn.isDefinedAt(exported.getExteriorPort), fn.isDefinedAt(exported.getInternalBlockPort)) match {
          case (true, false) => fn(exported.getExteriorPort)
          case (false, true) => fn(exported.getInternalBlockPort)
          case (true, true) => throw new IllegalArgumentException("exterior and interior both matched")
          case (false, false) => throw new IllegalArgumentException("neither interior nor exterior matched")
        }
      case _ => throw new IllegalArgumentException
    }

    // Returns a new connection with exactly one port reference replaced with the partial function
    def connectUpdateRef(fn: PartialFunction[expr.ValueExpr, expr.ValueExpr]): expr.ValueExpr = connection.expr match {
      case expr.ValueExpr.Expr.Connected(connected) =>
        (fn.isDefinedAt(connected.getBlockPort), fn.isDefinedAt(connected.getLinkPort)) match {
          case (true, false) => connection.update(_.connected.blockPort := fn(connected.getBlockPort))
          case (false, true) => connection.update(_.connected.linkPort := fn(connected.getLinkPort))
          case (true, true) => throw new IllegalArgumentException("block and link both matched")
          case (false, false) => throw new IllegalArgumentException("neither block nor link matched")
        }
      case expr.ValueExpr.Expr.Exported(exported) =>
        (fn.isDefinedAt(exported.getExteriorPort), fn.isDefinedAt(exported.getInternalBlockPort)) match {
          case (true, false) => connection.update(_.exported.exteriorPort := fn(exported.getExteriorPort))
          case (false, true) => connection.update(_.exported.internalBlockPort := fn(exported.getInternalBlockPort))
          case (true, true) => throw new IllegalArgumentException("exterior and interior both matched")
          case (false, false) => throw new IllegalArgumentException("neither interior nor exterior matched")
        }
      case expr.ValueExpr.Expr.ExportedTunnel(exported) =>
        (fn.isDefinedAt(exported.getExteriorPort), fn.isDefinedAt(exported.getInternalBlockPort)) match {
          case (true, false) => connection.update(_.exportedTunnel.exteriorPort := fn(exported.getExteriorPort))
          case (false, true) =>
            connection.update(_.exportedTunnel.internalBlockPort := fn(exported.getInternalBlockPort))
          case (true, true) => throw new IllegalArgumentException("exterior and interior both matched")
          case (false, false) => throw new IllegalArgumentException("neither interior nor exterior matched")
        }
      case _ => throw new IllegalArgumentException
    }

    // Returns a new connection with the find endpoint replaced with replace. For array connects only.
    def arrayUpdateRef(fn: PartialFunction[expr.ValueExpr, expr.ValueExpr]): expr.ValueExpr = connection.expr match {
      case expr.ValueExpr.Expr.ConnectedArray(connected) =>
        (fn.isDefinedAt(connected.getBlockPort), fn.isDefinedAt(connected.getLinkPort)) match {
          case (true, false) => connection.update(_.connectedArray.blockPort := fn(connected.getBlockPort))
          case (false, true) => connection.update(_.connectedArray.linkPort := fn(connected.getLinkPort))
          case (true, true) => throw new IllegalArgumentException("block and link both matched")
          case (false, false) => throw new IllegalArgumentException("neither block nor link matched")
        }
      case expr.ValueExpr.Expr.ExportedArray(exported) =>
        (fn.isDefinedAt(exported.getExteriorPort), fn.isDefinedAt(exported.getInternalBlockPort)) match {
          case (true, false) => connection.update(_.exportedArray.exteriorPort := fn(exported.getExteriorPort))
          case (false, true) =>
            connection.update(_.exportedArray.internalBlockPort := fn(exported.getInternalBlockPort))
          case (true, true) => throw new IllegalArgumentException("exterior and interior both matched")
          case (false, false) => throw new IllegalArgumentException("neither interior nor exterior matched")
        }
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
