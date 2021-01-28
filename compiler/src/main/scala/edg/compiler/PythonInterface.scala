package edg.compiler

import collection.mutable
import io.grpc.internal.DnsNameResolverProvider
import io.grpc.netty.NettyChannelBuilder
import edg.compiler.{hdl => edgrpc}
import edg.elem.elem
import edg.ref.ref
import edg.schema.schema
import edg.util.timeExec
import edg.wir.Library
import edg.IrPort


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


class PythonInterfaceLibrary(py: PythonInterface, modules: Seq[String]) extends Library {
  private val elts = mutable.HashMap[ref.LibraryPath, schema.Library.NS.Val.Type]()

  private def fetchEltIfNeeded(path: ref.LibraryPath): Unit = {
    if (!elts.contains(path)) {
      val reply = py.libraryRequest(modules, path)
      if (reply.`type`.isDefined) {
        elts.put(path, reply.`type`)
      }  // otherwise error handling done by caller
    }
  }

  // TODO this should be dedup'd with Library.EdgirLibrary, but there doesn't appear to be an easy
  // common superclass for mutable and immutable maps
  override def getBlock(path: ref.LibraryPath): elem.HierarchyBlock = {
    fetchEltIfNeeded(path)
    elts.get(path) match {
      case Some(schema.Library.NS.Val.Type.HierarchyBlock(member)) => member
      case Some(member) => throw new NoSuchElementException(s"Library element at $path not a block, got ${member.getClass}")
      case None => throw new NoSuchElementException(s"Library does not contain $path")
    }
  }
  override def getLink(path: ref.LibraryPath): elem.Link = {
    fetchEltIfNeeded(path)
    elts.get(path) match {
      case Some(schema.Library.NS.Val.Type.Link(member)) => member
      case Some(member) => throw new NoSuchElementException(s"Library element at $path not a link, got ${member.getClass}")
      case None => throw new NoSuchElementException(s"Library does not contain $path")
    }
  }
  override def getPort(path: ref.LibraryPath): IrPort = {
    fetchEltIfNeeded(path)
    elts.get(path) match {
      case Some(schema.Library.NS.Val.Type.Port(member)) => IrPort.Port(member)
      case Some(schema.Library.NS.Val.Type.Bundle(member)) => IrPort.Bundle(member)
      case Some(member) => throw new NoSuchElementException(s"Library element at $path not a port-like, got ${member.getClass}")
      case None => throw new NoSuchElementException(s"Library does not contain $path")
    }
  }
}
