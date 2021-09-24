package edg.compiler

import edg.wir.{IndirectDesignPath, Refinements}
import edg.compiler.{compiler => edgcompiler}
import edg.compiler.compiler.{CompilerRequest, CompilerResult}

import java.io.{File, PrintWriter, StringWriter}


/** A Scala-based EDG compiler interface as a server.
  * Because this uses a persistent HdlInterfaceService, this should not be used where HDL changes are expected
  * during its lifetime. This is suitable for unit tests, but not for long-term user interaction.
  */
object CompilerServerMain {
  private def constPropToSolved(vals: Map[IndirectDesignPath, ExprValue]): Seq[edgcompiler.CompilerResult.Value] = {
    vals.map { case (path, value) => edgcompiler.CompilerResult.Value(
      path=Some(path.toLocalPath),
      value=Some(value.toLit)
    )}.toSeq
  }

  def compile(request: CompilerRequest, library: PythonInterfaceLibrary): CompilerResult = {
    request.modules.foreach { module =>
      library.indexModule(module)
    }

    try {
      val refinements = Refinements(request.getRefinements)
      val compiler = new Compiler(request.getDesign, library, refinements)
      val compiled = compiler.compile()
      val checker = new DesignStructuralValidate()
      val errors = compiler.getErrors() ++ checker.map(compiled)
      val result = edgcompiler.CompilerResult(
        design = Some(compiled),
        error = errors.mkString(", "),
        solvedValues = constPropToSolved(compiler.getAllSolved)
      )
      result
    } catch {
      case e: Throwable =>
        val sw = new StringWriter()
        val pw = new PrintWriter(sw)
        e.printStackTrace(pw)
        edgcompiler.CompilerResult(error = sw.toString)
    }
  }

  def main(args: Array[String]): Unit = {
    val pyIf = new PythonInterface(new File("HdlInterfaceService.py"))  // use relative path
    val pyLib = new PythonInterfaceLibrary()
    pyLib.withPythonInterface(pyIf) {
      while (true) {
        val request = compiler.CompilerRequest.parseDelimitedFrom(System.in)
        request match {
          case Some(request) =>
            val result = compile(request, pyLib)
            result.writeDelimitedTo(System.out)
            System.out.flush()
          case None => // end of stream
            System.exit(0)
        }
      }
    }
  }
}
