package edg.wir

import scala.collection.mutable

import edgir.init.init
import edgir.elem.elem
import edgir.ref.ref


sealed trait PortLike extends Pathable {
  def toPb: elem.PortLike
}

object PortLike {
  import edg.IrPort
  def fromIrPort(irPort: IrPort): PortLike = irPort match {
    case IrPort.Port(port) => new Port(port)
    case IrPort.Bundle(bundle) => new Bundle(bundle)
    case irPort => throw new NotImplementedError(s"Can't construct PortLike from $irPort")
  }
}

class Port(pb: elem.Port) extends PortLike
    with HasParams {
  override def isElaborated: Boolean = true

  override def getParams: Map[String, init.ValInit] = pb.params

  override def resolve(suffix: Seq[String]): Pathable = suffix match {
    case Seq() => this
    case suffix => throw new InvalidPathException(s"No suffix $suffix in Port")
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
  private val nameOrder = ProtoUtil.getNameOrder(pb.meta)
  override protected val ports: mutable.SeqMap[String, PortLike] = parsePorts(pb.ports, nameOrder)

  override def isElaborated: Boolean = true

  override def getParams: Map[String, init.ValInit] = pb.params

  override def resolve(suffix: Seq[String]): Pathable = suffix match {
    case Seq() => this
    case Seq(subname, tail@_*) =>
      if (ports.contains(subname)) {
        ports(subname).resolve(tail)
      } else {
        throw new InvalidPathException(s"No element $subname in Block")
      }
  }

  def toEltPb: elem.Bundle = {
    pb.copy(
      ports=ports.view.mapValues(_.toPb).toMap,
    )
  }

  def toPb: elem.PortLike = {
    elem.PortLike(`is`=elem.PortLike.Is.Bundle(toEltPb))
  }
}

class PortArray(pb: elem.PortArray) extends PortLike with HasMutablePorts {
  override protected val ports: mutable.SeqMap[String, PortLike] = mutable.LinkedHashMap()
  var portsSet = false  // allow empty port arrays

  override def isElaborated: Boolean = portsSet

  override def resolve(suffix: Seq[String]): Pathable = suffix match {
    case Seq() => this
    case Seq(subname, tail@_*) =>
      if (ports.contains(subname)) {
        ports(subname).resolve(tail)
      } else {
        throw new InvalidPathException(s"No element $subname in Block")
      }
  }

  def getType: ref.LibraryPath = pb.getSelfClass

  def setPorts(newPorts: Map[String, PortLike]): Unit = {
    require(ports.isEmpty)
    ports ++= newPorts
    portsSet = true
  }

  def toEltPb: elem.PortArray = {
    pb.copy(
      ports=ports.view.mapValues(_.toPb).toMap,
    )
  }

  override def toPb: elem.PortLike = {
    elem.PortLike(`is`=elem.PortLike.Is.Array(toEltPb))
  }
}

case class PortLibrary(target: ref.LibraryPath) extends PortLike {
  def resolve(suffix: Seq[String]): Pathable = throw new InvalidPathException(s"Can't resolve into library $target")
  def toPb: elem.PortLike = elem.PortLike(elem.PortLike.Is.LibElem(target))
  override def isElaborated: Boolean = false
}
