package edg.compiler

import edg.wir.{IndirectDesignPath, Refinements}
import edg.compiler.{compiler => edgcompiler}
import edg.compiler.compiler.{CompilerRequest, CompilerResult}
import io.grpc.netty.NettyServerBuilder

import java.io.{File, PrintWriter, StringWriter}
import scala.concurrent.{ExecutionContext, Future}


private class CompilerImpl(library: PythonInterfaceLibrary) extends edgcompiler.CompilerGrpc.Compiler {
  private def constPropToSolved(vals: Map[IndirectDesignPath, ExprValue]): Seq[edgcompiler.CompilerResult.Value] = {
    vals.map { case (path, value) => edgcompiler.CompilerResult.Value(
      path=Some(path.toLocalPath),
      value=Some(value.toLit)
    )}.toSeq
  }

  override def compile(request: CompilerRequest): Future[CompilerResult] = {
    request.modules.foreach { module =>
      library.reloadModule(module)
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
      Future.successful(result)
    } catch {
      case e: Throwable =>
        val sw = new StringWriter()
        val pw = new PrintWriter(sw)
        e.printStackTrace(pw)
        Future.successful(edgcompiler.CompilerResult(
          error = sw.toString
        ))
    }
  }
}


object CompilerGrpcMain {
  def main(args: Array[String]): Unit = {
    val port = 50052

    val pyIf = new PythonInterface(new File("HdlInterfaceServer.py"))  // use relative path
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
