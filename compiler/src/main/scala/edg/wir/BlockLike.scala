package edg.wir

import edg.elem.elem
import scala.collection.mutable


sealed trait IrPorts  // to box Port-like types because of lack of union types in SScala
object IrPorts {
  case class Port(pb: elem.Port) extends IrPorts
  case class Bundle(pb: elem.Bundle) extends IrPorts
}


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
}

/**
  * "Wrapper" around a HierarchyBlock. Sub-trees of blocks and links are contained as a mutable map in this object
  * (instead of the proto), while everything else is kept in the proto.
  * BlockLike / LinkLike lib_elem are kept in the proto, and when elaborated, should be an empty BlockLike / LinkLike
  * (as a "placeholder") while the actual elaborated sub-tree is in the map.
  * This is to allow efficient transformation at any point in the design tree without re-writing the root.
  */
case class Block(var pb: elem.HierarchyBlock) extends Pathable {
  require(pb.blocks.values.map(_.`type`).collect {
    case elem.BlockLike.Type.Hierarchy(_) => true
  }.isEmpty, "Block declared with subtree with blocks")
  require(pb.links.values.map(_.`type`).collect {
    case elem.LinkLike.Type.Link(_) => true
  }.isEmpty, "Block declared with subtree with links")

  val subblocks = mutable.HashMap[String, Block]()
  val sublinks = mutable.HashMap[String, Link]()

  override def resolve(suffix: Seq[String]): Pathable = {
    suffix match {
      case Seq() => this
      case Seq(subname, tail@_*) =>
        if (subblocks.contains(subname)) {
          subblocks(subname).resolve(tail)
        } else if (sublinks.contains(subname)) {
          sublinks(subname).resolve(tail)
        } else {
          throw new InvalidPathException(s"No element $subname in Block")
        }
    }
  }
}

/**
  * Similar to Block, see documentation there.
  */
case class Link(var pb: elem.Link) extends Pathable {
  require(pb.links.values.map(_.`type`).collect {
    case elem.LinkLike.Type.Link(_) => true
  }.isEmpty, "Block declared with subtree with links")

  val sublinks = mutable.HashMap[String, Link]()

  override def resolve(suffix: Seq[String]): Pathable = {
    suffix match {
      case Seq() => this
      case Seq(subname, tail@_*) =>
        if (sublinks.contains(subname)) {
          sublinks(subname).resolve(tail)
        } else {
          throw new InvalidPathException(s"No element $subname in Link")
        }
    }
  }
}


class Design {
  val root: Pathable = ???  // TODO define me

  def resolve(path: DesignPath): Pathable = {
    root.resolve(path.steps)
  }
}
