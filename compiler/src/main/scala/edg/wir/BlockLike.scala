package edg.wir

import edg.elem.elem
import edg.expr.expr
import edg.init.init
import edg.ref.ref

import scala.collection.mutable


trait BlockLike extends Pathable {
  def toPb: elem.BlockLike
}

case class Generator(dependencies: Seq[ref.LocalPath])

/**
  * "Wrapper" around a HierarchyBlock. Sub-trees of blocks and links are contained as a mutable map in this object
  * (instead of the proto), while everything else is kept in the proto.
  * BlockLike / LinkLike lib_elem are kept in the proto, unmodified.
  * This is to allow efficient transformation at any point in the design tree without re-writing the root.
  */
class Block(pb: elem.HierarchyBlock, superclasses: Seq[ref.LibraryPath]) extends BlockLike
    with HasMutablePorts with HasMutableBlocks with HasMutableLinks with HasMutableConstraints with HasParams {
  private val nameOrder = getNameOrder(pb.meta)
  override protected val ports: mutable.SeqMap[String, PortLike] = parsePorts(pb.ports, nameOrder)
  override protected val blocks: mutable.SeqMap[String, BlockLike] = parseBlocks(pb.blocks, nameOrder)
  override protected val links: mutable.SeqMap[String, LinkLike] = parseLinks(pb.links, nameOrder)
  override protected val constraints: mutable.SeqMap[String, expr.ValueExpr] = parseConstraints(pb.constraints, nameOrder)

  protected val generators: mutable.SeqMap[String, Generator] = {
    MapSort(pb.generators.mapValues { generatorPb =>
      require(generatorPb.conditions.length <= 1, "TODO: support OR-ing of conditions")
      val prereqs = generatorPb.conditions.headOption.getOrElse(elem.Generator.GeneratorCondition()).prereqs
      Generator(prereqs)
    }.toMap, nameOrder)
  }

  def getGenerators(): Map[String, Generator] = generators.toMap

  def getBlockClass: ref.LibraryPath = {
    require(superclasses.length == 1)
    superclasses.head
  }
  override def isElaborated: Boolean = true

  override def getParams: Map[String, init.ValInit] = pb.params

  override def resolve(suffix: Seq[String]): Pathable = suffix match {
    case Seq() => this
    case Seq(subname, tail@_*) =>
      if (ports.contains(subname)) {
        ports(subname).resolve(tail)
      } else if (blocks.contains(subname)) {
        blocks(subname).resolve(tail)
      } else if (links.contains(subname)) {
        links(subname).resolve(tail)
      } else {
        throw new InvalidPathException(s"No element $subname in Block")
      }
  }

  def toEltPb: elem.HierarchyBlock = {
    require(getUnelaboratedPorts.isEmpty && getUnelaboratedBlocks.isEmpty && getUnelaboratedLinks.isEmpty)
    pb.copy(
      superclasses=superclasses,
      ports=ports.view.mapValues(_.toPb).toMap,
      blocks=blocks.view.mapValues(_.toPb).toMap,
      links=links.view.mapValues(_.toPb).toMap,
      constraints=constraints.toMap,
    )
  }

  override def toPb: elem.BlockLike = {
    elem.BlockLike(`type`=elem.BlockLike.Type.Hierarchy(toEltPb))
  }
}
