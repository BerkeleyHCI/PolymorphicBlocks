package edg.compiler

import edgir.elem.elem
import edgir.schema.schema
import edgir.ref.ref
import edg.wir.{ProtoUtil, DesignPath}
import edg.util.SeqMapSortableFrom._

import scala.collection.SeqMap


trait DesignMap[PortType, BlockType, LinkType] {
  // Top-level entry point
  def map(design: schema.Design): BlockType = {
    wrapBlock(DesignPath(), design.getContents)
  }

  // These methods handle how nodes are processed must be overridden by the user where appropriate
  // (left default, they will exception out, which may be desired behavior on unexpected node types)
  def mapPort(path: DesignPath, port: elem.Port): PortType = {
    throw new NotImplementedError(s"Undefined mapPort at $path")
  }
  def mapPortArray(path: DesignPath, port: elem.PortArray,
                   ports: SeqMap[String, PortType]): PortType = {
    throw new NotImplementedError(s"Undefined mapPortArray at $path")
  }
  def mapBundle(path: DesignPath, port: elem.Bundle,
                ports: SeqMap[String, PortType]): PortType = {
    throw new NotImplementedError(s"Undefined mapBundle at $path")
  }
  def mapPortLibrary(path: DesignPath, port: ref.LibraryPath): PortType = {
    throw new NotImplementedError(s"Undefined mapPortLibrary at $path")
  }

  def mapBlock(path: DesignPath, block: elem.HierarchyBlock,
               ports: SeqMap[String, PortType], blocks: SeqMap[String, BlockType],
               links: SeqMap[String, LinkType]): BlockType = {
    throw new NotImplementedError(s"Undefined mapBlock at $path")
  }
  def mapBlockLibrary(path: DesignPath, block: ref.LibraryPath): BlockType = {
    throw new NotImplementedError(s"Undefined mapBlockLibrary at $path")
  }

  def mapLink(path: DesignPath, link: elem.Link,
              ports: SeqMap[String, PortType], links: SeqMap[String, LinkType]): LinkType = {
    throw new NotImplementedError(s"Undefined mapLink at $path")
  }
  def mapLinkArray(path: DesignPath, link: elem.LinkArray,
                   ports: SeqMap[String, PortType], links: SeqMap[String, LinkType]): LinkType = {
    throw new NotImplementedError(s"Undefined mapLinkArray at $path")
  }
  def mapLinkLibrary(path: DesignPath, link: ref.LibraryPath): LinkType = {
    throw new NotImplementedError(s"Undefined mapLinkLibrary at $path")
  }

  // These methods provide default recursive processing functionality for child sub-tree elements,
  // and may be (but are not required to be) optionally overridden
  def wrapBundle(path: DesignPath, port: elem.Bundle): PortType = {
    val nameOrder = ProtoUtil.getNameOrder(port.meta)
    val ports = port.ports.map { case (name, elt) =>
      name -> wrapPortlike(path + name, elt) }
        .sortKeysFrom(nameOrder)
    mapBundle(path, port, ports)
  }

  def wrapPortArray(path: DesignPath, port: elem.PortArray): PortType = {
    val nameOrder = ProtoUtil.getNameOrder(port.meta)
    val ports = port.contains.ports.getOrElse(elem.PortArray.Ports()).ports.map { case (name, elt) =>
      name -> wrapPortlike(path + name, elt) }
        .sortKeysFrom(nameOrder)
    mapPortArray(path, port, ports)
  }

  def wrapPortlike(path: DesignPath, portLike: elem.PortLike): PortType = {
    portLike.is match {
      case elem.PortLike.Is.Port(port) => mapPort(path, port)
      case elem.PortLike.Is.Bundle(port) => wrapBundle(path, port)
      case elem.PortLike.Is.Array(port) => wrapPortArray(path, port)
      case elem.PortLike.Is.LibElem(port) => mapPortLibrary(path, port)
      case block => throw new NotImplementedError(s"Unknown BlockLike type at $path: $block")
    }
  }

