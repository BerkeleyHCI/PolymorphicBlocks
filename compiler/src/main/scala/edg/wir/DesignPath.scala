package edg.wir

import edg.elem.elem
import edg.schema.schema
import edg.ref.ref


/**
  * Absolute path (from the design root) to some element
  */
trait DesignPath {

}



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
