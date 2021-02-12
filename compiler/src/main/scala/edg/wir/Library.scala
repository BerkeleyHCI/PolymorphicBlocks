package edg.wir

import scala.collection.{AbstractMap, MapOps}
import edg.elem.elem
import edg.ref.ref
import edg.schema.schema
import edg.IrPort
import edg.compiler.ExprValue
import edg.util.Errorable


/** API definition for a library
  */
trait Library {
  def isSubclassOf(subclass: ref.LibraryPath, superclass: ref.LibraryPath): Boolean = {
    if (subclass == superclass) {
      true
    } else {
      getBlock(subclass).superclasses.exists {
        isSubclassOf(_, superclass)
      }
    }
  }

  def getBlock(path: ref.LibraryPath): elem.HierarchyBlock
  def getLink(path: ref.LibraryPath): elem.Link
  def getPort(path: ref.LibraryPath): IrPort

  // Returns all elements of the specified type and their path.
  // If the library has a mutable backing, this may change over time.
  def allPorts: Map[ref.LibraryPath, IrPort]
  def allBlocks: Map[ref.LibraryPath, elem.HierarchyBlock]
  def allLinks: Map[ref.LibraryPath, elem.Link]

  def runGenerator(path: ref.LibraryPath, fnName: String,
                   values: Map[ref.LocalPath, ExprValue]): Errorable[elem.HierarchyBlock]
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

  override def getBlock(path: ref.LibraryPath): elem.HierarchyBlock = elts.get(path) match {
    case Some(schema.Library.NS.Val.Type.HierarchyBlock(member)) => member
    case Some(member) => throw new NoSuchElementException(s"Library element at $path not a block, got ${member.getClass}")
    case None => throw new NoSuchElementException(s"Library does not contain $path")
  }

  override def getLink(path: ref.LibraryPath): elem.Link = elts.get(path) match {
    case Some(schema.Library.NS.Val.Type.Link(member)) => member
    case Some(member) => throw new NoSuchElementException(s"Library element at $path not a link, got ${member.getClass}")
    case None => throw new NoSuchElementException(s"Library does not contain $path")
  }

  override def getPort(path: ref.LibraryPath): IrPort = elts.get(path) match {
    case Some(schema.Library.NS.Val.Type.Port(member)) => IrPort.Port(member)
    case Some(schema.Library.NS.Val.Type.Bundle(member)) => IrPort.Bundle(member)
    case Some(member) => throw new NoSuchElementException(s"Library element at $path not a port-like, got ${member.getClass}")
    case None => throw new NoSuchElementException(s"Library does not contain $path")
  }

  override def runGenerator(path: ref.LibraryPath, fnName: String,
                            values: Map[ref.LocalPath, ExprValue]): Errorable[elem.HierarchyBlock] = {
    throw new IllegalArgumentException("Can't run generators in static library")
  }
}
