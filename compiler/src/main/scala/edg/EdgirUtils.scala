package edg

import edgir.common.common
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

  // Converts a string-to-string Map to a Metadata structure, for serializing data within the compiler.
  // Not meant to be a stable part of the public API, this format may change.
  def strMapToMeta(strMap: Map[String, String]): common.Metadata = {
    common.Metadata(meta =
      common.Metadata.Meta.Members(common.Metadata.Members(
        node = strMap.map { case (k, v) => k -> common.Metadata(meta = common.Metadata.Meta.TextLeaf(v)) }
      ))
    )
  }

  // Similar for strSeqToMeta, but for a sequence of strings, preserving order.
  def strSeqToMeta(strMap: Iterable[String]): common.Metadata = {
    common.Metadata(meta =
      common.Metadata.Meta.Members(common.Metadata.Members(
        node = strMap.zipWithIndex.map { case (value, i) =>
          i.toString -> common.Metadata(meta = common.Metadata.Meta.TextLeaf(value))
        }.toMap
      ))
    )
  }

  // Converts a Metadata object to a string-to-string Map structure, inverse of strMapToMeta.
  // Checks are strict, this crashes on invalidly formatted data
  def metaToStrMap(meta: common.Metadata): Map[String, String] = {
    meta.getMembers.node.map { case (k, v) => k -> v.getTextLeaf }
  }

  def metaToStrSeq(meta: common.Metadata): Seq[String] = {
    meta.getMembers.node.map { case (k, v) => k.toInt -> v.getTextLeaf }.toSeq.sortBy(_._1).map(_._2)
  }

  def metaInsertItem(base: Option[common.Metadata], key: String, value: common.Metadata): Option[common.Metadata] = {
    val baseMeta = base match {
      case None => common.Metadata()
      case Some(meta) => meta
    }
    require(baseMeta.meta.isMembers || baseMeta.meta.isEmpty) // must not be any other type that can be overwritten
    require(!baseMeta.getMembers.node.contains(key))
    Some(baseMeta.update(_.members.node :+= ((key, value))))
  }

  // from the meta field, returns the key metadata (if the metadata exists and is a dict with the field), or None
  def metaGetItem(base: Option[common.Metadata], key: String): Option[common.Metadata] = {
    base match {
      case Some(meta) => meta.meta match {
        case common.Metadata.Meta.Members(members) => members.node.get(key)
        case _ => None
      }
      case None => None
    }
  }
}
