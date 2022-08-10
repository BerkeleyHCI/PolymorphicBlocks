package edg.compiler

import edg.EdgirUtils.SimpleLibraryPath
import edg.IrPort
import edg.util.{Errorable, QueueStream, timeExec}
import edg.wir.Library
import edgir.elem.elem
import edgir.ref.ref
import edgir.schema.schema
import edgrpc.hdl.{hdl => edgrpc}

import java.io.{File, InputStream}
import scala.collection.mutable


class ProtobufSubprocessException() extends Exception()


object ProtobufStdioSubprocess {
  val kHeaderMagicByte = 0xfe  // currently only for Python -> Scala
}


class ProtobufStdioSubprocess
    [RequestType <: scalapb.GeneratedMessage, ResponseType <: scalapb.GeneratedMessage](
    responseType: scalapb.GeneratedMessageCompanion[ResponseType],
    args: Seq[String]) {
  protected val process = new ProcessBuilder(args: _*).start()

  // this provides a consistent Stream interface for both stdout and stderr
  // don't use PipedInputStream since it has a non-expanding buffer and is not single-thread safe
  val outputStream = new QueueStream()
  val errorStream = process.getErrorStream  // the raw error stream from the process

  def write(message: RequestType): Unit = {
    if (!process.isAlive) {  // quick check before we try to write to a dead process
      throw new ProtobufSubprocessException()
    }

    process.getOutputStream.write(ProtobufStdioSubprocess.kHeaderMagicByte)
    message.writeDelimitedTo(process.getOutputStream)
    process.getOutputStream.flush()
  }

  def read(): ResponseType = {
    var doneReadingStdout: Boolean = false
    while (!doneReadingStdout) {
      val nextByte = process.getInputStream.read()
     if (nextByte == ProtobufStdioSubprocess.kHeaderMagicByte) {
        doneReadingStdout = true
      } else if (nextByte < 0) {
        throw new ProtobufSubprocessException()
      } else {
       outputStream.write(nextByte)
      }
    }

    val responseOpt = responseType.parseDelimitedFrom(process.getInputStream)

    if (!process.isAlive) {
      throw new ProtobufSubprocessException()
    }
    responseOpt.get
  }

  // Shuts down the stream and returns the exit value
  def shutdown(): Int = {
    process.getOutputStream.close()
    var doneReadingStdout: Boolean = false
    while (!doneReadingStdout) {
      val nextByte = process.getInputStream.read()
      require(nextByte != ProtobufStdioSubprocess.kHeaderMagicByte)
      if (nextByte < 0) {
        doneReadingStdout = true
      } else {
        outputStream.write(nextByte)
      }
    }

    process.waitFor()
    process.exitValue()
  }
}


/** An interface to the Python HDL elaborator, which reads in Python HDL code and (partially) compiles
  * them down to IR.
  * The underlying Python HDL should not change while this is open. This will not reload updated Python HDL files.
  */
class PythonInterface(serverFile: File) {
  protected val process = new ProtobufStdioSubprocess[edgrpc.HdlRequest, edgrpc.HdlResponse](
    edgrpc.HdlResponse,
    Seq("python", "-u", serverFile.getAbsolutePath))  // in unbuffered mode
  val processOutputStream: InputStream = process.outputStream
  val processErrorStream: InputStream = process.errorStream


  // Hooks to implement when certain actions happen
  def onLibraryRequest(element: ref.LibraryPath): Unit = {}
  def onLibraryRequestComplete(element: ref.LibraryPath,
                               result: Errorable[(schema.Library.NS.Val, Option[edgrpc.Refinements])]): Unit = {}
  def onElaborateGeneratorRequest(element: ref.LibraryPath, values: Map[ref.LocalPath, ExprValue]): Unit = {}
  def onElaborateGeneratorRequestComplete(element: ref.LibraryPath, values: Map[ref.LocalPath, ExprValue],
                                          result: Errorable[elem.HierarchyBlock]): Unit = {}


