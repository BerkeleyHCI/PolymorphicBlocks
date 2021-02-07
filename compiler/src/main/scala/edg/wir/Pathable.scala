package edg.wir

import edg.ref.ref
import edg.common.common


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

  /** Returns whether this object is elaborated, or a library.
    * For containers, returns whether its contained element is elaborarted.
    * Only returns the status of this object, but it may contain unelaborated subtree(s).
    */
  def isElaborated: Boolean

  // Disallow equals since it's probably not useful, and full subtree matches are expensive.
  // But can be allowed in the future, since the current behavior is strict.
  override def equals(that: Any): Boolean = throw new NotImplementedError("Can't do equality comparison on Pathable")
}
