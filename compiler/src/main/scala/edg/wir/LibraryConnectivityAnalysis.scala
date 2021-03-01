package edg.wir

import edg.IrPort
import edg.ref.ref
import edg.elem.elem


/** Provides connectivity analysis (connectable ports) on libraries.
  * Analysis is lazy, but the ports and links maps are gathered eagerly, so state is consistent with the
  * library as of creation time of this object.
  */
class LibraryConnectivityAnalysis(library: Library) {
  private val allPorts: Map[ref.LibraryPath, IrPort] = library.allPorts
  private val allLinks: Map[ref.LibraryPath, elem.Link] = library.allLinks

  private def getLeafLibPorts(portLike: elem.PortLike): Seq[ref.LibraryPath] = {
    portLike.is match {
      case elem.PortLike.Is.LibElem(value) => Seq(value)
      case elem.PortLike.Is.Array(array) =>
      require(array.superclasses.length == 1)
        Seq(array.superclasses.head)
      case isOther => throw new IllegalArgumentException(s"unexpected $isOther")
    }
  }

  lazy private val portToLinkMap: Map[ref.LibraryPath, ref.LibraryPath] = allLinks.toSeq
      .flatMap { case (linkPath, link) =>  // to (port path, link path) pairs
        link.ports.values.flatMap { port =>
          getLeafLibPorts(port)
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
      }.collect {  // discard invalid links
        case pair @ (portPath, Seq(link)) => (portPath, link)
      }.toMap

  /** Returns the link associated with a port, or None if it failed (eg, port not in library,
    * no associated links).
    */
  def linkOfPort(port: ref.LibraryPath): Option[ref.LibraryPath] = {
    portToLinkMap.get(port)
  }
}
