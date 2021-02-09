package edg.wir

import edg.elem.elem
import edg.expr.expr
import edg.init.init
import edg.util.SeqMapSortableFrom._

import scala.collection.mutable


trait HasMutablePorts {
  protected val ports: mutable.SeqMap[String, PortLike]

  def getUnelaboratedPorts: Map[String, PortLike] = ports.toMap.filter(!_._2.isElaborated)
  def getElaboratedPorts: Map[String, PortLike] = ports.toMap.filter(_._2.isElaborated)
  def elaborate(name: String, port: PortLike): Unit = {
    require(!ports(name).isElaborated && port.isElaborated)
    ports.update(name, port)
  }

  protected def parsePorts(pb: Map[String, elem.PortLike], nameOrder: Seq[String]):
      mutable.SeqMap[String, PortLike] = {
    pb.mapValues { _.`is` match {
      case elem.PortLike.Is.LibElem(like) => PortLibrary(like)
      case elem.PortLike.Is.Array(like) if like.ports.isEmpty => new PortArray(like)
      case like => throw new NotImplementedError(s"Non-library sub-port $like")
    }}.toMap.sortKeysFrom(nameOrder).to(mutable.SeqMap)
  }
}

trait HasMutableBlocks {
  protected val blocks: mutable.SeqMap[String, BlockLike]

  def getUnelaboratedBlocks: Map[String, BlockLike] = blocks.toMap.filter(!_._2.isElaborated)
  def elaborate(name: String, block: BlockLike): Unit = {
    require(!blocks(name).isElaborated && block.isElaborated)
    blocks.update(name, block)
  }

  protected def parseBlocks(pb: Map[String, elem.BlockLike], nameOrder: Seq[String]):
  mutable.SeqMap[String, BlockLike] =
    pb.mapValues { _.`type` match {
      case elem.BlockLike.Type.LibElem(like) => BlockLibrary(like)
      case like => throw new NotImplementedError(s"Non-library sub-block $like")
    }}.toMap.sortKeysFrom(nameOrder).to(mutable.SeqMap)
}

trait HasMutableLinks {
  protected val links: mutable.SeqMap[String, LinkLike]

  def getUnelaboratedLinks: Map[String, LinkLike] = links.toMap.filter(!_._2.isElaborated)
  def elaborate(name: String, link: LinkLike): Unit = {
    require(!links(name).isElaborated && link.isElaborated)
    links.update(name, link)
  }

  protected def parseLinks(pb: Map[String, elem.LinkLike], nameOrder: Seq[String]):
      mutable.SeqMap[String, LinkLike] =
    pb.mapValues { _.`type` match {
      case elem.LinkLike.Type.LibElem(like) => LinkLibrary(like)
      case like => throw new NotImplementedError(s"Non-library sub-link $like")
    }}.toMap.sortKeysFrom(nameOrder).to(mutable.SeqMap)
}

trait HasMutableConstraints {
  import edg.util.SeqMapUtils

  protected val constraints: mutable.SeqMap[String, expr.ValueExpr]

  def getConstraints: Map[String, expr.ValueExpr] = constraints.toMap

  def mapConstraint(name: String)(fn: expr.ValueExpr => expr.ValueExpr): Unit = {
    constraints.update(name, fn(constraints(name)))
  }

  def mapMultiConstraint(name: String)(fn: expr.ValueExpr => Seq[(String, expr.ValueExpr)]): Unit = {
    SeqMapUtils.replaceInPlace(constraints, name, fn(constraints(name)))
  }

  protected def parseConstraints(pb: Map[String, expr.ValueExpr], nameOrder: Seq[String]):
      mutable.SeqMap[String, expr.ValueExpr] = {
    pb.sortKeysFrom(nameOrder).to(mutable.SeqMap)
  }

}

trait HasParams {
  def getParams: Map[String, init.ValInit]
}
