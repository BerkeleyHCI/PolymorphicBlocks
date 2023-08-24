package edg.util

object IterableUtils {
  // if all elements defined, returns the seq of elements, else None
  def getAllDefined[T](seq: Iterable[Option[T]]): Option[Iterable[T]] = {
    val (some, none) = seq.partitionMap {
      case Some(value) => Left(value)
      case None => Right(None)
    }
    if (none.nonEmpty) {
      None
    } else {
      Some(some)
    }
  }
}
