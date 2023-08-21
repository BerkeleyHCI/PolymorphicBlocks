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

    // Return all the expanded constraints (or itself, if non-expanded) wrapped in a ValueExpr
    def expandedConstraints: Seq[expr.ValueExpr] = connection.expr match {
      case expr.ValueExpr.Expr.Connected(connectedContainer) =>
        connectedContainer.expanded match {
          case Seq() => Seq(connection)
          case Seq(single) => Seq(expr.ValueExpr(expr = expr.ValueExpr.Expr.Connected(single)))
          case _ => throw new IllegalArgumentException(s"unexpected multiple expanded in connected")
        }
      case expr.ValueExpr.Expr.Exported(exportedContainer) =>
        exportedContainer.expanded match {
          case Seq() => Seq(connection)
          case Seq(single) => Seq(expr.ValueExpr(expr = expr.ValueExpr.Expr.Exported(single)))
          case _ => throw new IllegalArgumentException(s"unexpected multiple expanded in exported")
        }
      case expr.ValueExpr.Expr.ConnectedArray(connectedContainer) =>
        require(connectedContainer.expanded.nonEmpty)
        connectedContainer.expanded.map(expanded => expr.ValueExpr(expr = expr.ValueExpr.Expr.Connected(expanded)))
      case expr.ValueExpr.Expr.ExportedArray(exportedContainer) =>
        require(exportedContainer.expanded.nonEmpty)
        exportedContainer.expanded.map(expanded => expr.ValueExpr(expr = expr.ValueExpr.Expr.Exported(expanded)))
      case _ => throw new IllegalArgumentException(s"unexpected connect type ${connection.expr.getClass}")
    }

    // For an array type, expands the expanded with multiple instances of the connection into expanded.
    // If there is a single expanded, uses that as the basis for expanded, otherwise uses the container constraint.
    // Multiple transform functions on each instance allow multiple rewrite rules per-instance.
    // TODO: this is very dynamic-typey with materializing the expanded if it doesn't exist, and this is a product
    // of the prior compiler structure which mutated the connect-in-place without a clear delineation of original vs.
    // expanded. This should be re-structured to be less dynamic-typey when the connect system is overhauled.
    def arrayExpandMultiRefs(indices: Seq[String])(fn: String => Seq[PartialFunction[expr.ValueExpr, expr.ValueExpr]])
        : expr.ValueExpr = connection.expr match {
      case expr.ValueExpr.Expr.ConnectedArray(connectedContainer) =>
        val baseInstance = connectedContainer.expanded match {
          case Seq() => connectedContainer
          case Seq(single) => single
          case _ => throw new IllegalArgumentException(s"unexpected multiple expanded in connected array")
        }
        val newExpanded = indices.map { index =>
          fn(index).foldLeft(baseInstance) { case (prev, fn) =>
            (fn.lift(prev.getBlockPort), fn.lift(prev.getLinkPort)) match {
              case (Some(newBlockPort), None) => prev.update(_.blockPort := newBlockPort)
              case (None, Some(newLinkPort)) => prev.update(_.linkPort := newLinkPort)
              case (Some(_), Some(_)) => throw new IllegalArgumentException("block and link both matched")
              case (None, None) => throw new IllegalArgumentException("neither block nor link matched")
            }
          }
        }
        connection.update(_.connectedArray.expanded := newExpanded)
      case expr.ValueExpr.Expr.ExportedArray(exportedContainer) =>
        val baseInstance = exportedContainer.expanded match {
          case Seq() => exportedContainer
          case Seq(single) => single
          case _ => throw new IllegalArgumentException(s"unexpected multiple expanded in exported array")
        }
        val newExpanded = indices.map { index =>
          fn(index).foldLeft(baseInstance) { case (prev, fn) =>
            (fn.lift(prev.getExteriorPort), fn.lift(prev.getInternalBlockPort)) match {
              case (Some(newExteriorPort), None) => prev.update(_.exteriorPort := newExteriorPort)
              case (None, Some(newInternalPort)) => prev.update(_.internalBlockPort := newInternalPort)
              case (Some(_), Some(_)) => throw new IllegalArgumentException("exterior and interior both matched")
              case (None, None) => throw new IllegalArgumentException("neither exterior nor interior matched")
            }
          }
        }
        connection.update(_.exportedArray.expanded := newExpanded)
      case _ => throw new IllegalArgumentException(s"unexpected array connect type ${connection.expr.getClass}")
    }

    // Returns a new connection with exactly one port reference replaced with the partial function.
    // Does not modify the container connect, creates a new connect in expanded or updates expanded in place
    // TODO: this is very dynamic-typey with materializing the expanded if it doesn't exist, and this is a product
    // of the prior compiler structure which mutated the connect-in-place without a clear delineation of original vs.
    // expanded. This should be re-structured to be less dynamic-typey when the connect system is overhauled.
    def connectExpandRef(fn: PartialFunction[expr.ValueExpr, expr.ValueExpr]): expr.ValueExpr = connection.expr match {
      case expr.ValueExpr.Expr.Connected(connectedContainer) =>
        val connected = connectedContainer.expanded match {
          case Seq() => connectedContainer
          case Seq(single) => single
          case _ => throw new IllegalArgumentException(s"unexpected multiple expanded in connected")
        }
        val newExpanded = (fn.lift(connected.getBlockPort), fn.lift(connected.getLinkPort)) match {
          case (Some(newBlockPort), None) => connected.update(_.blockPort := newBlockPort)
          case (None, Some(newLinkPort)) => connected.update(_.linkPort := newLinkPort)
          case (Some(_), Some(_)) => throw new IllegalArgumentException("block and link both matched")
          case (None, None) => throw new IllegalArgumentException("neither block nor link matched")
        }
        connection.update(_.connected.expanded := Seq(newExpanded))
      case expr.ValueExpr.Expr.Exported(exportedContainer) =>
        val exported = exportedContainer.expanded match {
          case Seq() => exportedContainer
          case Seq(single) => single
          case _ => throw new IllegalArgumentException(s"unexpected multiple expanded in exported")
        }
        val newExpanded = (fn.lift(exported.getExteriorPort), fn.lift(exported.getInternalBlockPort)) match {
          case (Some(newExteriorPort), None) => exported.update(_.exteriorPort := newExteriorPort)
          case (None, Some(newInternalPort)) => exported.update(_.internalBlockPort := newInternalPort)
          case (Some(_), Some(_)) => throw new IllegalArgumentException("exterior and interior both matched")
          case (None, None) => throw new IllegalArgumentException("neither interior nor exterior matched")
        }
        connection.update(_.exported.expanded := Seq(newExpanded))
      case expr.ValueExpr.Expr.ExportedTunnel(exportedContainer) =>
        val exported = exportedContainer.expanded match {
          case Seq() => exportedContainer
          case Seq(single) => single
          case _ => throw new IllegalArgumentException(s"unexpected multiple expanded in connected")
        }
        val newExpanded = (fn.lift(exported.getExteriorPort), fn.lift(exported.getInternalBlockPort)) match {
          case (Some(newExteriorPort), None) => exported.update(_.exteriorPort := newExteriorPort)
          case (None, Some(newInternalPort)) => exported.update(_.internalBlockPort := newInternalPort)
          case (Some(_), Some(_)) => throw new IllegalArgumentException("exterior and interior both matched")
          case (None, None) => throw new IllegalArgumentException("neither interior nor exterior matched")
        }
        connection.update(_.exportedTunnel.expanded := Seq(newExpanded))
      case expr.ValueExpr.Expr.ConnectedArray(connectedContainer) =>
        val bases = connectedContainer.expanded match {
          case Seq() => Seq(connectedContainer)
          case bases => bases
        }
        val newExpanded = bases.map { base =>
          (fn.lift(base.getBlockPort), fn.lift(base.getLinkPort)) match {
            case (Some(newBlockPort), None) => base.update(_.blockPort := newBlockPort)
            case (None, Some(newLinkPort)) => base.update(_.linkPort := newLinkPort)
            case (Some(_), Some(_)) => throw new IllegalArgumentException("block and link both matched")
            case (None, None) => throw new IllegalArgumentException("neither block nor link matched")
          }
        }
        connection.update(_.connectedArray.expanded := newExpanded)
      case expr.ValueExpr.Expr.ExportedArray(exportedContainer) =>
        val bases = exportedContainer.expanded match {
          case Seq() => Seq(exportedContainer)
          case bases => bases
        }
        val newExpanded = bases.map { base =>
          (fn.lift(base.getExteriorPort), fn.lift(base.getInternalBlockPort)) match {
            case (Some(newExteriorPort), None) => base.update(_.exteriorPort := newExteriorPort)
            case (None, Some(newInternalPort)) => base.update(_.internalBlockPort := newInternalPort)
            case (Some(_), Some(_)) => throw new IllegalArgumentException("exterior and interior both matched")
            case (None, None) => throw new IllegalArgumentException("neither interior nor exterior matched")
          }
        }
        connection.update(_.exportedArray.expanded := newExpanded)
      case _ => throw new IllegalArgumentException
    }

    // Returns a new connection with the find endpoint replaced with replace. For array connects only.
