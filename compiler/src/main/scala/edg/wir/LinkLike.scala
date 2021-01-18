package edg.wir

import edg.elem.elem
import edg.expr.expr
import edg.ref.ref

import scala.collection.mutable


trait LinkLike extends Pathable

/**
  * Similar to Block, see documentation there.
  */
class Link(pb: elem.Link, superclasses: Seq[ref.LibraryPath]) extends LinkLike
    with HasMutablePorts with HasMutableLinks with HasMutableConstraints  {
  override protected val ports: mutable.Map[String, PortLike] = parsePorts(pb.ports)
  override protected val links: mutable.Map[String, LinkLike] = parseLinks(pb.links)
  override protected val constraints: mutable.Map[String, expr.ValueExpr] = mutable.HashMap() ++ pb.constraints


  override def isElaborated: Boolean = true


  override def resolve(suffix: Seq[String]): Pathable = suffix match {
    case Seq() => this
    case Seq(subname, tail@_*) =>
      if (ports.contains(subname)) {
        ports(subname).resolve(tail)
      } else if (links.contains(subname)) {
        links(subname).resolve(tail)
      } else {
        throw new InvalidPathException(s"No element $subname in Block")
      }
  }

  // Serializes this to protobuf
  def toPb: elem.Link = {
    require(getUnelaboratedPorts.isEmpty && getUnelaboratedLinks.isEmpty)
    pb.copy(
      superclasses=superclasses,
      ports=ports.view.mapValues {
        case port: Port => elem.PortLike(is=elem.PortLike.Is.Port(port.toPb))
        case port => throw new IllegalArgumentException(s"Unexpected port $port in serializing block")
      }.toMap,
      links=links.view.mapValues {
        case link: Link => elem.LinkLike(`type`=elem.LinkLike.Type.Link(link.toPb))
        case link => throw new IllegalArgumentException(s"Unexpected block $link in serializing block")
      }.toMap,
      constraints=constraints.toMap,
    )
  }
}
