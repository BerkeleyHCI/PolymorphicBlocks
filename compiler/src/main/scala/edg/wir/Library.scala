package edg.wir

import edg.elem.elem
import edg.ref.ref
import edg.schema.schema
import edg.IrPort


class Library(pb: schema.Library) {
  // TODO implement namespace support
  val elts: Map[ref.LibraryPath, schema.Library.NS.Val.Type] = pb.root.getOrElse(schema.Library.NS())
      .members.map { case (name, member) =>
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

  // API functions
  //
  def getBlock(path: ref.LibraryPath): elem.HierarchyBlock = elts.get(path) match {
    case Some(schema.Library.NS.Val.Type.HierarchyBlock(member)) => member
    case Some(member) => throw new NoSuchElementException(s"Library element at $path not a block, got ${member.getClass}")
    case None => throw new NoSuchElementException(s"Library does not contain $path")
  }

  def getLink(path: ref.LibraryPath): elem.Link = elts.get(path) match {
    case Some(schema.Library.NS.Val.Type.Link(member)) => member
    case Some(member) => throw new NoSuchElementException(s"Library element at $path not a link, got ${member.getClass}")
    case None => throw new NoSuchElementException(s"Library does not contain $path")
  }

  def getPort(path: ref.LibraryPath): IrPort = elts.get(path) match {
    case Some(schema.Library.NS.Val.Type.Port(member)) => IrPort.Port(member)
    case Some(schema.Library.NS.Val.Type.Bundle(member)) => IrPort.Bundle(member)
    case Some(member) => throw new NoSuchElementException(s"Library element at $path not a port-like, got ${member.getClass}")
    case None => throw new NoSuchElementException(s"Library does not contain $path")
  }
}
