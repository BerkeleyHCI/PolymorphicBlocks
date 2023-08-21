package edg.wir

import edgir.elem.elem

import scala.collection.SeqMap

/** Mildly analogous to the connect builder in the frontend HDL, this starts with a link, then ports can be added.
  * Immutable, added ports return a new ConnectBuilder object (if the add was successful) or None (if the ports cannot
  * be added). Accounts for bridging and vectors.
  *
  * TODO: support link array (array-array connections)
  */
class ConnectBuilder(library: LibraryConnectivityAnalysis, link: elem.Link, available_ports: SeqMap[String, elem.PortLike],
                     connected: Map[String, Seq[String]]) {
  // TODO link duplicate with available_ports?
  // should connected encode bridges?

  // Attempts to append new connected ports to this ConnectBuilder, returning a new ConnectBuilder if successful.
  def append(ports: (Seq[String], Seq[elem.PortLike])): Option[ConnectBuilder] = {
    // TODO ports need to encode bridges (exterior / interior status)
    ???
  }
}
