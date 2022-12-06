package edg.wir

import edg.EdgirUtils.SimpleLibraryPath
import edg.wir.ProtoUtil._

import scala.collection.{SeqMap, mutable}
import edgir.init.init
import edgir.elem.elem
import edgir.ref.ref


sealed trait PortLike extends Pathable {
  def cloned: PortLike  // using clone directly causes an access error to Object.clone
  def toPb: elem.PortLike
}

object PortLike {
  import edg.IrPort
  def fromIrPort(irPort: IrPort): PortLike = irPort match {
    case IrPort.Port(port) => new Port(port)
    case IrPort.Bundle(bundle) => new Bundle(bundle)
    case irPort => throw new NotImplementedError(s"Can't construct PortLike from $irPort")
  }

  def fromLibraryPb(portLike: elem.PortLike): PortLike = portLike.`is` match {
    case elem.PortLike.Is.LibElem(like) => PortLibrary(like)
    case elem.PortLike.Is.Array(like) => new PortArray(like)
    case like => throw new NotImplementedError(s"Non-library sub-port $like")
  }
}

class Port(pb: elem.Port) extends PortLike
    with HasParams {
  override def cloned: Port = this  // immutable

  override def isElaborated: Boolean = true

  override def getParams: SeqMap[String, init.ValInit] = pb.params.toSeqMap

  override def resolve(suffix: Seq[String]): Pathable = suffix match {
    case Seq() => this
    case suffix => throw new InvalidPathException(s"No elements (of $suffix) in Port")
  }

  def toEltPb: elem.Port = {
    pb
  }

  def toPb: elem.PortLike = {
    elem.PortLike(`is`=elem.PortLike.Is.Port(toEltPb))
  }
}

class Bundle(pb: elem.Bundle) extends PortLike
    with HasMutablePorts with HasParams {
  override protected val ports: mutable.SeqMap[String, PortLike] = parsePorts(pb.ports)

  override def cloned: Bundle = {
    val cloned = new Bundle(pb)
    cloned.ports.clear()
    cloned.ports.addAll(ports.map { case (name, port) => name -> port.cloned })
    cloned
  }

  override def isElaborated: Boolean = true

  override def getParams: SeqMap[String, init.ValInit] = pb.params.toSeqMap

  override def resolve(suffix: Seq[String]): Pathable = suffix match {
    case Seq() => this
    case Seq(subname, tail@_*) =>
      if (ports.contains(subname)) {
        ports(subname).resolve(tail)
      } else {
        throw new InvalidPathException(s"No elements $subname (of $suffix) in Bundle ${pb.getSelfClass.toSimpleString}")
      }
  }

  def toEltPb: elem.Bundle = {
    pb.copy(
      ports=ports.view.mapValues(_.toPb).to(SeqMap).toPb,
    )
  }

  def toPb: elem.PortLike = {
    elem.PortLike(`is`=elem.PortLike.Is.Bundle(toEltPb))
  }
}

class PortArray(pb: elem.PortArray) extends PortLike with HasMutablePorts {
  override protected val ports: mutable.SeqMap[String, PortLike] = mutable.LinkedHashMap()
  var portsSet = false  // allow empty port arrays

  pb.contains match {
    case elem.PortArray.Contains.Ports(ports) => setPorts(parsePorts(ports.ports))
    case _ =>
  }

  override def cloned: PortArray = {
    val cloned = new PortArray(pb)
    cloned.ports.clear()
    cloned.ports.addAll(ports.map { case (name, port) => name -> port.cloned })
    cloned.portsSet = portsSet
    cloned
  }

  override def isElaborated: Boolean = portsSet && ports.values.forall(_.isElaborated)

  override def resolve(suffix: Seq[String]): Pathable = suffix match {
    case Seq() => this
    case Seq(subname, tail@_*) =>
      if (ports.contains(subname)) {
        ports(subname).resolve(tail)
      } else {
        throw new InvalidPathException(s"No element $subname (of $suffix) in PortArray ${pb.getSelfClass.toSimpleString}")
      }
  }

  def getType: ref.LibraryPath = pb.getSelfClass

  def setPorts(newPorts: SeqMap[String, PortLike]): Unit = {
    require(!portsSet)
    ports ++= newPorts
    portsSet = true
  }

  def toEltPb: elem.PortArray = {
    if (!portsSet) {
      pb
    } else {
      pb.copy(
        contains=elem.PortArray.Contains.Ports(elem.PortArray.Ports(
          ports.view.mapValues(_.toPb).to(SeqMap).toPb
        ))
      )
    }
  }

  override def toPb: elem.PortLike = {
    elem.PortLike(`is`=elem.PortLike.Is.Array(toEltPb))
  }
}

case class PortLibrary(target: ref.LibraryPath) extends PortLike {
  override def cloned: PortLibrary = this  // immutable

  def resolve(suffix: Seq[String]): Pathable = suffix match {
    case Seq() => this
    case _ => throw new InvalidPathException(s"Can't resolve $suffix into library ${target.toSimpleString}")
  }
  def toPb: elem.PortLike = elem.PortLike(elem.PortLike.Is.LibElem(target))
  override def isElaborated: Boolean = false
}
