package edg.compiler

import edg.EdgirUtils.SimpleLibraryPath
import edg.IrPort
import edg.util.{Errorable, QueueStream, timeExec}
import edg.wir.{DesignPath, IndirectDesignPath, Library}
import edgir.elem.elem
import edgir.ref.ref
import edgir.schema.schema
import edgrpc.hdl.{hdl => edgrpc}

import java.io.{File, InputStream}
import scala.collection.mutable

class ProtobufSubprocessException(msg: String) extends Exception(msg)

object ProtobufStdioSubprocess {
  val kHeaderMagicByte = 0xfe
}

class ProtobufStdioSubprocess[RequestType <: scalapb.GeneratedMessage, ResponseType <: scalapb.GeneratedMessage](
    responseType: scalapb.GeneratedMessageCompanion[ResponseType],
    pythonPaths: Seq[String],
    args: Seq[String]
) {
  protected val process: Either[Process, Throwable] =
    try {
      val processBuilder = new ProcessBuilder(args: _*)
      if (pythonPaths.nonEmpty) {
        val env = processBuilder.environment()
        val pythonPathString = pythonPaths.mkString(";")
        Option(env.get("PYTHONPATH")) match { // merge existing PYTHONPATH if exists
          case None => env.put("PYTHONPATH", pythonPathString)
          case Some(envPythonPath) => env.put("PYTHONPATH", envPythonPath + ";" + pythonPathString)
        }
      }
      Left(processBuilder.start())
    } catch {
      case e: Throwable => Right(e) // if it fails store the exception to be thrown when we can
    }

  // this provides a consistent Stream interface for both stdout and stderr
  // don't use PipedInputStream since it has a non-expanding buffer and is not single-thread safe
  val outputStream = new QueueStream()
  val errorStream: InputStream = process match { // the raw error stream from the process
    case Left(process) => process.getErrorStream
    case Right(_) => new QueueStream() // empty queue if the process never started
  }

  protected def readStreamAvailable(stream: InputStream): String = {
    var available = stream.available()
    val outputBuilder = new mutable.StringBuilder()
    while (available > 0) {
      val array = new Array[Byte](available)
      stream.read(array)
      outputBuilder.append(new String(array))
      available = stream.available()
    }
    outputBuilder.toString
  }

  def write(message: RequestType): Unit = {
    process match {
      case Right(err) =>
        throw err
      case Left(process) if !process.isAlive =>
        throw new ProtobufSubprocessException("process died, " +
          s"buffered out=${readStreamAvailable(outputStream)}, err=${readStreamAvailable(errorStream)}")
      case Left(process) =>
        process.getOutputStream.write(ProtobufStdioSubprocess.kHeaderMagicByte)
        message.writeDelimitedTo(process.getOutputStream)
        process.getOutputStream.flush()
    }
  }

  def read(): ResponseType = {
    process match {
      case Right(err) =>
        throw err
      case Left(process) if !process.isAlive =>
        throw new ProtobufSubprocessException("process died, " +
          s"buffered out=${readStreamAvailable(outputStream)}, err=${readStreamAvailable(errorStream)}")
      case Left(process) =>
        var doneReadingStdout: Boolean = false
        while (!doneReadingStdout) {
          val nextByte = process.getInputStream.read()
          if (nextByte == ProtobufStdioSubprocess.kHeaderMagicByte) {
            doneReadingStdout = true
          } else if (nextByte < 0) {
            throw new ProtobufSubprocessException(s"unexpected end of stream, got $nextByte, " +
              s"buffered out=${readStreamAvailable(outputStream)}, err=${readStreamAvailable(errorStream)}")
          } else {
            outputStream.write(nextByte)
          }
        }
        responseType.parseDelimitedFrom(process.getInputStream).get
    }
  }

  // Shuts down the stream and returns the exit value
  def shutdown(): Int = {
    process match {
      case Right(_) => -1 // give a generic failed value, otherwise doesn't need to do anything
      case Left(process) =>
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

  // Forces a shutdown even if the process is busy
  def destroy(): Unit = {
    process match {
      case Right(_) => // ignored
      case Left(process) => process.destroyForcibly()
    }
  }
}

object PythonInterface {
  private val kHdlServerFilePaths = Seq(
    ("edg_hdl_server/__main__.py", "edg_hdl_server"), // developing on this repo
    ("PolymorphicBlocks/edg_hdl_server/__main__.py", "PolymorphicBlocks.edg_hdl_server") // this repo submoduled
  )
  // returns the HDL server Python script if it exists locally, otherwise returns None.
  def serverPackageOption(root: Option[File] = None): Option[String] = {
    kHdlServerFilePaths.map { case (path, packageName) =>
      (root.map(new File(_, path)).getOrElse(new File(path)), packageName)
    }.collectFirst {
      case (file, packageName) if file.exists() => packageName
    }
  }
}

/** An interface to the Python HDL elaborator, which reads in Python HDL code and (partially) compiles them down to IR.
  * The underlying Python HDL should not change while this is open. This will not reload updated Python HDL files.
  *
  * If the serverFile is specified, run that; otherwise use "python -m edg_hdl_server" for the global package.
  */
class PythonInterface(packageName: Option[String], pythonPaths: Seq[String], pythonInterpreter: String = "python") {
  private val command = Seq(pythonInterpreter, "-u", "-m", packageName.getOrElse("edg_hdl_server"))
  protected val process = new ProtobufStdioSubprocess[edgrpc.HdlRequest, edgrpc.HdlResponse](
    edgrpc.HdlResponse,
    pythonPaths,
    command
  )
  val processOutputStream: InputStream = process.outputStream
  val processErrorStream: InputStream = process.errorStream

  def shutdown(): Int = {
    process.shutdown()
  }

  def destroy(): Unit = {
    process.destroy()
  }

  // Hooks to implement when certain actions happen
  protected def onLibraryRequest(element: ref.LibraryPath): Unit = {}
  protected def onLibraryRequestComplete(
      element: ref.LibraryPath,
      result: Errorable[(schema.Library.NS.Val, Option[edgrpc.Refinements])]
  ): Unit = {}
  protected def onElaborateGeneratorRequest(element: ref.LibraryPath, values: Map[ref.LocalPath, ExprValue]): Unit = {}
  protected def onElaborateGeneratorRequestComplete(
      element: ref.LibraryPath,
      values: Map[ref.LocalPath, ExprValue],
      result: Errorable[elem.HierarchyBlock]
  ): Unit = {}

  def getProtoVersion(): Errorable[Int] = {
    val (reply, reqTime) = timeExec {
      process.write(edgrpc.HdlRequest(
        request = edgrpc.HdlRequest.Request.GetProtoVersion(0) // dummy argument
      ))
      process.read()
    }
    reply.response match {
      case edgrpc.HdlResponse.Response.GetProtoVersion(result) =>
        Errorable.Success(result)
      case edgrpc.HdlResponse.Response.Error(err) =>
        Errorable.Error(s"while getting proto version: ${err.error}")
      case _ =>
        Errorable.Error(s"while getting proto version: invalid response")
    }
  }

  def indexModule(module: String): Errorable[Seq[ref.LibraryPath]] = {
    val request = edgrpc.ModuleName(module)
    val (reply, reqTime) = timeExec {
      process.write(edgrpc.HdlRequest(
        request = edgrpc.HdlRequest.Request.IndexModule(value = request)
      ))
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

  def libraryRequest(element: ref.LibraryPath): Errorable[(schema.Library.NS.Val, Option[edgrpc.Refinements])] = {
    onLibraryRequest(element)

    val request = edgrpc.LibraryRequest(
      element = Some(element)
    )
    val (reply, reqTime) = timeExec { // TODO plumb refinements through
      process.write(edgrpc.HdlRequest(
        request = edgrpc.HdlRequest.Request.GetLibraryElement(value = request)
      ))
      process.read()
    }
    val result = reply.response match {
      case edgrpc.HdlResponse.Response.GetLibraryElement(result) =>
        Errorable.Success((result.getElement, result.refinements))
      case edgrpc.HdlResponse.Response.Error(err) =>
        Errorable.Error(err.error)
      case _ =>
        Errorable.Error("invalid response")
    }
    onLibraryRequestComplete(element, result)
    result
  }

  def elaborateGeneratorRequest(
      element: ref.LibraryPath,
      values: Map[ref.LocalPath, ExprValue]
  ): Errorable[elem.HierarchyBlock] = {
    onElaborateGeneratorRequest(element, values)

    val request = edgrpc.GeneratorRequest(
      element = Some(element),
      values = values.map { case (valuePath, valueValue) =>
        edgrpc.ExprValue(
          path = Some(valuePath),
          value = Some(valueValue.toLit)
        )
      }.toSeq
    )
    val (reply, reqTime) = timeExec {
      process.write(edgrpc.HdlRequest(
        request = edgrpc.HdlRequest.Request.ElaborateGenerator(value = request)
      ))
      process.read()
    }
    val result = reply.response match {
      case edgrpc.HdlResponse.Response.ElaborateGenerator(result) =>
        Errorable.Success(result.getGenerated)
      case edgrpc.HdlResponse.Response.Error(err) =>
        Errorable.Error(err.error)
      case _ =>
        Errorable.Error("invalid response")
    }
    onElaborateGeneratorRequestComplete(element, values, result)
    result
  }

  protected def onRunRefinementPass(refinementPass: ref.LibraryPath): Unit = {}

  protected def onRunBackend(backend: ref.LibraryPath): Unit = {}

  protected def onRunRefinementPassComplete(
      refinementPass: ref.LibraryPath,
      result: Errorable[Map[DesignPath, ExprValue]]
  ): Unit = {}

  protected def onRunBackendComplete(backend: ref.LibraryPath, result: Errorable[Map[DesignPath, String]]): Unit = {}

  def runRefinementPass(
      refinementPass: ref.LibraryPath,
      design: schema.Design,
      solvedValues: Map[IndirectDesignPath, ExprValue]
  ): Errorable[Map[DesignPath, ExprValue]] = {
    onRunRefinementPass(refinementPass)

    val request = edgrpc.RefinementRequest(
      refinementPass = Some(refinementPass),
      design = Some(design),
      solvedValues = solvedValues.map { case (path, value) =>
        edgrpc.ExprValue(path = Some(path.toLocalPath), value = Some(value.toLit))
      }.toSeq
    )
    val (reply, reqTime) = timeExec {
      process.write(edgrpc.HdlRequest(
        request = edgrpc.HdlRequest.Request.RunRefinement(value = request)
      ))
      process.read()
    }
    val result = reply.response match {
      case edgrpc.HdlResponse.Response.RunRefinement(result) =>
        Errorable.Success(result.newValues.map { result =>
          DesignPath() ++ result.getPath -> ExprValue.fromValueLit(result.getValue)
        }.toMap)
      case edgrpc.HdlResponse.Response.Error(err) =>
        Errorable.Error(err.error)
      case _ =>
        Errorable.Error(s"invalid response")
    }
    onRunRefinementPassComplete(refinementPass, result)
    result
  }

  def runBackend(
      backend: ref.LibraryPath,
      design: schema.Design,
      solvedValues: Map[IndirectDesignPath, ExprValue],
      arguments: Map[String, String]
  ): Errorable[Map[DesignPath, String]] = {
    onRunBackend(backend)

    val request = edgrpc.BackendRequest(
      backend = Some(backend),
      design = Some(design),
      solvedValues = solvedValues.map { case (path, value) =>
        edgrpc.ExprValue(path = Some(path.toLocalPath), value = Some(value.toLit))
      }.toSeq,
      arguments = arguments
    )
    val (reply, reqTime) = timeExec {
      process.write(edgrpc.HdlRequest(
        request = edgrpc.HdlRequest.Request.RunBackend(value = request)
      ))
      process.read()
    }
    val result = reply.response match {
      case edgrpc.HdlResponse.Response.RunBackend(result) =>
        Errorable.Success(result.results.map { result =>
          DesignPath() ++ result.getPath -> result.getText
        }.toMap)
      case edgrpc.HdlResponse.Response.Error(err) =>
        Errorable.Error(err.error)
      case _ =>
        Errorable.Error("invalid response")
    }
    onRunBackendComplete(backend, result)
    result
  }
}

class PythonInterfaceLibrary() extends Library {
  private val elts = mutable.HashMap[ref.LibraryPath, schema.Library.NS.Val.Type]()
  private val eltsRefinements = mutable.HashMap[ref.LibraryPath, edgrpc.Refinements]()
  private val generatorCache = mutable.HashMap[(ref.LibraryPath, Map[ref.LocalPath, ExprValue]), elem.HierarchyBlock]()

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

  private def getLibraryPartialMapped[T](
      path: ref.LibraryPath,
      expectedType: String
  )(mapping: PartialFunction[schema.Library.NS.Val.Type, T]): Errorable[T] = {
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

  override def getBlock(path: ref.LibraryPath, ignoreRefinements: Boolean = false): Errorable[elem.HierarchyBlock] = {
    getLibraryPartialMapped(path, "block") {
      case schema.Library.NS.Val.Type.HierarchyBlock(member) =>
        require(
          ignoreRefinements || !eltsRefinements.isDefinedAt(path),
          s"non-design-top ${path.toSimpleString} may not have refinements"
        )
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

  override def runGenerator(
      path: ref.LibraryPath,
      values: Map[ref.LocalPath, ExprValue]
  ): Errorable[elem.HierarchyBlock] = {
    generatorCache.get((path, values)) match {
      case Some(generated) => Errorable.Success(generated)
      case None =>
        val result = py.get.elaborateGeneratorRequest(path, values)
        result.map { generatorCache.put((path, values), _) }
        result
    }
  }

  def toLibraryPb: schema.Library = {
    schema.Library(root =
      Some(schema.Library.NS(
        members = elts.toMap.collect {
          case (path, elt) if !eltsRefinements.contains(path) =>
            // TODO: in future, refinements should be saved; right now the entire element is ignored
            // to prevent the block from loading without the refinements
            path.getTarget.getName -> schema.Library.NS.Val(elt)
        }
      ))
    )
  }

  def loadFromLibraryPb(library: schema.Library): Unit = {
    library.root.getOrElse(schema.Library.NS()).members.foreach { case (name, elt) =>
      val path = ref.LibraryPath(target = Some(ref.LocalStep(step = ref.LocalStep.Step.Name(name))))
      require(!elts.isDefinedAt(path), s"overwriting $name in loadFromLibraryPb")
      elts.put(path, elt.`type`)
    }
  }
}
