package edg.util

import scala.reflect.ClassTag

sealed trait Errorable[+T] {
  // Returns the contained (if Errorable.Success), or throws an exception with the error message
  // (if Errorable.Error)
  def get: T

  def toOption: Option[T]

  // Default map function on the contained type, that preserves the first error message,
  // and turns null results into an error.
  def map[V](errMsg: => String)(fn: T => V): Errorable[V] = {
    map[V](errMsg, null.asInstanceOf[V])(fn)
  }

  def map[V](errMsg: => String, failureVal: V)(fn: T => V): Errorable[V]

  // This map doesn't check for result failure, but will propagate parent errors
  def map[V](fn: T => V): Errorable[V]

  // Convenience wrapper for options
  def flatMap[V](errMsg: => String)(fn: T => Option[V]): Errorable[V] = {
    map[V](errMsg, null.asInstanceOf[V]) {
      fn(_) match {
        case Some(result) => result
        case None => null.asInstanceOf[V]
      }
    }
  }

  // Convenience wrapper to chain with Errorable functions
  // TODO: can this be implemented through map or Option flatMap?
  def flatMap[V](fn: T => Errorable[V]): Errorable[V]

  // Special case of map with string output, which returns the result of the function, or the propagated error
  def mapToString(fn: T => String): String = mapToStringOrElse(fn, identity)
  def mapToStringOrElse(fn: T => String, errFn: String => String): String

  // Applies a transformation on the error message (if this is an error).
  // Useful for adding context to error messages.
  def mapErr(errFn: String => String): Errorable[T]
}


object Errorable {
  case class Success[T](obj: T) extends Errorable[T] {
    override def get: T = obj

    override def toOption: Option[T] = Some(obj)

    override def map[V](errMsg: => String, failureVal: V)(fn: T => V): Errorable[V] = {
      val result = fn(obj)
      if (result == failureVal) {
        Error(errMsg)
      } else {
        Success(result)
      }
    }
    override def map[V](fn: T => V): Errorable[V] = {
      Success(fn(obj))
    }

    override def flatMap[V](fn: T => Errorable[V]): Errorable[V] = {
      fn(obj)
    }

    override def mapToStringOrElse(fn: T => String, errFn: String => String): String = {
      fn(obj)
    }

    override def mapErr(errFn: String => String): Errorable[T] = {
      this
    }
  }
  case class Error(msg: String) extends Errorable[Nothing] {
    override def get: Nothing = throw new NoSuchElementException(s"Errorable.Error get ($msg)")

    override def toOption: Option[Nothing] = None

    override def map[V](errMsg: => String, failureVal: V)(fn: Nothing => V): Errorable[V] = {
      this
    }
    override def map[V](fn: Nothing => V): Errorable[V] = {
      this
    }

    override def flatMap[V](fn: Nothing => Errorable[V]): Errorable[V] = {
      this
    }

    override def mapToStringOrElse(fn: Nothing => String, errFn: String => String): String = {
      errFn(msg)
    }

    override def mapErr(errFn: String => String): Errorable[Nothing] = {
      Error(errFn(msg))
    }
  }

  def apply[T](obj: Option[T], errMsg: => String): Errorable[T] = {
    require(obj != null)  // as a guard, the user should fix this and make sure Option cannot be null
    obj match {
      case Some(obj) => Success(obj)
      case None => Error(errMsg)
    }
  }

  // Creates Success(value), except for null
  def apply[T](obj: T, errMsg: => String): Errorable[T] = {
    apply[T](obj, errMsg, null.asInstanceOf[T])
  }

  protected def apply[T](obj: T, errMsg: => String, failureVal: T): Errorable[T] = {
    if (obj == failureVal) {
      Error(errMsg)
    } else {
      Success(obj)
    }
  }
}
