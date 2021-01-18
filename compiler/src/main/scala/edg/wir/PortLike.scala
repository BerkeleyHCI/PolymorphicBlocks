package edg.wir

import edg.elem.elem
import edg.ref.ref

import scala.collection.mutable


trait PortLike extends Pathable {
  def toPb: elem.PortLike
}

object PortLike {
  import edg.IrPort
  def fromIrPort(irPort: IrPort, libraryPath: ref.LibraryPath): PortLike = irPort match {
    case IrPort.Port(port) => new Port(port, Seq(libraryPath))
    case IrPort.Bundle(port) => ???
    case irPort => throw new NotImplementedError(s"Can't construct PortLike from $irPort")
  }

}

class Port(pb: elem.Port, superclasses: Seq[ref.LibraryPath]) extends PortLike {
  override def isElaborated: Boolean = true

  override def resolve(suffix: Seq[String]): Pathable = suffix match {
    case Seq() => this
    case suffix => throw new InvalidPathException(s"No suffix $suffix in Port")
  }

  def toEltPb: elem.Port = {
    pb.copy(
      superclasses = superclasses
    )
  }

  def toPb: elem.PortLike = {
    elem.PortLike(`is`=elem.PortLike.Is.Port(toEltPb))
  }
}

class PortArray(pb: elem.PortArray) extends PortLike with HasMutablePorts {
  require(pb.superclasses.length == 1)

  override protected val ports: mutable.SeqMap[String, PortLike] = mutable.LinkedHashMap()

  override def isElaborated: Boolean = ports.nonEmpty

  override def resolve(suffix: Seq[String]): Pathable = suffix match {
    case Seq() => this
    case Seq(subname, tail@_*) =>
      if (ports.contains(subname)) {
        ports(subname).resolve(tail)
      } else {
        throw new InvalidPathException(s"No element $subname in Block")
      }
  }

  def getType: ref.LibraryPath = pb.superclasses.head

  def setPorts(newPorts: Map[String, PortLike]): Unit = {
    require(ports.isEmpty)
    ports ++= newPorts
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
