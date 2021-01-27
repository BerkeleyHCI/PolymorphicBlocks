package edg.compiler

import io.grpc.internal.DnsNameResolverProvider
import io.grpc.netty.NettyChannelBuilder
import edg.compiler.{hdl => edgrpc}
import edg.ref.ref
import edg.schema.schema
import edg.util.timeExec


class PythonInterface {
  // TODO better debug toggle
  protected def debug(msg: => String): Unit = System.err.println(msg)
//  protected def debug(msg: => String): Unit = { }

  val ((channel, blockingStub), initTime) = timeExec {
    val channel = NettyChannelBuilder
        .forAddress("localhost", 50051)
        .nameResolverFactory(new DnsNameResolverProvider())
        .usePlaintext
        .build
    val blockingStub = edgrpc.HdlInterfaceGrpc.blockingStub(channel)
    (channel, blockingStub)
  }
  debug(s"PyIf:init (${initTime} ms)")

  def libraryRequest(modules: Seq[String], element: ref.LibraryPath): schema.Library.NS.Val = {
    val request = edgrpc.LibraryRequest(
      modules=modules,
      element=Some(element)
    )
    val (reply, reqTime) = timeExec {
      blockingStub.getLibraryElement(request)
    }
    debug(s"PyIf:libraryRequest ${element.getTarget.getName} (${reqTime} ms)")
    reply
  }
}
