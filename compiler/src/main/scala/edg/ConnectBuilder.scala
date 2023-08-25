package edg

import edg.EdgirUtils.SimpleLibraryPath
import edg.ExprBuilder.ValueExpr
import edg.util.SeqUtils
import edg.wir.LibraryConnectivityAnalysis
import edg.wir.ProtoUtil.{BlockProtoToSeqMap, PortProtoToSeqMap}
import edgir.elem.elem
import edgir.elem.elem.HierarchyBlock
import edgir.expr.expr
import edgir.ref.ref

import scala.collection.{SeqMap, mutable}

object ConnectTypes { // types of connections a port attached to a connection can be a part of
  // TODO structure this - materialize from constraint (using pre-lowered constraint?)
  // TODO materialize into constraints? - how to add tack this on to an existing IR graph
  sealed trait Base {
    def getPortType(container: elem.HierarchyBlock): Option[ref.LibraryPath] // retrieves the type from the container
  }

  sealed trait PortBase extends Base // base type for any port-valued connection
  sealed trait VectorBase extends Base // base type for any vector-valued connection
  sealed trait AmbiguousBase extends Base // base type for any connection which can be port- or vector-valued

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
  case class BlockPort(blockName: String, portName: String) extends PortBase {
    override def getPortType(container: HierarchyBlock): Option[ref.LibraryPath] = {
      container.blocks.toSeqMap.get(blockName).flatMap(_.`type`.hierarchy)
        .flatMap(_.ports.get(portName))
        .flatMap(typeOfSinglePort)
    }
  }

  // single exported port only
  case class BoundaryPort(portName: String, innerNames: Seq[String]) extends PortBase {
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
  case class BlockVectorUnit(blockName: String, portName: String) extends VectorBase {
    override def getPortType(container: HierarchyBlock): Option[ref.LibraryPath] = {
      container.blocks.toSeqMap.get(blockName).flatMap(_.`type`.hierarchy)
        .flatMap(_.ports.get(portName))
        .flatMap(typeOfArrayPort)
    }
  }

  sealed trait BlockVectorSliceBase extends Base {
    def blockName: String
    def portName: String
    override def getPortType(container: HierarchyBlock): Option[ref.LibraryPath] = { // same as BlockVectorUnit case
      container.blocks.toSeqMap.get(blockName).flatMap(_.`type`.hierarchy)
        .flatMap(_.ports.get(portName))
        .flatMap(typeOfArrayPort)
    }
  }

  // port-typed slice of a port array
  case class BlockVectorSlicePort(blockName: String, portName: String, suggestedIndex: Option[String])
      extends PortBase with BlockVectorSliceBase {}

  // vector-typed slice of a port array, connected using allocated / requested
  case class BlockVectorSliceVector(blockName: String, portName: String, suggestedIndex: Option[String])
      extends VectorBase with BlockVectorSliceBase {}

  // ambiguous slice of a port array, with no corresponding IR construct but used intuitively for GUI connections
  case class BlockVectorSlice(blockName: String, portName: String, suggestedIndex: Option[String])
      extends AmbiguousBase with BlockVectorSliceBase {}

  // port array, connected as a unit; port array cannot be part of any other connection
  case class BoundaryPortVectorUnit(portName: String) extends VectorBase {
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
      Some(BlockVectorSlicePort(blockName, portName, suggestedName))
    case _ => None // invalid / unrecognized form
  }

  protected def vectorBlockPortFromRef(ref: expr.ValueExpr): Option[Base] = ref match {
    case ValueExpr.Ref(Seq(blockName, portName)) => Some(BlockVectorUnit(blockName, portName))
    case ValueExpr.RefAllocate(Seq(blockName, portName), suggestedName) =>
      Some(BlockVectorSliceVector(blockName, portName, suggestedName))
    case _ => None // invalid / unrecognized form
  }
}

object ConnectMode { // state of a connect-in-progress
  trait Base
  case object Port extends Base // connection between single ports, generates into link
  case object Vector extends Base // connection with at least one full vector, generates into link array
  case object Ambiguous extends Base // connection which can be either - but is ambiguous and cannot be created
}

object ConnectBuilder {
  // creates a ConnectBuilder given all the connects to a link (found externally) and context data
  def apply(
      container: elem.HierarchyBlock,
      link: elem.Link, // link is needed to determine available connects
      constrs: Seq[expr.ValueExpr]
  ): Option[ConnectBuilder] = {
    val availableOpt = SeqUtils.getAllDefined(link.ports.toSeqMap.map { case (name, portLike) =>
      (name, portLike.is)
    }
      .map {
        case (name, elem.PortLike.Is.Port(port)) => port.selfClass.map((name, false, _))
        case (name, elem.PortLike.Is.Bundle(port)) => port.selfClass.map((name, false, _))
        case (name, elem.PortLike.Is.Array(array)) => array.selfClass.map((name, true, _))
        case _ => None
      }.toSeq)

    val constrConnectsOpt = SeqUtils.getAllDefined(constrs.map(ConnectTypes.fromConnect)).map(_.flatten)
    val constrConnectPortsOpt = constrConnectsOpt.flatMap { constrConnects =>
      SeqUtils.getAllDefined(constrConnects.map { constrConnect =>
        constrConnect.getPortType(container).map(portType => (constrConnect, portType))
      })
    }

    (availableOpt, constrConnectPortsOpt) match {
      case (Some(available), Some(constrConnectPorts)) =>
        new ConnectBuilder(container, available, Seq(), ConnectMode.Ambiguous).append(constrConnectPorts)
      case _ => None
    }
  }
}

/** Mildly analogous to the connect builder in the frontend HDL, this starts with a link, then ports can be added.
  * Immutable, added ports return a new ConnectBuilder object (if the add was successful) or None (if the ports cannot
  * be added). Accounts for bridging and vectors.
  */
class ConnectBuilder protected (
    container: elem.HierarchyBlock,
    val availablePorts: Seq[(String, Boolean, ref.LibraryPath)], // name, is array, port type
    val connected: Seq[(ConnectTypes.Base, ref.LibraryPath)], // connect type, used port type
    val connectMode: ConnectMode.Base
) {
  // TODO should connected encode bridges?

  // Attempts to append the connections (with attached port types) to the builder, returning a new builder
  // (if successful) or None (if not a legal connect).
  def append(newConnects: Seq[(ConnectTypes.Base, ref.LibraryPath)]): Option[ConnectBuilder] = {
    val availablePortsBuilder = availablePorts.to(mutable.ArrayBuffer)
    var connectModeBuilder = connectMode
    var failedToAllocate: Boolean = false

    newConnects.foreach { case (connect, portType) =>
      availablePortsBuilder.indexWhere(_._3 == portType) match {
        case -1 =>
          failedToAllocate = true
        case index =>
          val (portName, isArray, portType) = availablePortsBuilder(index)
          connect match {
            case _: ConnectTypes.PortBase =>
              if (connectModeBuilder == ConnectMode.Vector) {
                failedToAllocate = true
              } else {
                connectModeBuilder = ConnectMode.Port
              }
            case _: ConnectTypes.VectorBase =>
              if (connectModeBuilder == ConnectMode.Port) {
                failedToAllocate = true
              } else {
                connectModeBuilder = ConnectMode.Vector
              }
            case _: ConnectTypes.AmbiguousBase => // fine in either single or vector case
          }
          if (!isArray) {
            availablePortsBuilder.remove(index)
          }
      }
    }

    if (failedToAllocate) {
      None
    } else {
      Some(new ConnectBuilder(container, availablePortsBuilder.toSeq, connected ++ newConnects, connectModeBuilder))
    }
  }
}
