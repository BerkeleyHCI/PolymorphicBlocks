package edg.compiler

import edg.util.{Errorable, QueueStream, StreamUtils}
import edgrpc.compiler.{compiler => edgcompiler}
import edgrpc.compiler.compiler.{CompilerRequest, CompilerResult}
import edgrpc.hdl.{hdl => edgrpc}
import edg.wir.{DesignPath, IndirectDesignPath, Refinements}
import edgir.elem.elem
import edgir.ref.ref
import edgir.schema.schema

import java.io.{PrintWriter, StringWriter}

// a PythonInterface that uses the on-event hooks to forward stderr and stdout
// without this, the compiler can freeze on large stdout/stderr data, possibly because of queue sizing
// TODO REMOVE THIS REPLACE WITH HOST STDIO PROCESS INTERFACE
class ForwardingPythonInterface(interpreter: String = "python", pythonPaths: Seq[String] = Seq())
    extends ProtobufStdioSubprocess(interpreter = interpreter, pythonPaths = pythonPaths) {
  def forwardProcessOutput(): Unit = {
    StreamUtils.forAvailable(outputStream) { data =>
      System.out.print(new String(data))
      System.out.flush()
    }
    StreamUtils.forAvailable(errorStream) { data =>
      System.err.print(new String(data))
      System.err.flush()
    }
  }
}

class HostPythonInterface extends ProtobufInterface {
  val responseType = edgrpc.HdlResponse

  protected val stdoutStream = new QueueStream()
  val outputStream = stdoutStream.getReader

  protected val outputDeserializer =
    new ProtobufStreamDeserializer[edgrpc.HdlResponse](System.in, responseType, stdoutStream)
  protected val outputSerializer = new ProtobufStreamSerializer[edgrpc.HdlRequest](System.out)

  override def write(message: edgrpc.HdlRequest): Unit = outputSerializer.write(message)

  override def read(): edgrpc.HdlResponse = {
    outputDeserializer.read()
  }
}

/** A Scala-based EDG compiler interface as a server. Because this uses a persistent HdlInterfaceService, this should
  * not be used where HDL changes are expected during its lifetime. This is suitable for unit tests, but not for
  * long-term user interaction.
  */
object CompilerServerMain {
  final val kHdlVersionMismatchDelayMs = 2000

  private def constPropToSolved(vals: Map[IndirectDesignPath, ExprValue]): Seq[edgcompiler.CompilerResult.Value] = {
    vals.map { case (path, value) =>
      edgcompiler.CompilerResult.Value(
        path = Some(path.toLocalPath),
        value = Some(value.toLit)
      )
    }.toSeq
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
        errors = errors.map(_.toIr),
        solvedValues = constPropToSolved(compiler.getAllSolved)
      )
      result
    } catch {
      case e: Throwable =>
        val sw = new StringWriter()
        e.printStackTrace(new PrintWriter(sw))
        edgcompiler.CompilerResult(errors =
          Seq(edgcompiler.ErrorRecord(
            path = Some(DesignPath().asIndirect.toLocalPath),
            kind = "Internal error",
            name = "",
            details = sw.toString
          ))
        )
    }
  }

  def main(args: Array[String]): Unit = {
    while (true) { // handle multiple requests sequentially in the same process
      val expectedMagicByte = System.in.read()
      if (expectedMagicByte == -1) {
        System.exit(0) // end of stream, shut it down
      }

      require(expectedMagicByte == ProtobufStdioSubprocess.kHeaderMagicByte || expectedMagicByte < 0)
      val request = edgcompiler.CompilerRequest.parseDelimitedFrom(System.in)

      val protoInterface = new HostPythonInterface()
      val compilerInterface = new PythonInterface(protoInterface)
      (compilerInterface.getProtoVersion() match {
        case Errorable.Success(pyVersion) if pyVersion == Compiler.kExpectedProtoVersion => None
        case Errorable.Success(pyMismatchVersion) => Some(pyMismatchVersion.toString)
        case Errorable.Error(errMsg) => Some(s"error $errMsg")
      }).foreach { pyMismatchVersion =>
        System.err.println(f"WARNING: Python / compiler version mismatch, Python reported $pyMismatchVersion, " +
          f"expected ${Compiler.kExpectedProtoVersion}.")
        System.err.println(
          f"If you get unexpected errors or results, consider updating the Python library or compiler."
        )
        Thread.sleep(kHdlVersionMismatchDelayMs)
      }

      val pyLib = new PythonInterfaceLibrary()
      pyLib.withPythonInterface(compilerInterface) {
        val result = compile(request.get, pyLib)

        assert(protoInterface.outputStream.available() == 0, "unhandled in-band data from HDL compiler")

        // this acts as a message indicating end of compilation
        protoInterface.write(edgrpc.HdlRequest())

        System.out.write(ProtobufStdioSubprocess.kHeaderMagicByte)
        result.writeDelimitedTo(System.out)
        System.out.flush()
      }
    }
  }
}
