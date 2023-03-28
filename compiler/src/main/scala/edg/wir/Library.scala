package edg.wir

import edg.EdgirUtils.SimpleLibraryPath
import edg.IrPort
import edg.compiler.ExprValue
import edg.util.Errorable
import edg.wir.ProtoUtil.ParamProtoToSeqMap
import edgir.elem.elem
import edgir.ref.ref
import edgir.schema.schema


/** API definition for a library
  */
trait Library {
  // returns whether subclass is a subclass of (or equivalent to) superclass, traversing up the library
  // returns false if either subclass is missing
  def blockIsSubclassOf(subclass: ref.LibraryPath, superclass: ref.LibraryPath): Boolean = {
    if (subclass == superclass) {
      true
    } else {
      getBlock(subclass, true).toOption.map { elt => elt.superclasses.exists {
        blockIsSubclassOf(_, superclass)
      }}.getOrElse(false)
    }
  }

  // returns the top-most superclass that defines some parameter name
  // returns None if thisClass does not define the parameter, and errors out if there are multiple top-most superclasses
  def blockParamGetDefiningSuperclass(thisClass: ref.LibraryPath, paramName: String): Option[ref.LibraryPath] = {
    val thisBlock = getBlock(thisClass, true).get
    if (thisBlock.params.get(paramName).isEmpty) {
      return None
    }
    val definingSuperclasses = thisBlock.superclasses.flatMap { superclass =>
      blockParamGetDefiningSuperclass(superclass, paramName)
    }.distinct
    definingSuperclasses match {
      case Seq() => Some(thisClass)
      case Seq(baseClass) => Some(baseClass)
      case _ =>
        throw new IllegalArgumentException(s"multiple superclasses of ${thisClass.toSimpleString} defines $paramName")
    }
  }

  def getBlock(path: ref.LibraryPath): Errorable[elem.HierarchyBlock] = getBlock(path, false)
  // getBlock can't be used on blocks that have refinements, since that's data that would be discarded
  // this internal method allows that check to be ignored for cases where the block's definition isn't relevant,
  // for example for checking subclass relationships
  protected def getBlock(path: ref.LibraryPath, ignoreRefinements: Boolean): Errorable[elem.HierarchyBlock]
  def getLink(path: ref.LibraryPath): Errorable[elem.Link]
  def getPort(path: ref.LibraryPath): Errorable[IrPort]

  // Returns all elements of the specified type and their path.
  // If the library has a mutable backing, this may change over time.
  def allPorts: Map[ref.LibraryPath, IrPort]
  def allBlocks: Map[ref.LibraryPath, elem.HierarchyBlock]
  def allLinks: Map[ref.LibraryPath, elem.Link]

  def runGenerator(path: ref.LibraryPath, values: Map[ref.LocalPath, ExprValue]): Errorable[elem.HierarchyBlock]
}


/** Non-mutable library based off the proto IR
  */
class EdgirLibrary(pb: schema.Library) extends Library {
  // TODO implement namespace support
  private val elts = pb.root.getOrElse(schema.Library.NS()).members.map { case (name, member) =>
    val libraryPath = ref.LibraryPath(target=Some(ref.LocalStep(step=ref.LocalStep.Step.Name(name))))
    member.`type` match {
      case schema.Library.NS.Val.Type.Port(_) => libraryPath -> member.`type`
      case schema.Library.NS.Val.Type.Bundle(_) => libraryPath -> member.`type`
      case schema.Library.NS.Val.Type.HierarchyBlock(_) => libraryPath -> member.`type`
      case schema.Library.NS.Val.Type.Link(_) => libraryPath -> member.`type`
      case schema.Library.NS.Val.Type.Namespace(_) =>
        throw new NotImplementedError(s"Library namespaces not yet supported, got $name = $member")
      case member => throw new NotImplementedError(s"Unknown library member $member")
      } }

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

  override protected def getBlock(path: ref.LibraryPath, ignoreRefinements: Boolean): Errorable[elem.HierarchyBlock] = {
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

  override def runGenerator(path: ref.LibraryPath,
                            values: Map[ref.LocalPath, ExprValue]): Errorable[elem.HierarchyBlock] = {
    throw new IllegalArgumentException("Can't run generators in static library")
  }
}
