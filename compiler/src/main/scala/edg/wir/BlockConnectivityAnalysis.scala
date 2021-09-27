package edg.wir

import edg.elem.elem
import edg.expr.expr
import edg.ref.ref
import edg.ref.ref.LocalPath


/** A connection to a link, from the point of view of (and relative to) some block
  */
sealed trait Connection {
  def getPorts: Seq[ref.LocalPath]
}
case object Connection {
  case class Disconnected() extends Connection {
    override def getPorts: Seq[ref.LocalPath] = Seq()
  }

  case class Link(
    linkName: String,
    linkConnects: Seq[(ref.LocalPath, String)],  // including bridge link-facing ports, as (port ref, constr name)
    bridgedExports: Seq[(ref.LocalPath, String, String)]  // (exterior port ref, bridge block name, constr name)
  ) extends Connection {
    override def getPorts: Seq[ref.LocalPath] = linkConnects.map(_._1) ++ bridgedExports.map(_._1)
  }
  case class Export(
    constraintName: String,
    exteriorPort: ref.LocalPath,
    innerBlockPort: ref.LocalPath
  ) extends Connection {
    override def getPorts: Seq[LocalPath] = Seq(exteriorPort, innerBlockPort)
  }
}


object BlockConnectivityAnalysis {
  def typeOfPortLike(portLike: elem.PortLike): ref.LibraryPath = portLike.is match {
    case elem.PortLike.Is.LibElem(lib) => lib
    case elem.PortLike.Is.Port(port) => port.getSelfClass
    case elem.PortLike.Is.Bundle(port) => port.getSelfClass
    case elem.PortLike.Is.Array(port) => port.getSelfClass
    case other => throw new IllegalArgumentException(s"Unexpected PortLike ${other.getClass}")
  }
}


/** Class that "wraps" a block to provide connectivity analysis for constraints and links inside the block.
  */
