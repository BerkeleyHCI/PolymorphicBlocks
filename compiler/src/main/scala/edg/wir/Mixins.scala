package edg.wir

import edgir.elem.elem
import edgir.expr.expr
import edgir.init.init
import edg.util.SeqMapSortableFrom._

import scala.collection.{SeqMap, mutable}


trait HasMutablePorts {
  protected val ports: mutable.SeqMap[String, PortLike]

  def getPorts: SeqMap[String, PortLike] = ports.to(SeqMap)
  def elaborate(name: String, port: PortLike): Unit = {
    require(!ports(name).isElaborated && port.isElaborated)
    ports.update(name, port)
    require(ports(name).isElaborated)
  }

  protected def parsePorts(pb: SeqMap[String, elem.PortLike]):
      mutable.SeqMap[String, PortLike] = {
    pb.view.mapValues(PortLike.fromLibraryPb).to(mutable.SeqMap)
  }
}

trait HasMutableBlocks {
  protected val blocks: mutable.SeqMap[String, BlockLike]

  def getBlocks: SeqMap[String, BlockLike] = blocks.to(SeqMap)
  def elaborate(name: String, block: BlockLike): Unit = {
    require(!blocks(name).isElaborated && block.isElaborated)
    blocks.update(name, block)
    require(blocks(name).isElaborated)
  }

  protected def parseBlocks(pb: SeqMap[String, elem.BlockLike]):
      mutable.SeqMap[String, BlockLike] =
    pb.view.mapValues { _.`type` match {
      case elem.BlockLike.Type.LibElem(like) => BlockLibrary(like)
      case like => throw new NotImplementedError(s"Non-library sub-block $like")
    }}.to(mutable.SeqMap)
}

trait HasMutableLinks {
  protected val links: mutable.SeqMap[String, LinkLike]

  def getLinks: SeqMap[String, LinkLike] = links.to(SeqMap)
  def elaborate(name: String, link: LinkLike): Unit = {
    require(!links(name).isElaborated && link.isElaborated)
    links.update(name, link)
    require(links(name).isElaborated)
  }

  protected def parseLinks(pb: SeqMap[String, elem.LinkLike]):
      mutable.SeqMap[String, LinkLike] =
    pb.view.mapValues { _.`type` match {
      case elem.LinkLike.Type.LibElem(like) => LinkLibrary(like)
      case elem.LinkLike.Type.Array(like) => new LinkArray(like)
      case like => throw new NotImplementedError(s"Non-library sub-link $like")
    }}.to(mutable.SeqMap)
}

trait HasMutableConstraints {
  import edg.util.SeqMapUtils

  protected val constraints: mutable.SeqMap[String, expr.ValueExpr]

  def getConstraints: SeqMap[String, expr.ValueExpr] = constraints.to(SeqMap)

  def mapConstraint(name: String)(fn: expr.ValueExpr => expr.ValueExpr): Unit = {
    constraints.update(name, fn(constraints(name)))
  }

  // Replaces the constraint by name with the results of the map. Can be replaced with none, one, or several
  // new constraints. Returns a SeqMap of the new constraints.
  def mapMultiConstraint(name: String)(fn: expr.ValueExpr => Seq[(String, expr.ValueExpr)]):
      SeqMap[String, expr.ValueExpr] = {
    val newValues = fn(constraints(name))
    SeqMapUtils.replaceInPlace(constraints, name, newValues)
    newValues.to(SeqMap)
  }

  protected def parseConstraints(pb: SeqMap[String, expr.ValueExpr]):
      mutable.SeqMap[String, expr.ValueExpr] = {
    pb.to(mutable.SeqMap)
  }

}

trait HasParams {
  def getParams: SeqMap[String, init.ValInit]
}
