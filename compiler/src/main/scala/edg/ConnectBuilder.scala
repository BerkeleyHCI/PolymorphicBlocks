package edg

import edg.wir.LibraryConnectivityAnalysis
import edgir.elem.elem

import scala.collection.SeqMap

object ConnectTypes { // types of connections a port attached to a connection can be a part of
  // TODO structure this - materialize from constraint (using pre-lowered constraint?)
  // TODO materialize into constraints? - how to add tack this on to an existing IR graph
  class BlockPort() // single port
  class BoundaryPort() // single port, either direct or through a bridge
  class BlockVectorUnit() // port array, connected as a unit; port array cannot be part of any other connection
  class BlockVectorSlice() // slice of a port array, connected using allocated / requested; other connections can involve the port array via slicing
}

object ConnectState { // state of a connect-in-progress
  class Single() // connection between single ports, generates into link
  class VectorUnit() // connection with at least one full vector and only with slices, generates into link array
  class VectorCapable() // connection which can be either - but is ambiguous and cannot be created
}

/** Mildly analogous to the connect builder in the frontend HDL, this starts with a link, then ports can be added.
  * Immutable, added ports return a new ConnectBuilder object (if the add was successful) or None (if the ports cannot
  * be added). Accounts for bridging and vectors.
  *
  * TODO: support link array (array-array connections)
  */
class ConnectBuilder(
    library: LibraryConnectivityAnalysis,
    link: elem.Link,
    available_ports: SeqMap[String, elem.PortLike],
    connected: Map[String, Seq[String]]
) {
  // TODO link duplicate with available_ports?
  // should connected encode bridges?

  // Attempts to append new connected ports to this ConnectBuilder, returning a new ConnectBuilder if successful.
  def append(ports: (Seq[String], Seq[elem.PortLike])): Option[ConnectBuilder] = {
    // TODO ports need to encode bridges (exterior / interior status)
    ???
  }
}