  def wrapBlock(path: DesignPath, block: elem.HierarchyBlock): BlockType = {
    val nameOrder = ProtoUtil.getNameOrder(block.meta)
    val ports = block.ports.map { case (name, elt) =>
      name -> wrapPortlike(path + name, elt) }
        .sortKeysFrom(nameOrder)
    val blocks = block.blocks.map { case (name, elt) =>
      name -> wrapBlocklike(path + name, elt) }
        .sortKeysFrom(nameOrder)
    val links = block.links.map { case (name, elt) =>
      name -> wrapLinklike(path + name, elt) }
        .sortKeysFrom(nameOrder)
    mapBlock(path, block, ports, blocks, links)
  }

  def wrapBlocklike(path: DesignPath, blockLike: elem.BlockLike): BlockType = {
    blockLike.`type` match {
      case elem.BlockLike.Type.Hierarchy(block) => wrapBlock(path, block)
      case elem.BlockLike.Type.LibElem(block) => mapBlockLibrary(path, block)
      case block => throw new NotImplementedError(s"Unknown BlockLike type at $path: $block")
    }
  }

  def wrapLink(path: DesignPath, link: elem.Link): LinkType = {
    val nameOrder = ProtoUtil.getNameOrder(link.meta)
    val ports = link.ports.map { case (name, elt) =>
      name -> wrapPortlike(path + name, elt) }
        .sortKeysFrom(nameOrder)
    val links = link.links.map { case (name, elt) =>
      name -> wrapLinklike(path + name, elt) }
        .sortKeysFrom(nameOrder)
    mapLink(path, link, ports, links)
  }

  def wrapLinkArray(path: DesignPath, link: elem.LinkArray): LinkType = {
    val nameOrder = ProtoUtil.getNameOrder(link.meta)
    val ports = link.ports.map { case (name, elt) =>
      name -> wrapPortlike(path + name, elt) }
        .sortKeysFrom(nameOrder)
    val links = link.links.map { case (name, elt) =>
      name -> wrapLinklike(path + name, elt) }
        .sortKeysFrom(nameOrder)
    mapLinkArray(path, link, ports, links)
  }

  def wrapLinklike(path: DesignPath, linkLike: elem.LinkLike): LinkType = {
    linkLike.`type` match {
      case elem.LinkLike.Type.Link(link) => wrapLink(path, link)
      case elem.LinkLike.Type.Array(link) => wrapLinkArray(path, link)
      case elem.LinkLike.Type.LibElem(link) => mapLinkLibrary(path, link)
      case link => throw new NotImplementedError(s"Unknown LinkLike type at $path: $link")
    }
  }
}


trait DesignBlockMap[BlockType] extends DesignMap[Unit, BlockType, Unit] {
  // These methods should be overridden by the user
  def mapBlock(path: DesignPath, block: elem.HierarchyBlock,
               blocks: SeqMap[String, BlockType]): BlockType = {
    throw new NotImplementedError(s"Undefined mapBlock at $path")
  }
  override def mapBlockLibrary(path: DesignPath, block: ref.LibraryPath): BlockType = {
    throw new NotImplementedError(s"Undefined mapBlockLibrary at $path")
  }

  // These methods handle how nodes are processed must be overridden by the user where appropriate
  // (left default, they will exception out, which may be desired behavior on unexpected node types)
  final override def mapPort(path: DesignPath, port: elem.Port): Unit = {
  }
  final override def mapPortArray(path: DesignPath, port: elem.PortArray,
                   ports: SeqMap[String, Unit]): Unit = {
  }
  final override def mapBundle(path: DesignPath, port: elem.Bundle,
                ports: SeqMap[String, Unit]): Unit = {
  }
  final override def mapPortLibrary(path: DesignPath, port: ref.LibraryPath): Unit = {
  }

  final override def mapBlock(path: DesignPath, block: elem.HierarchyBlock,
               ports: SeqMap[String, Unit], blocks: SeqMap[String, BlockType],
               links: SeqMap[String, Unit]): BlockType = {
    mapBlock(path, block, blocks)
  }

  final override def mapLink(path: DesignPath, block: elem.Link,
              ports: SeqMap[String, Unit], links: SeqMap[String, Unit]): Unit = {
  }
  final override def mapLinkArray(path: DesignPath, block: elem.LinkArray,
                                  ports: SeqMap[String, Unit], links: SeqMap[String, Unit]): Unit = {
  }
  final override def mapLinkLibrary(path: DesignPath, link: ref.LibraryPath): Unit = {
  }
}
