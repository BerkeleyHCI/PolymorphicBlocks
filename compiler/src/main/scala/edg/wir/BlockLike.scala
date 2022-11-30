package edg.wir

import edg.EdgirUtils.SimpleLibraryPath
import edgir.elem.elem
import edgir.expr.expr
import edgir.init.init
import edgir.ref.ref
import edg.wir.ProtoUtil._
import edgir.ref.ref.LibraryPath

import scala.collection.{SeqMap, mutable}


sealed trait BlockLike extends Pathable {
  def cloned: BlockLike  // using clone directly causes an access error to Object.clone
  def toPb: elem.BlockLike
}

/**
  * "Wrapper" around a HierarchyBlock. Sub-trees of blocks and links are contained as a mutable map in this object
  * (instead of the proto), while everything else is kept in the proto.
  * BlockLike / LinkLike lib_elem are kept in the proto, unmodified.
  * This is to allow efficient transformation at any point in the design tree without re-writing the root.
  */
class Block(pb: elem.HierarchyBlock, unrefinedType: Option[ref.LibraryPath]) extends BlockLike
    with HasMutablePorts with HasMutableBlocks with HasMutableLinks with HasMutableConstraints with HasParams {
  override protected val ports: mutable.SeqMap[String, PortLike] = parsePorts(pb.ports)
  override protected val blocks: mutable.SeqMap[String, BlockLike] = parseBlocks(pb.blocks)
  override protected val links: mutable.SeqMap[String, LinkLike] = parseLinks(pb.links)
  override protected val constraints: mutable.SeqMap[String, expr.ValueExpr] = parseConstraints(pb.constraints)

  // creates a copy of this object
  override def cloned: Block = {
    val cloned = new Block(pb, unrefinedType)
    cloned.ports.clear()
    cloned.ports.addAll(ports.map { case (name, port) => name -> port.cloned })
    cloned.blocks.clear()
    cloned.blocks.addAll(blocks.map { case (name, block) => name -> block.cloned })
    cloned.links.clear()
    cloned.links.addAll(links.map { case (name, link) => name -> link.cloned })
    cloned.constraints.clear()
    cloned.constraints.addAll(constraints)
    cloned
  }

  override def isElaborated: Boolean = true

  def getBlockClass: LibraryPath = pb.getSelfClass

  override def getParams: SeqMap[String, init.ValInit] = pb.params.toSeqMap

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
        throw new InvalidPathException(s"No element $subname (of $suffix) in Block ${pb.getSelfClass.toSimpleString}")
      }
  }

  def toEltPb: elem.HierarchyBlock = {
    pb.copy(
      prerefineClass=unrefinedType match {
        case None => pb.prerefineClass
        case Some(prerefineClass) => Some(prerefineClass)
      },
      ports=ports.view.mapValues(_.toPb).to(SeqMap).toPb,
      blocks=blocks.view.mapValues(_.toPb).to(SeqMap).toPb,
      links=links.view.mapValues(_.toPb).to(SeqMap).toPb,
      constraints=constraints.toPb,
    )
  }

  override def toPb: elem.BlockLike = {
    elem.BlockLike(`type`=elem.BlockLike.Type.Hierarchy(toEltPb))
  }
}

// A generator version of the base block that can expand the block internals from a generator, subject to
// some constraints
class Generator(basePb: elem.HierarchyBlock, unrefinedType: Option[ref.LibraryPath])
    extends Block(basePb, unrefinedType) {
  require(basePb.generator.isDefined)

  var generatedPb: Option[elem.HierarchyBlock] = None

  blocks.clear()
  links.clear()
  constraints.clear()

  override def cloned: Generator = {  // TODO dedup w/ super (Block)? but Block.cloned returns a Block
    val cloned = new Generator(basePb, unrefinedType)
    cloned.ports.clear()
    cloned.ports.addAll(ports.map { case (name, port) => name -> port.cloned })
    cloned.blocks.clear()
    cloned.blocks.addAll(blocks.map { case (name, block) => name -> block.cloned })
    cloned.links.clear()
    cloned.links.addAll(links.map { case (name, link) => name -> link.cloned })
    cloned.constraints.clear()
    cloned.constraints.addAll(constraints)
    cloned.generatedPb = generatedPb
    cloned
  }

  // Apply the generated block on top of the generator stub, and returns the ports that have arrays newly defined
  def applyGenerated(pb: elem.HierarchyBlock): Seq[String] = {
    require(generatedPb.isEmpty, "can't generate twice")
    require(pb.generator.isEmpty, "generated can't define generators")

    // check that the generated block is consistent with the generator stub
    require(pb.getSelfClass == basePb.getSelfClass)
    require(pb.params == basePb.params)

    // expand port arrays that may be defined by the generator
    val basePbPorts = basePb.ports.toSeqMap
    val pbPorts = pb.ports.toSeqMap
    require(pbPorts.keySet == basePbPorts.keySet)
    val expandedPorts = pbPorts.flatMap { case (portName, portPb) => portPb.is match {
      case elem.PortLike.Is.Array(port) if port.contains.isPorts && !basePbPorts(portName).getArray.contains.isPorts =>
        val port = ports(portName).asInstanceOf[PortArray]
        require(!port.isElaborated)
        ports.put(portName, PortLike.fromLibraryPb(portPb))
        Some(portName)
      case _ => None
    } }

    require(blocks.isEmpty)
    require(links.isEmpty)
    require(constraints.isEmpty)
    blocks.addAll(parseBlocks(pb.blocks))
    links.addAll(parseLinks(pb.links))
    constraints.addAll(parseConstraints(pb.constraints))

    generatedPb = Some(pb)

    expandedPorts.toSeq
  }

  // returns a list of dependencies of this generator
  def getDependencies: Seq[ref.LocalPath] = {
    basePb.getGenerator.requiredParams
  }

  override def toEltPb: elem.HierarchyBlock = {
    generatedPb.getOrElse(basePb).copy(  // if the block did not generate, return the base w/ the generator field
      prerefineClass=unrefinedType match {
        case None => generatedPb.getOrElse(basePb).prerefineClass
        case Some(prerefineClass) => Some(prerefineClass)
      },
      ports=ports.view.mapValues(_.toPb).to(SeqMap).toPb,
      blocks=blocks.view.mapValues(_.toPb).to(SeqMap).toPb,
      links=links.view.mapValues(_.toPb).to(SeqMap).toPb,
      constraints=constraints.to(SeqMap).toPb,
    )
  }
}

case class BlockLibrary(target: ref.LibraryPath) extends BlockLike {
  override def cloned: BlockLibrary = this  // immutable

  def resolve(suffix: Seq[String]): Pathable = suffix match {
    case Seq() => this
    case _ => throw new InvalidPathException(s"Can't resolve $suffix into library ${target.toSimpleString}")
  }
  def toPb: elem.BlockLike = elem.BlockLike(elem.BlockLike.Type.LibElem(target))
  override def isElaborated: Boolean = false
}
