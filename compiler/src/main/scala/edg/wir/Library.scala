package edg.wir

import edg.EdgirUtils.SimpleLibraryPath
import edg.IrPort
import edg.compiler.ExprValue
import edg.util.Errorable
import edg.wir.ProtoUtil.{
  BlockProtoToSeqMap,
  BlockSeqMapToProto,
  ConstraintProtoToSeqMap,
  ConstraintSeqMapToProto,
  LinkProtoToSeqMap,
  LinkSeqMapToProto,
  ParamProtoToSeqMap,
  ParamSeqMapToProto,
  PortProtoToSeqMap,
  PortSeqMapToProto
}
import edgir.elem.elem
import edgir.ref.ref
import edgir.schema.schema

import scala.collection.SeqMap

/** API definition for a library
  */
trait Library {
  // getBlock can't be used on blocks that have refinements, since that's data that would be discarded
  // ignoreRefinements should only be used where the block's contents aren't relevant, for example for checking
  // subclass relations
  def getBlock(path: ref.LibraryPath, ignoreRefinements: Boolean = false): Errorable[elem.HierarchyBlock]
  def getLink(path: ref.LibraryPath): Errorable[elem.Link]
  def getPort(path: ref.LibraryPath): Errorable[IrPort]

  // Returns all elements of the specified type and their path.
  // If the library has a mutable backing, this may change over time.
  def allPorts: Map[ref.LibraryPath, IrPort]
  def allBlocks: Map[ref.LibraryPath, elem.HierarchyBlock]
  def allLinks: Map[ref.LibraryPath, elem.Link]

  def runGenerator(path: ref.LibraryPath, values: Map[ref.LocalPath, ExprValue]): Errorable[elem.HierarchyBlock]

  // wrapper around getBlock that handles mixins
  // if mixins is empty, this reduces down to getBlock
  def getBlock(path: ref.LibraryPath, mixins: Seq[ref.LibraryPath]): Errorable[elem.HierarchyBlock] = {
    getBlock(path) match {
      case baseBlock: Errorable.Error => baseBlock
      case Errorable.Success(baseBlock) =>
        val mixinBlockRaw = mixins.map(getBlock(_))
        val mixinBlockErrs = mixinBlockRaw.filter(_.isInstanceOf[Errorable.Error])
        if (mixinBlockErrs.nonEmpty) {
          mixinBlockErrs.head
        } else {
          val mixinBlocks = mixinBlockRaw.map(_.get)
          require(mixinBlocks.isEmpty || baseBlock.isAbstract, s"non-abstract block cannot have mixins")
          // TODO this is not the most accurate algorithm, but this doesn't matter since mixins are only created
          // for abstract parts or port indexing, and never in the final design (where a single concrete block is used)
          val mixedBlock = baseBlock
            .withPorts((baseBlock.ports.toSeqMap ++ mixinBlocks.map(_.ports.toSeqMap).fold(SeqMap())(_ ++ _)).toPb)
            .withParams((baseBlock.params.toSeqMap ++ mixinBlocks.map(_.params.toSeqMap).fold(SeqMap())(_ ++ _)).toPb)
            .withBlocks((baseBlock.blocks.toSeqMap ++ mixinBlocks.map(_.blocks.toSeqMap).fold(SeqMap())(_ ++ _)).toPb)
            .withLinks((baseBlock.links.toSeqMap ++ mixinBlocks.map(_.links.toSeqMap).fold(SeqMap())(_ ++ _)).toPb)
            .withConstraints((baseBlock.constraints.toSeqMap ++ mixinBlocks.map(_.constraints.toSeqMap).fold(SeqMap())(
              _ ++ _
            )).toPb)

          // take the last valid default refinement, TODO: support default refinements conditioned on multiple mixins
          val mixinsRefinements = mixinBlocks.flatMap(_.defaultRefinement)
          val refinedBlock = mixinsRefinements.lastOption match {
            case Some(mixinRefinement) => mixedBlock.withDefaultRefinement(mixinRefinement)
            case None => mixedBlock
          }

          Errorable.Success(refinedBlock)
        }
    }
  }
}

/** Non-mutable library based off the proto IR
  */
class EdgirLibrary(pb: schema.Library) extends Library {
  // TODO implement namespace support
  private val elts = pb.root.getOrElse(schema.Library.NS()).members.map { case (name, member) =>
    val libraryPath = ref.LibraryPath(target = Some(ref.LocalStep(step = ref.LocalStep.Step.Name(name))))
    member.`type` match {
      case schema.Library.NS.Val.Type.Port(_) => libraryPath -> member.`type`
      case schema.Library.NS.Val.Type.Bundle(_) => libraryPath -> member.`type`
      case schema.Library.NS.Val.Type.HierarchyBlock(_) => libraryPath -> member.`type`
      case schema.Library.NS.Val.Type.Link(_) => libraryPath -> member.`type`
      case schema.Library.NS.Val.Type.Namespace(_) =>
        throw new NotImplementedError(s"Library namespaces not yet supported, got $name = $member")
      case member => throw new NotImplementedError(s"Unknown library member $member")
    }
  }

  override def allBlocks: Map[ref.LibraryPath, elem.HierarchyBlock] = elts.collect {
    case (path, schema.Library.NS.Val.Type.HierarchyBlock(block)) => (path, block)
  }

  override def allPorts: Map[ref.LibraryPath, IrPort] = elts.collect {
    case (path, schema.Library.NS.Val.Type.Port(port)) => (path, IrPort.Port(port))
    case (path, schema.Library.NS.Val.Type.Bundle(port)) => (path, IrPort.Bundle(port))
  }

  override def allLinks: Map[ref.LibraryPath, elem.Link] = elts.collect {
    case (path, schema.Library.NS.Val.Type.Link(link)) => (path, link)
  }

  override def getBlock(path: ref.LibraryPath, ignoreRefinements: Boolean = false): Errorable[elem.HierarchyBlock] = {
    elts.get(path) match {
      case Some(schema.Library.NS.Val.Type.HierarchyBlock(member)) => Errorable.Success(member)
      case Some(member) => Errorable.Error(s"Library element at $path not a block, got ${member.getClass}")
      case None => Errorable.Error(s"Library does not contain $path")
    }
  }

  override def getLink(path: ref.LibraryPath): Errorable[elem.Link] = elts.get(path) match {
    case Some(schema.Library.NS.Val.Type.Link(member)) => Errorable.Success(member)
    case Some(member) => Errorable.Error(s"Library element at $path not a link, got ${member.getClass}")
    case None => Errorable.Error(s"Library does not contain $path")
  }

  override def getPort(path: ref.LibraryPath): Errorable[IrPort] = elts.get(path) match {
    case Some(schema.Library.NS.Val.Type.Port(member)) => Errorable.Success(IrPort.Port(member))
    case Some(schema.Library.NS.Val.Type.Bundle(member)) => Errorable.Success(IrPort.Bundle(member))
    case Some(member) => Errorable.Error(s"Library element at $path not a port-like, got ${member.getClass}")
    case None => Errorable.Error(s"Library does not contain $path")
  }

  override def runGenerator(
      path: ref.LibraryPath,
      values: Map[ref.LocalPath, ExprValue]
  ): Errorable[elem.HierarchyBlock] = {
    throw new IllegalArgumentException("Can't run generators in static library")
  }
}
