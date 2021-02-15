package edg.compiler

import collection.mutable
import io.grpc.internal.DnsNameResolverProvider
import io.grpc.netty.NettyChannelBuilder
import edg.compiler.{hdl => edgrpc}
import edg.elem.elem
import edg.ref.ref
import edg.schema.schema
import edg.util.{Errorable, timeExec}
import edg.wir.{Library}
import edg.IrPort


class PythonInterface {
  // TODO better debug toggle
//  protected def debug(msg: => String): Unit = println(msg)
  protected def debug(msg: => String): Unit = { }

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

  def reloadModule(module: String): Seq[ref.LibraryPath] = {
    val request = edgrpc.ModuleName(module)
    val (reply, reqTime) = timeExec {
      blockingStub.reloadModule(request)
    }
    debug(s"PyIf:reloadModule $module (${reqTime} ms)")
    reply.toSeq
  }

  def libraryRequest(element: ref.LibraryPath):
      Errorable[(schema.Library.NS.Val, Option[edgrpc.Refinements])] = {
    val request = edgrpc.LibraryRequest(
      element=Some(element)
    )
    val (reply, reqTime) = timeExec {  // TODO plumb refinements through
      blockingStub.getLibraryElement(request)
    }

    reply.result match {
      case edgrpc.LibraryResponse.Result.Element(elem) =>
        debug(s"PyIf:libraryRequest ${element.getTarget.getName} <= ... (${reqTime} ms)")
        Errorable.Success((elem, reply.refinements))
      case edgrpc.LibraryResponse.Result.Error(err) =>
        debug(s"PyIf:libraryRequest ${element.getTarget.getName} <= err $err (${reqTime} ms)")
        Errorable.Error(err)
      case edgrpc.LibraryResponse.Result.Empty =>
        debug(s"PyIf:libraryRequest ${element.getTarget.getName} <= empty (${reqTime} ms)")
        Errorable.Error("empty response")
    }
  }

  def elaborateGeneratorRequest(element: ref.LibraryPath,
                                fnName: String, values: Map[ref.LocalPath, ExprValue]):
      Errorable[elem.HierarchyBlock] = {
    val request = edgrpc.GeneratorRequest(
      element=Some(element), fn=fnName,
      values=values.map { case (valuePath, valueValue) =>
        edgrpc.GeneratorRequest.Value(
          path=Some(valuePath),
          value=Some(valueValue.toLit)
        )
      }.toSeq
    )
    val (reply, reqTime) = timeExec {
      blockingStub.elaborateGenerator(request)
    }
    debug(s"PyIf:generatorRequest ${element.getTarget.getName} $fnName (${reqTime} ms)")
    reply.result match {
      case edgrpc.GeneratorResponse.Result.Generated(elem) => Errorable.Success(elem)
      case edgrpc.GeneratorResponse.Result.Error(err) => Errorable.Error(err)
      case edgrpc.GeneratorResponse.Result.Empty => Errorable.Error("empty response")
    }
  }
}


class PythonInterfaceLibrary(py: PythonInterface) extends Library {
  private val elts = mutable.HashMap[ref.LibraryPath, schema.Library.NS.Val.Type]()
  private val eltsRefinements = mutable.HashMap[ref.LibraryPath, edgrpc.Refinements]()
  private val generatorCache = mutable.HashMap[(ref.LibraryPath, String, Map[ref.LocalPath, ExprValue]),
      elem.HierarchyBlock]()

  def clearThisCache(): Unit = {
    elts.clear()
    generatorCache.clear()
  }

  def discardCached(module: String): Seq[ref.LibraryPath] = {
    val discardKeys = elts.collect {  // TODO this assumes following the naming convention
      case (path, data) if path.getTarget.getName.startsWith(module) => path
    }
    elts --= discardKeys
    eltsRefinements --= discardKeys

    val discardGenerator = generatorCache.collect {  // TODO this assumes following the naming convention
      case (key @ (path, fn, values), data) if path.getTarget.getName.startsWith(module) => key
    }
    generatorCache --= discardGenerator

    discardKeys.toSeq
  }

  def reloadModule(module: String): Seq[ref.LibraryPath] = {
    val pyRefreshedElements = py.reloadModule(module)
    pyRefreshedElements
  }

  private def fetchEltIfNeeded(path: ref.LibraryPath): Unit = {
    if (!elts.contains(path)) {
      py.libraryRequest(path) match {
        case Errorable.Success((elem, None)) =>
          elts.put(path, elem.`type`)
        case Errorable.Success((elem, Some(refinements))) =>
          elts.put(path, elem.`type`)
          eltsRefinements.put(path, refinements)
        case Errorable.Error(err) =>
          // TODO better error handling and passing
      }
    }
  }

  // TODO this should be dedup'd with Library.EdgirLibrary, but there doesn't appear to be an easy
  // common superclass for mutable and immutable maps
  override def allBlocks: Map[ref.LibraryPath, elem.HierarchyBlock] = elts.collect {
    case (path, schema.Library.NS.Val.Type.HierarchyBlock(block)) => (path, block)
  }.toMap

  override def allPorts: Map[ref.LibraryPath, IrPort] = elts.collect {
    case (path, schema.Library.NS.Val.Type.Port(port)) => (path, IrPort.Port(port))
    case (path, schema.Library.NS.Val.Type.Bundle(port)) => (path, IrPort.Bundle(port))
  }.toMap

  override def allLinks: Map[ref.LibraryPath, elem.Link] = elts.collect {
    case (path, schema.Library.NS.Val.Type.Link(link)) => (path, link)
  }.toMap

  override def getBlock(path: ref.LibraryPath): elem.HierarchyBlock = {
    fetchEltIfNeeded(path)
    elts.get(path) match {
      case Some(schema.Library.NS.Val.Type.HierarchyBlock(member)) =>
        require(!eltsRefinements.isDefinedAt(path))
        member
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

  def getDesignTop(path: ref.LibraryPath): (elem.HierarchyBlock, edgrpc.Refinements) = {
    fetchEltIfNeeded(path)
    val refinements = eltsRefinements.get(path) match {
      case Some(refinements) => refinements
      case None => edgrpc.Refinements()
    }
    elts.get(path) match {
      case Some(schema.Library.NS.Val.Type.HierarchyBlock(member)) =>
        (member, refinements)
      case Some(member) => throw new NoSuchElementException(s"Library element at $path not a block, got ${member.getClass}")
      case None => throw new NoSuchElementException(s"Library does not contain $path")
    }
  }

  override def runGenerator(path: ref.LibraryPath, fnName: String,
                            values: Map[ref.LocalPath, ExprValue]): Errorable[elem.HierarchyBlock] = {
    generatorCache.get((path, fnName, values)) match {
      case Some(generated) => Errorable.Success(generated)
      case None =>
        val result = py.elaborateGeneratorRequest(path, fnName, values)
        result.map { generatorCache.put((path, fnName, values), _) }
        result
    }
  }
}
