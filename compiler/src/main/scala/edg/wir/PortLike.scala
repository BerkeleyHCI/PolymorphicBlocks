package edg.wir
import edg.elem.elem
import edg.ref.ref

trait PortLike extends Pathable

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

  def toPb: elem.Port = {
    pb.copy(
      superclasses = superclasses
    )
  }
}
