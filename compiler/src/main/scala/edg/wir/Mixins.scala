package edg.wir

import edg.elem.elem
import edg.expr.expr

import scala.collection.mutable


trait HasMutablePorts {
  protected val ports: mutable.Map[String, PortLike]

  def getUnelaboratedPorts: Map[String, PortLike] = ports.toMap.filter(!_._2.isElaborated)
  def elaborate(name: String, port: PortLike): Unit = {
    require(!ports(name).isElaborated && port.isElaborated)
    ports.put(name, port)
  }

  protected def parsePorts(pb: Map[String, elem.PortLike]): mutable.Map[String, PortLike] =
    mutable.HashMap[String, PortLike]() ++ pb.mapValues { _.`is` match {
      case elem.PortLike.Is.LibElem(like) => LibraryElement(like)
      case elem.PortLike.Is.Array(like) if like.ports.isEmpty => new PortArray(like)
      case like => throw new NotImplementedError(s"Non-library sub-port $like")
    }}
}

trait HasMutableBlocks {
  protected val blocks: mutable.Map[String, BlockLike]

  def getUnelaboratedBlocks: Map[String, BlockLike] = blocks.toMap.filter(!_._2.isElaborated)
  def elaborate(name: String, block: BlockLike): Unit = {
    require(!blocks(name).isElaborated && block.isElaborated)
    blocks.put(name, block)
  }

  protected def parseBlocks(pb: Map[String, elem.BlockLike]): mutable.Map[String, BlockLike] =
    mutable.HashMap[String, BlockLike]() ++ pb.mapValues { _.`type` match {
      case elem.BlockLike.Type.LibElem(like) => LibraryElement(like)
      case like => throw new NotImplementedError(s"Non-library sub-block $like")
    }}
}

trait HasMutableLinks {
  protected val links: mutable.Map[String, LinkLike]

  def getUnelaboratedLinks: Map[String, LinkLike] = links.toMap.filter(!_._2.isElaborated)
  def elaborate(name: String, link: LinkLike): Unit = {
    require(!links(name).isElaborated && link.isElaborated)
    links.put(name, link)
  }

  protected def parseLinks(pb: Map[String, elem.LinkLike]): mutable.Map[String, LinkLike] =
    mutable.HashMap[String, LinkLike]() ++ pb.mapValues { _.`type` match {
      case elem.LinkLike.Type.LibElem(like) => LibraryElement(like)
      case like => throw new NotImplementedError(s"Non-library sub-link $like")
    }}
}

trait HasMutableConstraints {
  protected val constraints: mutable.Map[String, expr.ValueExpr]

  def getConstraints: Map[String, expr.ValueExpr] = constraints.toMap

  def mapConstraint(name: String)(fn: expr.ValueExpr => expr.ValueExpr): Unit = {
    constraints.put(name, fn(constraints(name)))
  }
}
