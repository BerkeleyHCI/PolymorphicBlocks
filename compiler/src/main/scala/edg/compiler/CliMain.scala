package edg.compiler

import edg.ref.ref
import edg.schema.schema


object CliMain {
  def main(args: Array[String]): Unit = {
    System.err.println("JAR started")

    val moduleName = args(0)
    val blockName = args(1)

    val pyIf = new PythonInterface()
    System.err.println("Channel created")

    val blockLib = ref.LibraryPath(target=Some(ref.LocalStep(ref.LocalStep.Step.Name(blockName))))
    val topBlock = pyIf.libraryRequest(Seq(moduleName), blockLib).getHierarchyBlock
    System.err.println("Compilation done")

    schema.Design(contents=Some(topBlock)).writeTo(System.out)
  }
}
