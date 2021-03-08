package edg.wir

import edg.elem.elem
import edg.expr.expr
import edg.ref.ref


/** A connection to a link, from the point of view of (and relative to) some block
  */
sealed trait Connection
case object Connection {
  case class Link(
    containingBlockPath: DesignPath,
    linkName: String,
    linkConnects: Seq[(ref.LocalPath, String)],  // including bridge link-facing ports, as (port ref, constr name)
    bridgedExports: Seq[(ref.LocalPath, String, String)]  // (exterior port ref, bridge block name, constr name)
  ) extends Connection
  case class Export(
    containingBlockPath: DesignPath,
    constraintName: String,
    exteriorPort: ref.LocalPath,
    innerBlockPort: ref.LocalPath
  ) extends Connection
}


/** Class that "wraps" a block to provide connectivity analysis for constraints and links inside the block.
  */
class BlockConnectivityAnalysis(blockPath: DesignPath, block: elem.HierarchyBlock) {
  lazy val allExports: Seq[(ref.LocalPath, ref.LocalPath, String)] = {  // external ref, internal ref, constr name
    block.constraints
        .map { case (name, constr) =>
          (name, constr.expr)
        }
        .collect {  // filter for exported only, into (inner block port path, exterior port path) pairs
          case (name, expr.ValueExpr.Expr.Exported(exported)) =>
            (exported.getExteriorPort.getRef, exported.getInternalBlockPort.getRef, name)
        }.toSeq
  }

  lazy val allConnects: Seq[(ref.LocalPath, ref.LocalPath, String)] = {  // block ref, link ref, constr name
    block.constraints
        .map { case (name, constr) =>
          (name, constr.expr)
        }
        .collect {  // filter for exported only, into (inner block port path, exterior port path) pairs
          case (name, expr.ValueExpr.Expr.Connected(connected)) =>
            (connected.getBlockPort.getRef, connected.getLinkPort.getRef, name)
        }.toSeq
  }

  // All exports, structured as exterior port ref -> (interior port ref, constr name)
  lazy val exportsByOuter: Map[ref.LocalPath, (ref.LocalPath, String)] = {
    allExports.groupBy(_._1)
        .mapValues {
          case Seq((exteriorRef, interiorRef, constrName)) => (interiorRef, constrName)
          case other => throw new IllegalArgumentException(s"unexpected grouped exports $other")
        }.toMap
  }

  // All exports, structured as inner port ref -> (exterior port ref, constr name)
  lazy val exportsByInner: Map[ref.LocalPath, (ref.LocalPath, String)] = {
    allExports.groupBy(_._2)
        .mapValues {
          case Seq((exteriorRef, interiorRef, constrName)) => (exteriorRef, constrName)
          case other => throw new IllegalArgumentException(s"unexpected grouped exports $other")
        }.toMap
  }

  // All exports, structured as inner block port ref -> (link port ref, constr name)
  lazy val connectsByBlock: Map[ref.LocalPath, (ref.LocalPath, String)] = {
    allConnects.groupBy(_._1)
        .mapValues {
          case Seq((innerRef, linkRef, constrName)) => (linkRef, constrName)
          case other => throw new IllegalArgumentException(s"unexpected grouped connects $other")
        }.toMap
  }

  // Returns all internal connected ports
  def getAllConnectedInternalPorts: Seq[ref.LocalPath] = allConnects.map(_._1) ++ allExports.map(_._2)
  // Returns all external (boundary) connected ports
  def getAllConnectedExternalPorts: Seq[ref.LocalPath] = allExports.map(_._1)

  /** Returns the Connection that portPath is part of, or None if it is not connected.
    */
  def getConnected(portRef: ref.LocalPath): Option[Connection] = {
    if (connectsByBlock.contains(portRef)) {
      require(!exportsByInner.contains(portRef), s"overconnected port $portRef")
      require(!exportsByOuter.contains(portRef), s"overconnected port $portRef")
      val (linkPortRef, constrName) = connectsByBlock(portRef)
      require(linkPortRef.steps.nonEmpty)
      val linkName = linkPortRef.steps.head.getName
      require(block.links.contains(linkName), s"reference to nonexistent link $linkName connected to $portRef")

      // Find all connects to the link
      val allBlockRefConstrs = allConnects.collect {  // filter by link name, and map to (port ref, constr name)
        case (blockPortRef, linkPortRef, constrName)
          if linkPortRef.steps.nonEmpty && linkPortRef.steps.head.getName == linkName =>
          (blockPortRef, constrName)
      }

      // Find all bridged exports
      val allExportRefBlockConstrs = allBlockRefConstrs.map {
        case (blockPortRef, constrName) => (blockPortRef, exportsByInner.get(blockPortRef))
      }.collect {
        case (blockPortRef, Some((exteriorPortRef, exportName))) =>
          (exteriorPortRef, blockPortRef.steps.head.getName, exportName)
      }

      Some(Connection.Link(
        blockPath, linkName,
        allBlockRefConstrs,
        allExportRefBlockConstrs
      ))
    } else if (exportsByInner.contains(portRef)) {
      require(!exportsByOuter.contains(portRef), s"overconnected port $portRef")
      val (exteriorRef, constrName) = exportsByInner(portRef)
      Some(Connection.Export(blockPath, constrName, exteriorRef, portRef))
    } else if (exportsByOuter.contains(portRef)) {
      val (innerRef, constrName) = exportsByOuter(portRef)
      Some(Connection.Export(blockPath, constrName, portRef, innerRef))
    } else {
      None
    }
  }
}
