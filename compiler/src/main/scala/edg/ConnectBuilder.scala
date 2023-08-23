package edg

import edg.ExprBuilder.ValueExpr
import edg.wir.LibraryConnectivityAnalysis
import edgir.elem.elem
import edgir.expr.expr

import scala.collection.SeqMap

object ConnectTypes { // types of connections a port attached to a connection can be a part of
  // TODO structure this - materialize from constraint (using pre-lowered constraint?)
  // TODO materialize into constraints? - how to add tack this on to an existing IR graph
  class Base() {}

  case class BlockPort(blockName: String, portName: String) extends Base {}

  // single port, either direct or through a bridge; innerNames can either be a bundle element or vector index
  case class BoundaryPort(portName: String, innerNames: Seq[String]) extends Base {}

  // port array, connected as a unit; port array cannot be part of any other connection
  case class BlockVectorUnit(blockName: String, portName: String) extends Base {}

  // slice of a port array, connected using allocated / requested; other connections can involve the port array via slicing
  case class BlockVectorSlice(blockName: String, portName: String, suggestedIndex: Option[String]) extends Base {}

  // port array, connected as a unit; port array cannot be part of any other connection
  case class BoundaryPortVectorUnit(portName: String) extends Base {}

  // turns an unlowered (but optionally expanded) connect expression into a structured connect type, if the form matches
  // None means the expression failed to decode
  def fromConnect(constr: expr.ValueExpr): Option[Seq[Base]] = constr.expr match {
    // TODO support bridges - has multiple constraints that is merged into one connect unit
    case expr.ValueExpr.Expr.Connected(connected) =>
      singleBlockPortFromRef(connected.getBlockPort).map(Seq(_))
    case expr.ValueExpr.Expr.Exported(exported) =>
      val exterior = exported.getExteriorPort match {
        case ValueExpr.Ref(Seq(portName, innerNames @ _*)) => Some(BoundaryPort(portName, innerNames))
        case _ => None // invalid / unrecognized form
      }
      val interior = singleBlockPortFromRef(exported.getInternalBlockPort)
      (exterior, interior) match {
        case (Some(exterior), Some(interior)) => Some(Seq(exterior, interior))
        case _ => None // at least one failed to decode
      }
    case expr.ValueExpr.Expr.ConnectedArray(connectedArray) =>
      vectorBlockPortFromRef(connectedArray.getBlockPort).map(Seq(_))
    case expr.ValueExpr.Expr.ExportedArray(exportedArray) =>
      val exterior = exportedArray.getExteriorPort match {
        // exported array only supported as a unit, the compiler cannot materialize subarray indices
        case ValueExpr.Ref(Seq(portName)) => Some(BoundaryPortVectorUnit(portName))
        case _ => None // invalid / unrecognized form
      }
      val interior = vectorBlockPortFromRef(exportedArray.getInternalBlockPort)
      (exterior, interior) match {
        case (Some(exterior), Some(interior)) => Some(Seq(exterior, interior))
        case _ => None // at least one failed to decode
      }
    case _ => None
  }

  protected def singleBlockPortFromRef(ref: expr.ValueExpr): Option[Base] = ref match {
    case ValueExpr.Ref(Seq(blockName, portName)) => Some(BlockPort(blockName, portName))
    case ValueExpr.RefAllocate(Seq(blockName, portName), suggestedName) =>
      Some(BlockVectorSlice(blockName, portName, suggestedName))
    case _ => None // invalid / unrecognized form
  }

  protected def vectorBlockPortFromRef(ref: expr.ValueExpr): Option[Base] = ref match {
    case ValueExpr.Ref(Seq(blockName, portName)) => Some(BlockVectorUnit(blockName, portName))
    case ValueExpr.RefAllocate(Seq(blockName, portName), suggestedName) =>
      Some(BlockVectorSlice(blockName, portName, suggestedName))
    case _ => None // invalid / unrecognized form
  }
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
    linkName: Option[String],
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
