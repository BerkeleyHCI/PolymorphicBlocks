package edg.compiler

import edg.util.Errorable
import edgir.ref.ref.LibraryPath
import org.scalatest.flatspec.AnyFlatSpec
import org.scalatest.matchers.should.Matchers._

import java.io.File


class PythonInterfaceTest extends AnyFlatSpec {
  "Python Interface" should "make basic connections" in {
    val compiledDir = new File(getClass.getResource("").getPath)
    // above returns compiler/target/scala-2.xx/test-classes/edg/compiler, get the root repo dir
    val repoDir = compiledDir.getParentFile.getParentFile.getParentFile.getParentFile.getParentFile.getParentFile
    val pyIf = new PythonInterface(new File(repoDir, "HdlInterfaceService.py"))
    pyIf.indexModule("edg_core").getClass should equal(classOf[Errorable.Success[Seq[LibraryPath]]])
    pyIf.shutdown() should equal(0)
  }
}
