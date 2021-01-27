package edg.util

object timeExec {
  def apply[T](fn: => T): (T, Long) = {
    val startTime = System.nanoTime()
    val result = fn
    val endTime = System.nanoTime()
    (result, (endTime - startTime)/1000/1000)
  }
}
