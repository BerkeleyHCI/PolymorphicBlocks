package edg.util

import java.io.InputStream

object StreamUtils {
  def forAvailable(stream: InputStream)(fn: Array[Byte] => Unit): Unit = {
    var available = stream.available()
    while (available > 0) {
      val array = new Array[Byte](available)
      stream.read(array)
      fn(array)
      available = stream.available()
    }
  }
}
