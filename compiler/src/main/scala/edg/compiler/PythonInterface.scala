package edg.compiler

import collection.mutable
import edg.compiler.{hdl => edgrpc}
import edg.elem.elem
import edg.ref.ref
import edg.schema.schema
import edg.util.{Errorable, timeExec}
import edg.wir.Library
import edg.IrPort
import java.io.{File, InputStream, OutputStream}


class ProtobufStdioSubprocess
    [RequestType <: scalapb.GeneratedMessage, ResponseType <: scalapb.GeneratedMessage](
    responseType: scalapb.GeneratedMessageCompanion[ResponseType],
    args: Seq[String]) {
  protected val process = new ProcessBuilder(args: _*)
      .redirectError(ProcessBuilder.Redirect.INHERIT)
      .start()

  def write(message: RequestType): Unit = {
    message.writeDelimitedTo(process.getOutputStream)
    process.getOutputStream.flush()
  }

  def read(): ResponseType = {
    responseType.parseDelimitedFrom(process.getInputStream).get
  }
}


class PythonInterface(serverFile: File) {
  // TODO better debug toggle
//  protected def debug(msg: => String): Unit = println(msg)
  protected def debug(msg: => String): Unit = { }

  protected val process = if (serverFile.exists()) {
    Errorable.Success(new ProtobufStdioSubprocess[edgrpc.HdlRequest, edgrpc.HdlResponse](
      edgrpc.HdlResponse,
      Seq("python", serverFile.getAbsolutePath)))
  } else {
    Errorable.Error(s"No HDL Interface Stub at ${serverFile.getAbsolutePath}")
  }


  def reloadModule(module: String): Errorable[Seq[ref.LibraryPath]] = process.map { process =>
    val request = edgrpc.ModuleName(module)
    val (reply, reqTime) = timeExec {
      process.write(edgrpc.HdlRequest(
        request=edgrpc.HdlRequest.Request.ReloadModule(value=request)))
      val reply = process.read()
      reply.getReloadModule.indexed
    }
    debug(s"PyIf:reloadModule $module (${reqTime} ms)")
    reply
  }

  def libraryRequest(element: ref.LibraryPath):
      Errorable[(schema.Library.NS.Val, Option[edgrpc.Refinements])] = process.flatMap { process =>
    val request = edgrpc.LibraryRequest(
      element=Some(element)
    )
    val (reply, reqTime) = timeExec {  // TODO plumb refinements through
      process.write(edgrpc.HdlRequest(
        request=edgrpc.HdlRequest.Request.GetLibraryElement(value=request)))
      val reply = process.read()
      reply.getGetLibraryElement
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
      Errorable[elem.HierarchyBlock] = process.flatMap { process =>
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
      process.write(edgrpc.HdlRequest(
        request=edgrpc.HdlRequest.Request.ElaborateGenerator(value=request)))
      val reply = process.read()
      reply.getElaborateGenerator
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
    eltsRefinements.clear()
    generatorCache.clear()
  }

  /** Discards a type from the cache, returning whether the item existed (and was discarded) */
  def discardCached(discardType: ref.LibraryPath): Boolean = {
    val discarded = if (elts.contains(discardType)) {
      true
    } else {
      false
    }
    elts -= discardType
    eltsRefinements -= discardType
    generatorCache.filterInPlace {
      case (key @ (path, fn, values), data) if path == discardType => false
      case _ => true
    }

    discarded
  }

  def reloadModule(module: String): Errorable[Seq[ref.LibraryPath]] = {
    val pyRefreshedElements = py.reloadModule(module)
    pyRefreshedElements
  }

  def getLibrary(path: ref.LibraryPath): Errorable[schema.Library.NS.Val.Type] = {
    elts.get(path) match {
      case Some(value) => Errorable.Success(value)
      case None => py.libraryRequest(path) match { // not in cache, fetch from Python
        case Errorable.Success((elem, refinementsOpt)) =>
          elts.put(path, elem.`type`)
          refinementsOpt.foreach {
            eltsRefinements.put(path, _)
          }
          Errorable.Success(elem.`type`)
        case err @ Errorable.Error(_) => err
      }
    }
  }

  private def getLibraryPartialMapped[T](path: ref.LibraryPath, expectedType: String)
                                        (mapping: PartialFunction[schema.Library.NS.Val.Type, T]): Errorable[T] = {
    getLibrary(path).flatMap(s"Library element at $path expected type $expectedType") { value =>
      mapping.lift.apply(value)
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

  override def getBlock(path: ref.LibraryPath): Errorable[elem.HierarchyBlock] = {
    getLibraryPartialMapped(path, "block") {
      case schema.Library.NS.Val.Type.HierarchyBlock(member) =>
        require(!eltsRefinements.isDefinedAt(path))  // non-design-top blocks should not have refinements
        member
    }
  }
  override def getLink(path: ref.LibraryPath): Errorable[elem.Link] = {
    getLibraryPartialMapped(path, "link") {
      case schema.Library.NS.Val.Type.Link(member) => member
    }
  }
  override def getPort(path: ref.LibraryPath): Errorable[IrPort] = {
    getLibraryPartialMapped(path, "port") {
      case schema.Library.NS.Val.Type.Port(member) => IrPort.Port(member)
      case schema.Library.NS.Val.Type.Bundle(member) => IrPort.Bundle(member)
    }
  }

  def getDesignTop(path: ref.LibraryPath): Errorable[(elem.HierarchyBlock, edgrpc.Refinements)] = {
    getLibraryPartialMapped(path, "block") {
      case schema.Library.NS.Val.Type.HierarchyBlock(member) =>
        val refinements = eltsRefinements.get(path) match {
          case Some(refinements) => refinements
          case None => edgrpc.Refinements()
        }
        (member, refinements)
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

  def toLibraryPb: schema.Library = {
    schema.Library(root=Some(schema.Library.NS(
      members=elts.toMap.collect { case (path, elt) if !eltsRefinements.contains(path) =>
        // TODO: in future, refinements should be saved; right now the entire element is ignored
        // to prevent the block from loading without the refinements
        path.getTarget.getName -> schema.Library.NS.Val(elt)
      }
    )))
  }

  def loadFromLibraryPb(library: schema.Library): Unit = {
    library.root.getOrElse(schema.Library.NS()).members foreach { case (name, elt) =>
      val path = ref.LibraryPath(target=Some(ref.LocalStep(step=ref.LocalStep.Step.Name(name))))
      require(!elts.isDefinedAt(path), s"overwriting $name in loadFromLibraryPb")
      elts.put(path, elt.`type`)
    }
  }
}
