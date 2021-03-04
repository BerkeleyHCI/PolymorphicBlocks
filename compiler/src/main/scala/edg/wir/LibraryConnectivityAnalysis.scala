package edg.wir

import edg.ref.ref
import edg.elem.elem


object LibraryConnectivityAnalysis {
  // Shared library path to the base PortBridge class
  val portBridge = ref.LibraryPath(target=Some(ref.LocalStep(step=ref.LocalStep.Step.Name("edg_core.PortBlocks.PortBridge"))))
  val portBridgeOuterPort = "outer_port"
  val portBridgeLinkPort = "inner_link"

  // TODO these should go in utils or something?
  def getLibPortType(portLike: elem.PortLike): ref.LibraryPath = portLike.is match {
      case elem.PortLike.Is.LibElem(value) => value
      case elem.PortLike.Is.Array(array) =>
        require(array.superclasses.length == 1)
        array.superclasses.head
      case isOther => throw new IllegalArgumentException(s"unexpected $isOther")
  }
}


/** Provides connectivity analysis (connectable ports) on libraries.
  * Analysis is lazy, but the ports and links maps are gathered eagerly, so state is consistent with the
  * library as of creation time of this object.
  */
class LibraryConnectivityAnalysis(library: Library) {
  private val allBlocks: Map[ref.LibraryPath, elem.HierarchyBlock] = library.allBlocks
  private val allLinks: Map[ref.LibraryPath, elem.Link] = library.allLinks

  lazy private val portToLinkMap: Map[ref.LibraryPath, ref.LibraryPath] = allLinks.toSeq
      .flatMap { case (linkPath, link) =>  // expand to all combinations (port path, link path) pairs
        link.ports.values.map { port =>
          LibraryConnectivityAnalysis.getLibPortType(port)
        }.map {
          (_, linkPath)
        }
      } .groupBy(_._1)  // port path -> seq[(port path, link path) pairs]
      .mapValues(_.map(_._2).distinct)  // flatten into: port path -> seq[link path]
      .map {  // debugging pass only
        case pair @ (port, Seq(link)) => pair
        case pair @ (port, links) =>
          println(s"LibraryConnectivityAnalysis: discarding $port => $links")  // TODO better logging
          pair
      }.collect {  // take single link value (and discard invalid multiple link values)
        case pair @ (portPath, Seq(link)) => (portPath, link)
      }.toMap

  // exterior side port type -> (link side port type, port bridge type)
  lazy private val bridgedPortMap: Map[ref.LibraryPath, (ref.LibraryPath, ref.LibraryPath)] = allBlocks.toSeq
      .collect { case (blockType, block)   // filter by PortBridge superclass
        if block.superclasses.headOption.contains(LibraryConnectivityAnalysis.portBridge) =>
        (blockType,
            block.ports.get(LibraryConnectivityAnalysis.portBridgeOuterPort),
            block.ports.get(LibraryConnectivityAnalysis.portBridgeLinkPort))
      }.collect { // to (exterior port type, (link port type, port bridge type)) pairs
        case (blockType, Some(srcPort), Some(dstPort)) =>
          (LibraryConnectivityAnalysis.getLibPortType(srcPort),
              (LibraryConnectivityAnalysis.getLibPortType(dstPort), blockType))
      }.groupBy(_._1)  // aggregate by exterior port type
      .collect { case (srcPortType, pairs) if pairs.length == 1 =>  // discard overlaps
        srcPortType -> pairs.map(_._2).head
      }

  /** Returns the link associated with a port, or None if it failed (eg, port not in library,
    * no associated links).
    */
  def linkOfPort(port: ref.LibraryPath): Option[ref.LibraryPath] = {
    portToLinkMap.get(port)
  }

  /** Returns all the port types that can be connected to this link.
    * If connected is specified, returns additional port types that can be connected to this link, accounting
    * for the already-connected links.
    */
  def connectablePorts(linkPath: ref.LibraryPath,
                       connected: Seq[ref.LibraryPath] = Seq()): Option[Set[ref.LibraryPath]] = {
    val link = allLinks.getOrElse(linkPath, return None)
    val linkPortTypes = link.ports.values.map(_.is).toSeq

    val singlePorts = linkPortTypes.collect {
      case elem.PortLike.Is.LibElem(value) => value
    }
    val arrayPorts = linkPortTypes.collect {
      case elem.PortLike.Is.Array(array) =>
        require(array.superclasses.length == 1)
        array.superclasses.head
    }.toSet
    val nonArrayConnects = connected.filter(!arrayPorts.contains(_))  // ignore flexible-width array ports for counting

    // TODO might be more efficient to do mutable seq subtract ops
    val singlePortsCounts = singlePorts.groupBy(identity).mapValues(_.size)
    val connectedCounts = connected.groupBy(identity).mapValues(_.size)

    val remainingSinglePortsCounts = singlePortsCounts.map { case (path, count) =>
      connectedCounts.get(path) match {
        case Some(connectedCount) => (path, count - connectedCount)
        case None => (path, count)
      }
    }.filter(_._2 > 0)
    Some(remainingSinglePortsCounts.map(_._1).toSet ++ arrayPorts)
  }

  def bridgedPort(port: ref.LibraryPath): Option[ref.LibraryPath] = {
    bridgedPortMap.get(port).map(_._1)
  }
}
