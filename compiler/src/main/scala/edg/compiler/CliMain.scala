package edg.compiler

import edg.common.common
import edg.ref.ref
import edg.schema.schema
import edg.wir.IndirectDesignPath
import edg.compiler.{hdl => edgrpc}
import edg.ElemBuilder.Metadata


object CliMain {
  def constPropToSolved(vals: Map[IndirectDesignPath, ExprValue]): edgrpc.SolvedConstraints = {
    edgrpc.SolvedConstraints(
      values=vals.map { case (path, value) => edgrpc.SolvedConstraints.Value(
        path=Some(path.toLocalPath),
        value=Some(value.toLit)
      )}.toSeq)
  }

  def main(args: Array[String]): Unit = {
    val moduleName = args(0)
    val blockName = args(1)

    val pyIf = new PythonInterface()

    val blockLib = ref.LibraryPath(target=Some(ref.LocalStep(ref.LocalStep.Step.Name(blockName))))
    val topBlock = pyIf.libraryRequest(Seq(moduleName), blockLib).getHierarchyBlock

    val topDesign = schema.Design(contents=Some(topBlock))
    val compiler = new Compiler(topDesign, new PythonInterfaceLibrary(pyIf, Seq(moduleName)))
    val compiled = compiler.compile()

    val constPropMeta = constPropToSolved(compiler.getAllSolved).toByteString
    val compiledWithVals = compiled.update(
      _.contents.meta.members.node.:+=("solved" -> Metadata.Bytes(constPropMeta))
    )

    compiledWithVals.writeTo(System.out)
  }
}
