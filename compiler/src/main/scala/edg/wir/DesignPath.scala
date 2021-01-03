package edg.wir

import edg.elem.elem
import edg.schema.schema
import edg.ref.ref

/**
  * Absolute path (from the design root) to some element, including indirect elements like CONNECTED_LINK and link-side
  * ports.
  *
  * Case classes will automatically generate an equality method that does the right thing,
  * including field and type checks.
  *
  * TODO: would be much improved with union types... which are not supported in Scala =(
  */
trait IndirectDesignPath

trait IndirectLinkParentable extends IndirectDesignPath
trait IndirectLinkPortParentable extends IndirectDesignPath
trait IndirectLinkParamParentable extends IndirectDesignPath

case class ConnectedLink(parent: PortPath) extends IndirectDesignPath
  with IndirectLinkPortParentable with IndirectLinkParamParentable
case class LinkPort(eltName: String, parent: LinkPath) extends IndirectDesignPath
  with IndirectLinkPortParentable with IndirectLinkParamParentable
case class LinkPortParam(eltName: String, parent: IndirectLinkParamParentable) extends IndirectDesignPath

/**
  * Absolute path (from the design root) to some element.
  * Excludes link ports, since the block side port is treated as authoritative.
  */
trait DesignPath extends IndirectDesignPath

trait LinkParentable extends DesignPath with IndirectLinkParentable
trait PortParentable extends DesignPath
trait ParamParentable extends DesignPath

case class BlockPath(eltName: String, parent: Option[BlockPath]) extends DesignPath
  with LinkParentable with PortParentable with ParamParentable

case class LinkPath(eltName: String, parent: LinkParentable) extends LinkParentable with ParamParentable

case class PortPath(eltName: String, parent: PortParentable) extends PortParentable with ParamParentable

case class ParamPath(eltName: String, parent: ParamParentable) extends DesignPath


// TODO refactor to its own class file?
/**
  * Base trait for any element that can be resolved from a path, a wrapper around types in elem.proto and parameters.
  * Non-mutable, changes should be copy the object and return a new one.
  */
trait Pathable {
  /**
    * Resolves a LocalPath from here, returning the absolute path and the target element
    */
  def resolve(path: ref.LocalPath): (DesignPath, Pathable)
}


class Design extends Pathable {
  def resolve(path: DesignPath): Pathable = {

  }
}
