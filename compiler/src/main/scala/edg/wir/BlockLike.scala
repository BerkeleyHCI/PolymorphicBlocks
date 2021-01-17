package edg.wir

import edg.elem.elem
import edg.expr.expr
import edg.init.init
import edg.ref.ref

import scala.collection.mutable


class InvalidPathException(message: String) extends Exception(message)

/**
  * Base trait for any element that can be resolved from a path, a wrapper around types in elem.proto and parameters.
  * Non-mutable, changes should be copy the object and return a new one.
  */
trait Pathable {
  /**
    * Resolves a LocalPath from here, returning the absolute path and the target element.
    * The target element must exist as an elaborated element (and not lib_elem).
    */
  def resolve(suffix: Seq[String]): Pathable

  // Disallow equals since it's probably not useful, and full subtree matches are expensive.
  // But can be allowed in the future, since the current behavior is strict.
  override def equals(that: Any): Boolean = throw new NotImplementedError("Can't do equality comparison on Pathable")
}

trait Port extends Pathable
trait Block extends Pathable
trait Link extends Pathable

class LibraryElement(target: ref.LibraryPath) extends Port with Block with Link {
  def resolve(suffix: Seq[String]): Pathable = throw new InvalidPathException("Can't resolve LibraryElement")
}

trait HasMutablePorts {
  protected val portsLib: mutable.HashMap[String, ref.LibraryPath]
  protected val ports: mutable.HashMap[String, Port]

  def getUnelaboratedPorts: Map[String, ref.LibraryPath] = portsLib.toMap  // return as immutable view
  def getUnelaboratedPort(name: String): ref.LibraryPath = portsLib(name)
  def elaborate(name: String, port: Port): Unit = {
    require(portsLib.isDefinedAt(name) && !ports.isDefinedAt(name))
    portsLib.remove(name)
    ports.put(name, port)
  }
}

trait HasMutableBlocks {
  protected val blocksLib: mutable.HashMap[String, ref.LibraryPath]
  protected val blocks: mutable.HashMap[String, Block]

  def getUnelaboratedBlocks: Map[String, ref.LibraryPath] = blocksLib.toMap  // return as immutable view
  def getUnelaboratedBlock(name: String): ref.LibraryPath = blocksLib(name)
  def elaborate(name: String, block: Block): Unit = {
    require(blocksLib.isDefinedAt(name) && !blocks.isDefinedAt(name))
    blocksLib.remove(name)
    blocks.put(name, block)
  }
}

trait HasMutableLinks {
  protected val linksLib: mutable.HashMap[String, ref.LibraryPath]
  protected val links: mutable.HashMap[String, Link]

  def getUnelaboratedLinks: Map[String, ref.LibraryPath] = linksLib.toMap  // return as immutable view
  def getUnelaboratedLink(name: String): ref.LibraryPath = linksLib(name)
  def elaborate(name: String, link: Link): Unit = {
    require(linksLib.isDefinedAt(name) && !links.isDefinedAt(name))
    linksLib.remove(name)
    links.put(name, link)
  }
}


/**
  * "Wrapper" around a HierarchyBlock. Sub-trees of blocks and links are contained as a mutable map in this object
  * (instead of the proto), while everything else is kept in the proto.
  * BlockLike / LinkLike lib_elem are kept in the proto, unmodified.
  * This is to allow efficient transformation at any point in the design tree without re-writing the root.
  */
case class Block(pb: elem.HierarchyBlock) extends Pathable with HasMutablePorts with HasMutableBlocks with HasMutableLinks {
  override protected val portsLib = mutable.HashMap[String, ref.LibraryPath]() ++ pb.blocks.collect { case (name, like) =>
    like.`type` match {
      case elem.BlockLike.Type.LibElem(like) => name -> like
      case like => throw new NotImplementedError(s"Block with non-library sub-block $like")
    }
  }
  override protected val ports = mutable.HashMap[String, Port]()

  override protected val blocksLib = mutable.HashMap[String, ref.LibraryPath]() ++ pb.blocks.collect { case (name, like) =>
    like.`type` match {
      case elem.BlockLike.Type.LibElem(like) => name -> like
      case like => throw new NotImplementedError(s"Block with non-library sub-block $like")
    }
  }
  override protected val blocks = mutable.HashMap[String, Block]()

  override protected val linksLib = mutable.HashMap[String, ref.LibraryPath]() ++ pb.links.collect { case (name, like) =>
    like.`type` match {
      case elem.LinkLike.Type.LibElem(like) => name -> like
      case like => throw new NotImplementedError(s"Block with non-library sub-link $like")
    }
  }
  override protected val links = mutable.HashMap[String, Link]()

  private val constraints = mutable.HashMap[String, expr.ValueExpr]() ++ pb.constraints

  def getParams: Map[String, init.ValInit] = pb.params  // immutable

  override def resolve(suffix: Seq[String]): Pathable = {
    suffix match {
      case Seq() => this
      case Seq(subname, tail@_*) =>
        if (blocks.contains(subname)) {
          blocks(subname).resolve(tail)
        } else if (links.contains(subname)) {
          links(subname).resolve(tail)
        } else {
          throw new InvalidPathException(s"No element $subname in Block")
        }
    }
  }

  // Serializes this to protobuf
  def toPb: elem.HierarchyBlock = {
    require(blocksLib.isEmpty && linksLib.isEmpty)
    ???
  }
}

/**
  * Similar to Block, see documentation there.
  */
case class Link(var pb: elem.Link) extends Pathable with HasMutableLinks {
  override protected val linksLib = mutable.HashMap[String, ref.LibraryPath]() ++ pb.links.collect { case (name, like) =>
    like.`type` match {
      case elem.LinkLike.Type.LibElem(like) => name -> like
      case like => throw new NotImplementedError(s"Block with non-library sub-link $like")
    }
  }
  override protected val links = mutable.HashMap[String, Link]()


  override def resolve(suffix: Seq[String]): Pathable = {
    suffix match {
      case Seq() => this
      case Seq(subname, tail@_*) =>
        if (links.contains(subname)) {
          links(subname).resolve(tail)
        } else {
          throw new InvalidPathException(s"No element $subname in Link")
        }
    }
  }

  // Serializes this to protobuf
  def toPb: elem.Link = {
    require(linksLib.isEmpty)
    ???
  }
}


class Design {
  val root: Pathable = ???  // TODO define me

  def resolve(path: DesignPath): Pathable = {
    root.resolve(path.steps)
  }
}