//    def arrayUpdateRef(fn: PartialFunction[expr.ValueExpr, expr.ValueExpr]): expr.ValueExpr = connection.expr match {
//      case expr.ValueExpr.Expr.ConnectedArray(connected) =>
//        (fn.isDefinedAt(connected.getBlockPort), fn.isDefinedAt(connected.getLinkPort)) match {
//          case (true, false) => connection.update(_.connectedArray.blockPort := fn(connected.getBlockPort))
//          case (false, true) => connection.update(_.connectedArray.linkPort := fn(connected.getLinkPort))
//          case (true, true) => throw new IllegalArgumentException("block and link both matched")
//          case (false, false) => throw new IllegalArgumentException("neither block nor link matched")
//        }
//      case expr.ValueExpr.Expr.ExportedArray(exported) =>
//        (fn.isDefinedAt(exported.getExteriorPort), fn.isDefinedAt(exported.getInternalBlockPort)) match {
//          case (true, false) => connection.update(_.exportedArray.exteriorPort := fn(exported.getExteriorPort))
//          case (false, true) =>
//            connection.update(_.exportedArray.internalBlockPort := fn(exported.getInternalBlockPort))
//          case (true, true) => throw new IllegalArgumentException("exterior and interior both matched")
//          case (false, false) => throw new IllegalArgumentException("neither interior nor exterior matched")
//        }
//      case _ => throw new IllegalArgumentException
//    }
  }

  // Converts a iterable of String (preserving order) to a Metadata structure, for serializing data internally.
  // Not meant to be a stable part of the public API, this format may change.
  def strSeqToMeta(strMap: Iterable[String]): common.Metadata = {
    common.Metadata(meta =
      common.Metadata.Meta.Members(common.Metadata.Members(
        node = strMap.zipWithIndex.map { case (value, i) =>
          i.toString -> common.Metadata(meta = common.Metadata.Meta.TextLeaf(value))
        }.toMap
      ))
    )
  }

  // Inverse of strSeqToMeta, including strict checks (will crash on badly formatted data)
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

  def mergeMeta(meta1: Option[common.Metadata], meta2: Option[common.Metadata]): Option[common.Metadata] = {
    (meta1, meta2) match {
      case (None, None) => None
      case (Some(meta1), None) => Some(meta1)
      case (None, Some(meta2)) => Some(meta2)
      case (Some(meta1), Some(meta2)) => (meta1.meta, meta2.meta) match {
          case (common.Metadata.Meta.Members(members1), common.Metadata.Meta.Members(members2)) =>
            val keys = members1.node.keys ++ members2.node.keys
            Some(common.Metadata(meta =
              common.Metadata.Meta.Members(common.Metadata.Members(
                node = keys.map { key =>
                  (members1.node.get(key), members2.node.get(key)) match {
                    case (Some(value1), None) => key -> value1
                    case (None, Some(value2)) => key -> value2
                    case (Some(value1), Some(value2)) if value1 == value2 => key -> value1
                    case _ => throw new IllegalArgumentException("cannot merge metadata with conflicting keys ")
                  }
                }.toMap
              ))
            ))
          case (members1, members2) => throw new IllegalArgumentException("cannot merge non-dict metadata")
        }
    }
  }
}