  def indexModule(module: String): Errorable[Seq[ref.LibraryPath]] = {
    val request = edgrpc.ModuleName(module)
    val (reply, reqTime) = timeExec {
      process.write(edgrpc.HdlRequest(
        request=edgrpc.HdlRequest.Request.IndexModule(value=request)))
      process.read()
    }
    reply.response match {
      case edgrpc.HdlResponse.Response.IndexModule(result) =>
        Errorable.Success(result.indexed)
      case edgrpc.HdlResponse.Response.Error(err) =>
        Errorable.Error(s"while indexing $module: ${err.error}")
      case _ =>
        Errorable.Error(s"while indexing $module: invalid response")
    }
  }

  def libraryRequest(element: ref.LibraryPath):
      Errorable[(schema.Library.NS.Val, Option[edgrpc.Refinements])] = {
    onLibraryRequest(element)

    val request = edgrpc.LibraryRequest(
      element=Some(element)
    )
    val (reply, reqTime) = timeExec {  // TODO plumb refinements through
      process.write(edgrpc.HdlRequest(
        request=edgrpc.HdlRequest.Request.GetLibraryElement(value=request)))
      process.read()
    }
    val result = reply.response match {
      case edgrpc.HdlResponse.Response.GetLibraryElement(result) =>
        Errorable.Success((result.getElement, result.refinements))
      case edgrpc.HdlResponse.Response.Error(err) =>
        Errorable.Error(s"while elaborating ${element.toSimpleString}: ${err.error}")
      case _ =>
        Errorable.Error(s"while elaborating ${element.toSimpleString}: invalid response")
    }
    onLibraryRequestComplete(element, result)
    result
  }

  def elaborateGeneratorRequest(element: ref.LibraryPath, values: Map[ref.LocalPath, ExprValue]):
      Errorable[elem.HierarchyBlock] = {
    onElaborateGeneratorRequest(element, values)

    val request = edgrpc.GeneratorRequest(
      element=Some(element),
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
      process.read()
    }
    val result = reply.response match {
      case edgrpc.HdlResponse.Response.ElaborateGenerator(result) =>
        Errorable.Success(result.getGenerated)
      case edgrpc.HdlResponse.Response.Error(err) =>
        Errorable.Error(s"while generating ${element.toSimpleString}: ${err.error}")
      case _ =>
        Errorable.Error(s"while generating ${element.toSimpleString}: invalid response")
    }
    onElaborateGeneratorRequestComplete(element, values, result)
    result
  }

  def shutdown(): Int = {
    process.shutdown()
  }
}


class PythonInterfaceLibrary() extends Library {
  private val elts = mutable.HashMap[ref.LibraryPath, schema.Library.NS.Val.Type]()
  private val eltsRefinements = mutable.HashMap[ref.LibraryPath, edgrpc.Refinements]()
  private val generatorCache = mutable.HashMap[(ref.LibraryPath, Map[ref.LocalPath, ExprValue]),
      elem.HierarchyBlock]()

  protected var py: Option[PythonInterface] = None

  // Runs some block of code with the specified Python interface.
  def withPythonInterface[T](withInterface: PythonInterface)(fn: => T): T = {
    require(py.isEmpty)
    py = Some(withInterface)
    try {
      val result = fn
      result
    } finally {
      require(py.contains(withInterface))
      py = None
    }
  }

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
      case (key @ (path, values), data) if path == discardType => false
      case _ => true
    }

    discarded
  }

  def indexModule(module: String): Errorable[Seq[ref.LibraryPath]] = {
    py.get.indexModule(module)
  }

  def getLibrary(path: ref.LibraryPath): Errorable[schema.Library.NS.Val.Type] = {
    elts.get(path) match {
      case Some(value) => Errorable.Success(value)
      case None => py.get.libraryRequest(path) match { // not in cache, fetch from Python
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

  override def runGenerator(path: ref.LibraryPath,
                            values: Map[ref.LocalPath, ExprValue]): Errorable[elem.HierarchyBlock] = {
    generatorCache.get((path, values)) match {
      case Some(generated) => Errorable.Success(generated)
      case None =>
        val result = py.get.elaborateGeneratorRequest(path, values)
        result.map { generatorCache.put((path, values), _) }
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
