package edg.wir

import scala.collection.mutable
import edg.elem.elem
import edg.schema.schema
import edg.ref.ref
import jdk.jshell.spi.ExecutionControl.NotImplementedException


/**
  * Absolute path (from the design root) to some element, including indirect elements like CONNECTED_LINK and link-side
  * ports. Should be a path only, and independent of any particular design (so designs can be transformed while the
  * paths remain valid).
  *
  * Needs a connectivity table to resolve.
  */
sealed trait IndirectStep
object IndirectStep {  // namespace
  case class ConnectedLink() extends IndirectStep  // block-side port -> link
  case class ConnectedPort() extends IndirectStep  // link-side port -> block-side port (authoritative)
  case class Element(name: String) extends IndirectStep
}
case class IndirectDesignPath(steps: Seq[IndirectStep]) {
  def +(suffix: String): IndirectDesignPath = {
    IndirectDesignPath(steps :+ IndirectStep.Element(suffix))
  }

  def ++(suffix: Seq[String]): IndirectDesignPath = {
    IndirectDesignPath(steps ++ suffix.map { IndirectStep.Element(_) })
  }

  def ++(suffix: ref.LocalPath): IndirectDesignPath = {
    IndirectDesignPath(steps ++ suffix.steps.map { step => step.step match {
      case ref.LocalStep.Step.Name(name) => IndirectStep.Element(name)
      case ref.LocalStep.Step.ReservedParam(ref.Reserved.CONNECTED_LINK) => IndirectStep.ConnectedLink()
      case step => throw new NotImplementedError(s"Unknown step $step in appending $suffix from $this")
    } } )
  }
}

object IndirectDesignPath {
  def root: IndirectDesignPath = IndirectDesignPath(Seq())
  def fromDesignPath(designPath: DesignPath): IndirectDesignPath = {
    IndirectDesignPath(designPath.steps.map { IndirectStep.Element(_) })
  }
}


/**
  * Absolute path (from the design root) to some element.
  * TODO: should exclude link ports, since the block side port is treated as authoritative.
  */
case class DesignPath(steps: Seq[String]) {
  def +(elem: String): DesignPath = {
    DesignPath(steps :+ elem)
  }

  def ++(suffix: ref.LocalPath): DesignPath = {
    DesignPath(steps ++ suffix.steps.map { step => step.step match {
      case ref.LocalStep.Step.Name(name) => name
      case step => throw new DesignPath.IndirectPathException(
        s"Found non-direct step $step when appending LocalPath $suffix")
    } } )
  }
}

object DesignPath {
  class IndirectPathException(message: String) extends Exception(message)

  /**
    * Converts an indirect path to a (direct) design path, throwing an exception if there are indirect references
    */
  def fromIndirect(indirect: IndirectDesignPath): DesignPath = {
    DesignPath(indirect.steps.map {
      case IndirectStep.Element(name) => name
      case step => throw new IndirectPathException(s"Found non-direct $step when converting indirect $indirect")
    })
  }

  def root: DesignPath = DesignPath(Seq())
}



class InvalidPathException(message: String) extends Exception(message)


// TODO refactor to its own class file?
/**
  * Base trait for any element that can be resolved from a path, a wrapper around types in elem.proto and parameters.
  * Non-mutable, changes should be copy the object and return a new one.
  */
trait Pathable {
  /**
    * Resolves a LocalPath from here, returning the absolute path and the target element.
    * The target element must exist as an elaborated element (and not lib_elem).
    */
  protected[wir] def resolve(suffix: Seq[String]): Pathable
}

/**
  * "Wrapper" around a HierarchyBlock. Sub-trees of blocks and links are contained as a mutable map in this object
  * (instead of the proto), while everything else is kept in the proto.
  * BlockLike / LinkLike lib_elem are kept in the proto, and when elaborated, should be an empty BlockLike / LinkLike
  * (as a "placeholder") while the actual elaborated sub-tree is in the map.
  * This is to allow efficient transformation at any point in the design tree without re-writing the root.
  */
case class Block(var block: elem.HierarchyBlock) extends Pathable {
  val subblocks = mutable.HashMap[String, Block]()
  val sublinks = mutable.HashMap[String, Link]()

  override protected[wir] def resolve(suffix: Seq[String]): Pathable = {
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
case class Link(var link: elem.Link) extends Pathable {
  val sublinks = mutable.HashMap[String, Link]()

  override protected[wir] def resolve(suffix: Seq[String]): Pathable = {
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
