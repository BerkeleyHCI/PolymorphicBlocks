package edg.compiler

import edg.wir.{IndirectDesignPath, Refinements}
import edg.compiler.{compiler => edgcompiler}
import edg.compiler.compiler.{CompilerRequest, CompilerResult}
import io.grpc.netty.NettyServerBuilder

import java.io.{PrintWriter, StringWriter}
import scala.concurrent.{ExecutionContext, Future}


private class CompilerImpl(library: PythonInterfaceLibrary) extends edgcompiler.CompilerGrpc.Compiler {
  private def constPropToSolved(vals: Map[IndirectDesignPath, ExprValue]): Seq[edgcompiler.CompilerResult.Value] = {
    vals.map { case (path, value) => edgcompiler.CompilerResult.Value(
      path=Some(path.toLocalPath),
      value=Some(value.toLit)
    )}.toSeq
  }

  override def compile(request: CompilerRequest): Future[CompilerResult] = {
    library.setModules(request.modules)

    try {
      val refinements = Refinements.fromCompilerRequest(request)
      val compiler = new Compiler(request.getDesign, library, refinements)
      val compiled = compiler.compile()
      val result = edgcompiler.CompilerResult(
        result = edgcompiler.CompilerResult.Result.Design(compiled),
        solvedValues = constPropToSolved(compiler.getAllSolved)
      )
      Future.successful(result)
    } catch {
      case e: Throwable =>
        val sw = new StringWriter()
        val pw = new PrintWriter(sw)
        e.printStackTrace(pw)
        Future.successful(edgcompiler.CompilerResult(
          result = edgcompiler.CompilerResult.Result.Error(sw.toString)
        ))
    }
  }
}


object CompilerGrpcMain {
  def main(args: Array[String]): Unit = {
    val port = 50052

    val pyIf = new PythonInterface()
    val compilerService = new CompilerImpl(new PythonInterfaceLibrary(pyIf))

    val server = NettyServerBuilder
        .forPort(port)
        .addService(edgcompiler.CompilerGrpc.bindService(compilerService, ExecutionContext.global))
        .build
        .start

    sys.addShutdownHook {
      server.shutdown()
    }

    scala.io.StdIn.readLine
  }
}
