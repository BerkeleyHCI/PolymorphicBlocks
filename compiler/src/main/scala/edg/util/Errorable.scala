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

  // Checks if some property of the contained value is true, otherwise convert to error with message
  def require(errMsg: => String)(fn: T => Boolean): Errorable[T] = {
    flatMap(errMsg) { contained =>
      if (fn(contained)) {
        Some(contained)
      } else {
        None
      }
    }
  }

  // If the contained object is an instance of V, cast it to V, otherwise convert to error with message
  def mapInstanceOf[V](errMsg: => String)(implicit tag: ClassTag[V]) : Errorable[V] = {
    // Need the implicit tag so this generates a proper runtime check
    flatMap(errMsg) {
      case obj: V => Some(obj)
      case obj => None
    }
  }

  def +[T2](other: Errorable[T2]): Errorable[(T, T2)] = {
    (this, other) match {
      case (Errorable.Success(thisVal), Errorable.Success(otherVal)) =>
        Errorable.Success((thisVal, otherVal))
      case (thisErr @ Errorable.Error(_), _) => thisErr
      case (_, otherErr @ Errorable.Error(_)) => otherErr
    }
  }
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
  }

  def apply[T](obj: Option[T], errMsg: => String): Errorable[T] = {
    if (obj == null) {  // in case a null goes down this path
      Error(errMsg)
    } else {
      obj match {
        case Some(obj) => Success(obj)
        case None => Error(errMsg)
      }
    }
  }

  def apply[T](obj: T, errMsg: => String): Errorable[T] = {
    apply[T](obj, errMsg, null.asInstanceOf[T])
  }

  def apply[T](obj: T, errMsg: => String, failureVal: T): Errorable[T] = {
    if (obj == failureVal) {
      Error(errMsg)
    } else {
      Success(obj)
    }
  }
}
