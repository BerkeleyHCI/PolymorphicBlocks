package edg.compiler

import io.grpc.internal.DnsNameResolverProvider
import io.grpc.netty.NettyChannelBuilder
import edg.compiler.{hdl => edgrpc}
import edg.ref.ref
import edg.schema.schema


class PythonInterface {
  val channel = NettyChannelBuilder
      .forAddress("localhost", 50051)
      .nameResolverFactory(new DnsNameResolverProvider())
      .usePlaintext
      .build
  val blockingStub = edgrpc.HdlInterfaceGrpc.blockingStub(channel)

  def libraryRequest(modules: Seq[String], element: ref.LibraryPath): schema.Library.NS.Val = {
    val request = edgrpc.LibraryRequest(
      modules=modules,
      element=Some(element)
    )
    blockingStub.getLibraryElement(request)
  }
}
