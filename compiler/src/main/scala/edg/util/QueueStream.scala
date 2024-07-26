package edg.util

import java.io.{InputStream, OutputStream}
import collection.mutable

/** Why the heck are we writing another QueueStream when we have things like Apache QueueInputStream?
  *
  * Well it turns out that they never bothered to implement available(), which is needed for functional compatibility
  * with how subprocess implements their streams. And PipedInputStream doesn't support single-threaded access, it has a
  * limited buffer size and deadlocks.
  *
  * So here, yet another variation of Stream. Yay.
  */
class QueueStream extends OutputStream {
  protected val queue = mutable.Queue[Byte]()

  override def write(data: Int): Unit = queue.enqueue(data.toByte)

  def getReader: Reader = new Reader

  class Reader extends InputStream {
    override def read(): Int = queue.dequeue()
    override def available(): Int = queue.length
  }
}
