package edg.compiler

import java.net.{Inet4Address, InetAddress, InetSocketAddress}
import io.grpc.{ManagedChannel, ManagedChannelBuilder}
import io.grpc.netty.NettyChannelBuilder
import io.grpc.internal.DnsNameResolverProvider
import edg.compiler.{hdl => edgrpc}
import edg.ref.ref

import java.net.InetSocketAddress

object CliMain {
  def main(args: Array[String]): Unit = {
    val moduleName = args(0)
    val blockName = args(1)
    println(s"Compile with modules $moduleName, block $blockName")

//    val channel = ManagedChannelBuilder.forAddress("localhost", 50051).usePlaintext.build
    val channel = NettyChannelBuilder
        .forAddress("localhost", 50051)
        .nameResolverFactory(new DnsNameResolverProvider())
        .usePlaintext
        .build
//    val address = new InetSocketAddress(InetAddress.getByAddress(Array(127, 0, 0, 1)), 50051)
//    val channel = NettyChannelBuilder.forAddress(address).usePlaintext.build
    val blockingStub = edgrpc.HdlInterfaceGrpc.blockingStub(channel)

    val request = edgrpc.LibraryRequest(
      modules=Seq(moduleName),
      element=Some(ref.LibraryPath(target=Some(ref.LocalStep(ref.LocalStep.Step.Name(blockName)))))
    )
    val reply = blockingStub.getLibraryElement(request)
    println(reply)
  }
}
