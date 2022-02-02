package edg.util


object IterableUtils {
  implicit class IterableExtensions[T](self: Iterable[T]) {
    // Requires this Iterable is the same as the other, and returns either.
    def listEq(other: Iterable[T]): Iterable[T] = {
      require(self == other, s"lists not equal: $self, $other")
      self
    }
  }
}
