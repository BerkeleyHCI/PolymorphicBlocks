package edg

import edg.ExprBuilder.ValueExpr
import edg.wir.LibraryConnectivityAnalysis
import edg.wir.ProtoUtil.{BlockProtoToSeqMap, PortProtoToSeqMap}
import edgir.elem.elem
import edgir.elem.elem.HierarchyBlock
import edgir.expr.expr
import edgir.ref.ref

import scala.collection.SeqMap

object ConnectTypes { // types of connections a port attached to a connection can be a part of
  // TODO structure this - materialize from constraint (using pre-lowered constraint?)
  // TODO materialize into constraints? - how to add tack this on to an existing IR graph
  trait Base {
    def getPortType(container: elem.HierarchyBlock): Option[ref.LibraryPath] // retrieves the type from the container
  }

  protected def typeOfSinglePort(portLike: elem.PortLike): Option[ref.LibraryPath] = portLike.is match {
    case elem.PortLike.Is.Port(port) => port.selfClass
    case elem.PortLike.Is.Bundle(port) => port.selfClass
    case _ => None
  }

  protected def typeOfArrayPort(portLike: elem.PortLike): Option[ref.LibraryPath] = portLike.is match {
    case elem.PortLike.Is.Array(array) => array.selfClass
    case _ => None
  }

  // including bridges
  case class BlockPort(blockName: String, portName: String) extends Base {
    override def getPortType(container: HierarchyBlock): Option[ref.LibraryPath] = {
      container.blocks.toSeqMap.get(blockName).flatMap(_.`type`.hierarchy)
        .flatMap(_.ports.get(portName))
        .flatMap(typeOfSinglePort)
    }
  }

  // single exported port only
  case class BoundaryPort(portName: String, innerNames: Seq[String]) extends Base {
    override def getPortType(container: HierarchyBlock): Option[ref.LibraryPath] = {
      val initPort = container.ports.get(portName)
      val finalPort = innerNames.foldLeft(initPort) { case (prev, innerName) =>
        prev.flatMap(_.is.bundle)
          .flatMap(_.ports.get(innerName))
      }
      finalPort.flatMap(typeOfSinglePort)
    }
  }

  // port array, connected as a unit; port array cannot be part of any other connection
  case class BlockVectorUnit(blockName: String, portName: String) extends Base {
    override def getPortType(container: HierarchyBlock): Option[ref.LibraryPath] = {
      container.blocks.toSeqMap.get(blockName).flatMap(_.`type`.hierarchy)
        .flatMap(_.ports.get(portName))
        .flatMap(typeOfArrayPort)
    }
  }

  // slice of a port array, connected using allocated / requested; other connections can involve the port array via slicing
  case class BlockVectorSlice(blockName: String, portName: String, suggestedIndex: Option[String]) extends Base {
    override def getPortType(container: HierarchyBlock): Option[ref.LibraryPath] = { // same as BlockVectorUnit case
      container.blocks.toSeqMap.get(blockName).flatMap(_.`type`.hierarchy)
        .flatMap(_.ports.get(portName))
        .flatMap(typeOfArrayPort)
    }
  }

  // port array, connected as a unit; port array cannot be part of any other connection
  case class BoundaryPortVectorUnit(portName: String) extends Base {
    override def getPortType(container: HierarchyBlock): Option[ref.LibraryPath] = {
      container.ports.get(portName)
        .flatMap(typeOfArrayPort)
    }
  }

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
  trait Base
  case object Single extends Base // connection between single ports, generates into link
  case object VectorUnit extends Base // connection with at least one full vector, generates into link array
  case object VectorCapable extends Base // connection which can be either - but is ambiguous and cannot be created
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
