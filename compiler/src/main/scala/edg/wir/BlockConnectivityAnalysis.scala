package edg.wir

import edg.elem.elem
import edg.expr.expr


sealed trait Connection
case object Connection {
  case class Link(
    link: DesignPath,
    linkConnects: Seq[DesignPath],  // including bridge link-facing ports
    bridgedExports: Seq[(DesignPath, DesignPath)]  // (bridge path, exterior port path)
  ) extends Connection
  case class Export(
    innerBlockPort: DesignPath,
    exteriorPort: DesignPath
  ) extends Connection
}


/** Class that "wraps" a block to provide connectivity analysis for constrants and links inside the block.
  */
class BlockConnectivityAnalysis(blockPath: DesignPath, block: elem.HierarchyBlock) {
  // All exports, structured as inner block port path -> exterior port path
  lazy val exportsByInner: Map[DesignPath, DesignPath] = block.constraints
      .values
      .map(_.expr)
      .collect {  // filter for exported only, into (inner block port path, exterior port path) pairs
        case expr.ValueExpr.Expr.Exported(exported) =>
          (blockPath ++ exported.getInternalBlockPort.getRef,
              blockPath ++ exported.getExteriorPort.getRef)
      }.groupBy(_._1)  // group by inner block
      .mapValues { pairs =>  // extract only exterior port path from value pairs seq
        require(pairs.size == 1)
        pairs.head._2
      }.toMap

  lazy val exportsByOuter: Map[DesignPath, DesignPath] = exportsByInner.map { case (k, v) => v -> k }

  // All connects, structured as inner block port path -> inner link path
  lazy val connectsByBlock: Map[DesignPath, DesignPath] = block.constraints
      .values
      .map(_.expr)
      .collect {  // filter for connected constraints only, and unpack
        case expr.ValueExpr.Expr.Connected(connected) =>
          (blockPath ++ connected.getBlockPort.getRef,
              blockPath ++connected.getLinkPort.getRef)
      }.groupBy(_._1)  // group by inner block port
      .mapValues { pairs =>  // extract only link path from value pairs seq
        require(pairs.size == 1)
        pairs.head._2
      }.toMap

  // Returns all internal connected ports
  def getAllConnectedInternalPorts: Set[DesignPath] = connectsByBlock.keySet
  // Returns all external (boundary) connected ports
  def getAllConnectedExternalPorts: Set[DesignPath] = exportsByInner.values.toSet

  /** Returns the Connection that portPath is part of, or None if it is not connected.
    */
  def getConnected(portPath: DesignPath): Option[Connection] = {
    ???
  }
}
