package edg.compiler

import edg.util.Errorable
import edgir.ref.ref.LibraryPath
import org.scalatest.flatspec.AnyFlatSpec
import org.scalatest.matchers.should.Matchers._

import java.io.File


class PythonInterfaceTest extends AnyFlatSpec {
  "Python Interface" should "make basic connections" in {
    val pyIf = new PythonInterface(new File("../HdlInterfaceService.py"))
    pyIf.indexModule("edg_core").getClass should equal(classOf[Errorable.Success[Seq[LibraryPath]]])
    pyIf.shutdown() should equal(0)
  }
}
