package edg.compiler

import edg.util.StreamUtils
import edgrpc.compiler.{compiler => edgcompiler}
import edgrpc.compiler.compiler.{CompilerRequest, CompilerResult}
import edg.wir.{IndirectDesignPath, Refinements}

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
    try {
      val refinements = Refinements(request.getRefinements)
      val compiler = new Compiler(request.getDesign, library, refinements)
      val compiled = compiler.compile()
      val errors = compiler.getErrors() ++ new DesignAssertionCheck(compiler).map(compiled) ++
        new DesignStructuralValidate().map(compiled) ++ new DesignRefsValidate().validate(compiled)
      val result = edgcompiler.CompilerResult(
        design = Some(compiled),
        error = errors.mkString("\n"),
        solvedValues = constPropToSolved(compiler.getAllSolved)
      )
      result
    } catch {
      case e: Throwable =>
        val sw = new StringWriter()
        e.printStackTrace(new PrintWriter(sw))
        edgcompiler.CompilerResult(error = sw.toString)
    }
  }

  def main(args: Array[String]): Unit = {
    val pyIf = new PythonInterface(new File("HdlInterfaceService.py"))  // use relative path
    val pyLib = new PythonInterfaceLibrary()
    pyLib.withPythonInterface(pyIf) {
      while (true) {
        val expectedMagicByte = System.in.read()
        require(expectedMagicByte == ProtobufStdioSubprocess.kHeaderMagicByte || expectedMagicByte < 0)

        val request = edgcompiler.CompilerRequest.parseDelimitedFrom(System.in)
        val result = request match {
          case Some(request) =>
            compile(request, pyLib)
          case None => // end of stream
            System.exit(0)
            throw new NotImplementedError()  // provides a return type, shouldn't ever happen
        }

        // forward stdout and stderr output
        StreamUtils.forAvailable(pyIf.processOutputStream) { data =>
          System.out.print(new String(data))
          System.out.flush()
        }
        StreamUtils.forAvailable(pyIf.processErrorStream) { data =>
          System.err.print(new String(data))
          System.err.flush()
        }

        System.out.write(ProtobufStdioSubprocess.kHeaderMagicByte)
        result.writeDelimitedTo(System.out)
        System.out.flush()
      }
    }
  }
}
