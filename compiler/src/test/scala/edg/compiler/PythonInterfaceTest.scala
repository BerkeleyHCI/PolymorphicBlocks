package edg.compiler

import edg.compiler.hdl.HdlInterfaceGrpc
import edg.compiler.hdl.HdlInterfaceGrpc.HdlInterface
import org.scalatest._
import org.scalatest.flatspec.AnyFlatSpec
import matchers.should.Matchers._
import edg.compiler.{hdl => edgrpc}
import io.grpc.ManagedChannelBuilder


class PythonInterfaceTest extends AnyFlatSpec {
  behavior of "PythonInterface"

  it should "do something" in {
    val channel = ManagedChannelBuilder.forAddress("localhost", 50051).usePlaintext.build
    val request = edgrpc.ModuleName(name = "World")
    val blockingStub = HdlInterfaceGrpc.blockingStub(channel)
    val reply = blockingStub.libraryElementsInModule(request)

    println(reply)
    println(reply.mkString(", "))
  }

}