class BlockConnectivityAnalysis(block: elem.HierarchyBlock) {
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
        .view.mapValues{
          case Seq((exteriorRef, interiorRef, constrName)) => (interiorRef, constrName)
          case other => throw new IllegalArgumentException(s"unexpected grouped exports $other")
        }.toMap
  }

  // All exports, structured as inner port ref -> (exterior port ref, constr name)
  lazy val exportsByInner: Map[ref.LocalPath, (ref.LocalPath, String)] = {
    allExports.groupBy(_._2)
        .view.mapValues {
          case Seq((exteriorRef, interiorRef, constrName)) => (exteriorRef, constrName)
          case other => throw new IllegalArgumentException(s"unexpected grouped exports $other")
        }.toMap
  }

  // All exports, structured as inner block port ref -> (link port ref, constr name)
  lazy val connectsByBlock: Map[ref.LocalPath, (ref.LocalPath, String)] = {
    allConnects.groupBy(_._1)
        .view.mapValues {
          case Seq((innerRef, linkRef, constrName)) => (linkRef, constrName)
          case other => throw new IllegalArgumentException(s"unexpected grouped connects $other")
        }.toMap
  }

  // Returns all internal connected ports
  def getAllConnectedInternalPorts: Seq[ref.LocalPath] = allConnects.map(_._1) ++ allExports.map(_._2)
  // Returns all external (boundary) connected ports
  def getAllConnectedExternalPorts: Seq[ref.LocalPath] = allExports.map(_._1)

  private def blockIsBridge(block: elem.HierarchyBlock): Boolean = {
    // TODO superclass check once the infrastructure is there
    block.ports.keySet == Set(
      LibraryConnectivityAnalysis.portBridgeOuterPort,
      LibraryConnectivityAnalysis.portBridgeLinkPort)
  }

  /** If innerPortRef cconnects to a bridge block,
    * returns the exterior port ref, bridge name, and export constraint
    */
  private def bridgedToOuterOption(innerPortRef: ref.LocalPath): Option[(ref.LocalPath, String, String)] = {
    val bridgeName = innerPortRef.steps.head.getName  // name for the block in question, which MAY be a bridge
    block.blocks.get(bridgeName).map { blockLike =>  // filter by block exists
      blockLike.getHierarchy
    }.collect { case block if blockIsBridge(block) => // filter by is-bridge, transform to path, exported
      val bridgeOuterRef = ref.LocalPath().update(_.steps := Seq(
        ref.LocalStep().update(_.name := bridgeName),
        ref.LocalStep().update(_.name := LibraryConnectivityAnalysis.portBridgeOuterPort)
      ))
      exportsByInner.get(bridgeOuterRef)
    }.flatten
    .collect { case (exportedRef, exportConstrName) =>
      (exportedRef, bridgeName, exportConstrName)
    }
  }

  private def bridgedToInnerOption(outerPortRef: ref.LocalPath): Option[ref.LocalPath] = {
    val bridgeName = outerPortRef.steps.head.getName  // name for the block in question, which MAY be a bridge
    block.blocks.get(bridgeName).map { blockLike =>  // filter by block exists
      blockLike.getHierarchy
    }.collect { case block if blockIsBridge(block) => // filter by is-bridge, transform to path, exported
      ref.LocalPath().update(_.steps := Seq(
        ref.LocalStep().update(_.name := bridgeName),
        ref.LocalStep().update(_.name := LibraryConnectivityAnalysis.portBridgeLinkPort)
      ))
    }
  }

  def getConnectedToLink(linkName: String): Connection.Link = {
    val allBlockRefConstrs = allConnects.collect {  // filter by link name, and map to (port ref, constr name)
      case (blockPortRef, linkPortRef, constrName)
        if linkPortRef.steps.nonEmpty && linkPortRef.steps.head.getName == linkName =>
        (blockPortRef, constrName)
    }

    // Find all bridged exports
    val allExportRefBlockConstrs = allBlockRefConstrs.flatMap { case (blockPortRef, constrName) =>
      bridgedToOuterOption(blockPortRef)
    }

    Connection.Link(
      linkName,
      allBlockRefConstrs,
      allExportRefBlockConstrs
    )
  }

  /** Returns the Connection that portPath is part of, or None if it is not connected.
    */
  def getConnected(portRef: ref.LocalPath): Connection = {
    if (connectsByBlock.contains(portRef)) {
      require(!exportsByInner.contains(portRef), s"overconnected port $portRef")
      require(!exportsByOuter.contains(portRef), s"overconnected port $portRef")
      val (linkPortRef, constrName) = connectsByBlock(portRef)
      require(linkPortRef.steps.nonEmpty)
      val linkName = linkPortRef.steps.head.getName
      require(block.links.contains(linkName), s"reference to nonexistent link $linkName connected to $portRef")

      getConnectedToLink(linkName)
    } else if (exportsByInner.contains(portRef)) {
      require(!exportsByOuter.contains(portRef), s"overconnected port $portRef")
      val (exteriorRef, constrName) = exportsByInner(portRef)
      bridgedToInnerOption(portRef) match {
          // TODO: possible edge case with bridge with disconnected inner that would ignore the export
        case Some(bridgeInnerRef) => getConnected(bridgeInnerRef)
        case None => Connection.Export(constrName, exteriorRef, portRef)
      }
    } else if (exportsByOuter.contains(portRef)) {
      val (innerRef, constrName) = exportsByOuter(portRef)
      getConnected(innerRef)  // delegate to handle both export and bridged case
    } else {
      Connection.Disconnected()
    }
  }

  case class ConnectablePorts(innerPortTypes: Set[(ref.LocalPath, ref.LibraryPath)],
                              exteriorPortTypes: Set[(ref.LocalPath, ref.LibraryPath)])
  /** Returns all the connectable ports and types of this block,
    * including inner block ports (and their types) and exterior ports (and their non-bridged type)
    */
  def allConnectablePortTypes: ConnectablePorts = {
    val innerPortTypes = block.blocks.toSeq.flatMap { case (blockName, blockLike) =>
      blockLike.getHierarchy.ports.map { case (portName, portLike) =>
        val portRef = ref.LocalPath().update(_.steps := Seq(
          ref.LocalStep().update(_.name := blockName),
          ref.LocalStep().update(_.name := portName)
        ))
        (portRef, BlockConnectivityAnalysis.typeOfPortLike(portLike))
      }
    }.toSet
    val exteriorPortTypes = block.ports.toSeq.map { case (portName, portLike) =>
      val portRef = ref.LocalPath().update(_.steps := Seq(
        ref.LocalStep().update(_.name := portName)
      ))
      (portRef, BlockConnectivityAnalysis.typeOfPortLike(portLike))
    }.toSet
    ConnectablePorts(innerPortTypes, exteriorPortTypes)
  }
}
