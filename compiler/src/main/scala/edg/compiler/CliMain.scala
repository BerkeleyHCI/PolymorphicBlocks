package edg.compiler

import edg.ref.ref
import edg.schema.schema


object CliMain {
  def main(args: Array[String]): Unit = {
    val moduleName = args(0)
    val blockName = args(1)

    val pyIf = new PythonInterface()

    val blockLib = ref.LibraryPath(target=Some(ref.LocalStep(ref.LocalStep.Step.Name(blockName))))
    val topBlock = pyIf.libraryRequest(Seq(moduleName), blockLib).getHierarchyBlock

    schema.Design(contents=Some(topBlock)).writeTo(System.out)
  }
}
