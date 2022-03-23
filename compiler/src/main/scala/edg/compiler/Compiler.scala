package edg.compiler

import scala.collection.{SeqMap, mutable}
import edgir.schema.schema
import edgir.expr.expr
import edgir.ref.ref
import edgir.ref.ref.{LibraryPath, LocalPath}
import edg.wir.{DesignPath, IndirectDesignPath, IndirectStep, PathSuffix, PortLike, Refinements}
import edg.{EdgirUtils, ExprBuilder, wir}
import edg.util.{DependencyGraph, Errorable, SingleWriteHashMap}
import EdgirUtils._


class IllegalConstraintException(msg: String) extends Exception(msg)


sealed trait ElaborateRecord
object ElaborateRecord {
  sealed trait ElaborateTask extends ElaborateRecord  // an elaboration task that can be run
  sealed trait ElaborateDependency extends ElaborateRecord  // an elaboration dependency source

  case class Block(blockPath: DesignPath) extends ElaborateTask  // even when done, still may only be a generator
  case class Link(linkPath: DesignPath) extends ElaborateTask

  // Connection to be elaborated, to set port parameter, IS_CONNECTED, and CONNECTED_LINK equivalences.
  // Only elaborates the direct connect, and for bundles, creates sub-Connect tasks since it needs
  // connectedLink and linkParams.
  case class Connect(toLinkPortPath: DesignPath, toBlockPortPath: DesignPath)
      extends ElaborateTask

  // Elaborates the contents of a port array, based on the port array's ELEMENTS parameter.
  // Only called for port arrays without defined elements (so excluding blocks that define their ports, including
  // generator-defined port arrays which are structurally similar).
  // Created but never run for abstract blocks with abstract port array).
  case class ElaboratePortArray(path: DesignPath) extends ElaborateTask

  // Lowers array-allocate connections to individual leaf-level allocate connections, once all array connections to
  // a port array are of known length.
  // Also defines the ALLOCATED param of the port array (giving an arbitrary name to anonymous ALLOCATEs) and
  // creates the task to lower the ALLOCATE steps..
  // Also created for port arrays that have no array-connects, to define the ALLOCATE parameter.
  // constraintNames includes all ALLOCATEs to the target port, whether array or not.
  case class LowerArrayAllocateConnections(parent: DesignPath, portPath: Seq[String], constraintNames: Seq[String],
                                           portIsLink: Boolean) extends ElaborateTask

  // Lowers leaf-level allocate connections by replacing the ALLOCATE with a port name.
  // Requires array-allocate connections have been already lowered to leaf-level allocate connections, and that
  // the port's ELEMENTS have been defined.
  case class LowerAllocateConnections(parent: DesignPath, portPath: Seq[String], constraintNames: Seq[String],
                                      portIsLink: Boolean) extends ElaborateTask

  case class ParamValue(paramPath: IndirectDesignPath) extends ElaborateDependency  // when solved

  // Set when the connection from the link's port to portPath have been elaborated, or for link ports
  // when the link has been elaborated.
  // When this is completed, connectedLink for the port and linkParams for the link will be set.
  // If the portPath is an port array, this is set once all the constituent connections are set, if there are any.
  // For arrays with no connections, this will never be set.
  case class ConnectedLink(portPath: DesignPath) extends ElaborateDependency
}


sealed trait CompilerError
object CompilerError {
  case class Unelaborated(elaborateRecord: ElaborateRecord, missing: Set[ElaborateRecord]) extends CompilerError {
    // These errors may be redundant with below, but provides dependency data
    override def toString: String = s"Unelaborated missing dependencies $elaborateRecord:\n" +
        s"${missing.map(x => s"- $x").mkString("\n")}"
  }
  case class LibraryElement(path: DesignPath, target: ref.LibraryPath) extends CompilerError {
    override def toString: String = s"Unelaborated library element ${target.toSimpleString} @ $path"
  }
  case class UndefinedPortArray(path: DesignPath, portType: ref.LibraryPath) extends CompilerError {
    override def toString: String = s"Undefined port array ${portType.toSimpleString} @ $path"
  }

  case class LibraryError(path: DesignPath, target: ref.LibraryPath, err: String) extends CompilerError {
    override def toString: String = s"Library error ${target.toSimpleString} @ $path: $err"
  }
  case class GeneratorError(path: DesignPath, target: ref.LibraryPath, fn: String, err: String) extends CompilerError {
    override def toString: String = s"Generator error ${target.toSimpleString}.$fn @ $path: $err"
  }
  case class RefinementSubclassError(path: DesignPath, refinedLibrary: ref.LibraryPath, designLibrary: ref.LibraryPath)
      extends CompilerError {
    override def toString: String =
      s"Invalid refinement ${refinedLibrary.toSimpleString} <- ${designLibrary.toSimpleString} @ $path"
  }

  case class OverAssign(target: IndirectDesignPath,
                        causes: Seq[OverAssignCause]) extends CompilerError {
    override def toString: String = s"Overassign to $target:\n" +
        s"${causes.map(x => s"- $x").mkString("\n")}"
  }

  case class BadRef(path: DesignPath, ref: IndirectDesignPath) extends CompilerError

  case class AbstractBlock(path: DesignPath, blockType: ref.LibraryPath) extends CompilerError {
    override def toString: String = s"Abstract block: $path (of type ${blockType.toSimpleString})"
  }

  case class FailedAssertion(root: DesignPath, constrName: String,
                             value: expr.ValueExpr, result: ExprValue) extends CompilerError {
    override def toString: String =
      s"Failed assertion: $root.$constrName, ${ExprToString.apply(value)} => $result"
  }
  case class MissingAssertion(root: DesignPath, constrName: String,
                              value: expr.ValueExpr, missing: Set[IndirectDesignPath]) extends CompilerError {
    override def toString: String =
      s"Unevaluated assertion: $root.$constrName (${ExprToString.apply(value)}), missing ${missing.mkString(", ")}"
  }

  // TODO should this be an error? Currently a debugging tool
  case class EmptyRange(param: IndirectDesignPath, root: DesignPath, constrName: String,
                        value: expr.ValueExpr) extends CompilerError

  sealed trait OverAssignCause
  object OverAssignCause {
    case class Assign(target: IndirectDesignPath, root: DesignPath, constrName: String, value: expr.ValueExpr)
        extends OverAssignCause {
      override def toString = s"Assign $target <- ${ExprToString(value)} @ $root.$constrName"
    }
    case class Equal(target: IndirectDesignPath, source: IndirectDesignPath)  // TODO constraint info once we track that?
        extends OverAssignCause {
      override def toString = s"Equals $target = $source"
    }
  }
}


/** Compiler for a particular design, with an associated library to elaborate references from.
  * TODO also needs a Python interface for generators, somewhere.
  *
  * During the compilation process, internal data structures are mutated.
  *
  * Port parameters are propagated by expanding connect and export statements between connected ports
  * into equalities between all contained parameters.
  * This expansion triggers when both ports are fully elaborated, and checks the structures of both ends
  * for equivalence.
  *
  * CONNECTED_LINK parameters are propagated by expanding from the link's top-level port outward.
  * Expansion triggers at the link-side top-level port (by ref matching), or when the towards-innermost-link
  * (or towards-outermost-block) port is expanded.
  * A list of link params is kept in a hashmap indexed by ports, as they are expanded.
  *
  * Alternative: fetch links from library (using the port type) to get params to expand.
  * Problem: a bit more restrictive than what can be expressed in a block - but should be a common interface.
  *
  * It is intentional to allow a link-side port to access the CONNECTED_LINK, as a mechanism to access inner links.
  */
class Compiler(inputDesignPb: schema.Design, library: edg.wir.Library,
               refinements: Refinements=Refinements()) {
  // TODO better debug toggle
//  protected def debug(msg: => String): Unit = println(msg)
  protected def debug(msg: => String): Unit = { }

  def readableLibraryPath(path: ref.LibraryPath): String = {  // TODO refactor to shared utils?
    path.getTarget.getName
  }

  // Working design tree data structure
  private var root = new wir.Block(inputDesignPb.getContents, None)  // TODO refactor to unify root / non-root cases
  def resolve(path: DesignPath): wir.Pathable = root.resolve(path.steps)
  def resolveBlock(path: DesignPath): wir.BlockLike = root.resolve(path.steps).asInstanceOf[wir.BlockLike]
  def resolveLink(path: DesignPath): wir.LinkLike = root.resolve(path.steps).asInstanceOf[wir.LinkLike]
  def resolvePort(path: DesignPath): wir.PortLike = root.resolve(path.steps).asInstanceOf[wir.PortLike]

  // Main data structure that tracks the next unit to elaborate
  private val elaboratePending = DependencyGraph[ElaborateRecord, None.type]()

  // Design parameters solving (constraint evaluation) and assertions
  private val constProp = new ConstProp() {
    override def onParamSolved(param: IndirectDesignPath, value: ExprValue): Unit = {
      elaboratePending.setValue(ElaborateRecord.ParamValue(param), null)
    }
  }
  private[edg] def getValue(path: IndirectDesignPath): Option[ExprValue] = constProp.getValue(path)  // TODO clean up this API?
  for ((path, value) <- refinements.instanceValues) {  // seed const prop with path assertions
    constProp.setForcedValue(path.asIndirect, value, "path refinement")
  }

  private val assertions = mutable.Buffer[(DesignPath, String, expr.ValueExpr, SourceLocator)]()  // containing block, name, expr

  // Supplemental elaboration data structures
  private val linkParams = SingleWriteHashMap[DesignPath, Seq[IndirectStep]]()  // link path -> list of params
  linkParams.put(DesignPath(), Seq())  // empty path means disconnected
  private val connectedLink = SingleWriteHashMap[DesignPath, DesignPath]()  // port -> connected link path

  private val errors = mutable.ListBuffer[CompilerError]()

  // Returns all errors, by scanning the design tree for errors and adding errors accumulated through the compile
  // process
  def getErrors(): Seq[CompilerError] = {
    val assertionErrors = assertions.flatMap { case (root, constrName, value, sourceLocator) =>
      new ExprEvaluatePartial(constProp, root).map(value) match {
        case ExprResult.Result(BooleanValue(true)) => None
        case ExprResult.Result(result) =>
          Some(CompilerError.FailedAssertion(root, constrName, value, result))
        case ExprResult.Missing(missing) =>
          Some(CompilerError.MissingAssertion(root, constrName, value, missing))
      }
    }.toSeq

    val pendingErrors = elaboratePending.getMissing.map { missingNode =>
      CompilerError.Unelaborated(missingNode, elaboratePending.nodeMissing(missingNode))
    }.toSeq

    errors.toSeq ++ constProp.getErrors ++ pendingErrors ++ assertionErrors
  }

  // Seed the elaboration record with the root design
  //
  elaboratePending.addNode(ElaborateRecord.Block(DesignPath()), Seq())
  require(root.getElaboratedPorts.isEmpty, "design top may not have ports")  // also don't need to elaborate top ports
  processParamDeclarations(DesignPath(), root)

  // Hook method to be overridden, eg for status
  //
  def onElaborate(record: ElaborateRecord): Unit = { }

  // Actual compilation methods
  //

  // Elaborate a connection (either a connect or export), by generating bidirectional equality constraints
  // including link parameters (through CONNECTED_LINK) and IS_CONNECTED.
  // Neither port can be an array (container) port (array connects should be expanded into individual element connects),
  // but ports may be bundle or inner ports (in bundles or arrays).
  // Only the link side port needs to have been elaborated.
  protected def elaborateConnect(connect: ElaborateRecord.Connect): Unit = {
    // Generate port-port parameter propagation
    // All connected ports should have params
    val toLinkPort = resolvePort(connect.toLinkPortPath).asInstanceOf[wir.HasParams]
    val connectedSteps = toLinkPort.getParams.keys.map(IndirectStep.Element(_)) ++ Seq(IndirectStep.IsConnected)
    for (connectedStep <- connectedSteps) {
      constProp.addEquality(
        connect.toLinkPortPath.asIndirect + connectedStep,
        connect.toBlockPortPath.asIndirect + connectedStep
      )
    }

    val linkPath = connectedLink(connect.toLinkPortPath)  // must have ben set with ConnectedLink
    connectedLink.put(connect.toBlockPortPath, linkPath)  // propagate CONNECTED_LINK params
    val allParams = linkParams(linkPath) :+ IndirectStep.Name
    for (linkParam <- allParams) {  // generate CONNECTED_LINK equalities
      constProp.addEquality(
        connect.toBlockPortPath.asIndirect + IndirectStep.ConnectedLink + linkParam,
        linkPath.asIndirect + linkParam,
      )
    }

    // Add sub-ports to the elaboration dependency graph, as appropriate
    toLinkPort match {
      case toLinkPort: wir.Bundle =>
        for (portName <- toLinkPort.getElaboratedPorts.keys) {
          constProp.addEquality(connect.toLinkPortPath.asIndirect + IndirectStep.IsConnected,
            connect.toLinkPortPath.asIndirect + portName + IndirectStep.IsConnected)
          constProp.addEquality(connect.toBlockPortPath.asIndirect + IndirectStep.IsConnected,
            connect.toBlockPortPath.asIndirect + portName + IndirectStep.IsConnected)

          elaboratePending.addNode(
            ElaborateRecord.Connect(connect.toLinkPortPath + portName, connect.toBlockPortPath + portName),
            Seq(ElaborateRecord.ConnectedLink(connect.toLinkPortPath + portName))
          )
        }
      case toLinkPort => // everything else ignored
    }

    // Register port as finished
    elaboratePending.setValue(ElaborateRecord.ConnectedLink(connect.toBlockPortPath), None)
  }

  protected def resolvePortConnectivity(containerPath: DesignPath, portPostfix: Seq[String],
                                        constraint: Option[(String, expr.ValueExpr)]): Unit = {
    val port = resolvePort(containerPath ++ portPostfix)
    val container = resolve(containerPath).asInstanceOf[wir.HasMutableConstraints]  // block or link
    val portBlock = resolve(containerPath + portPostfix.head).asInstanceOf[wir.HasMutableConstraints]  // block or link
    val constraintExpr = constraint.map { case (constrName, constr) => (constrName, constr.expr) }

    def recursiveSetNotConnected(portPath: DesignPath, port: wir.PortLike): Unit = {
      constProp.setValue(portPath.asIndirect + IndirectStep.IsConnected,
        BooleanValue(false),
        s"${containerPath ++ portPostfix}.(not connected)")
      portBlock match {
        case _: wir.Block =>
          connectedLink.put(portPath, DesignPath())
          elaboratePending.setValue(ElaborateRecord.ConnectedLink(portPath), None)
        case _: wir.Link =>  // do nothing
      }
      port match {
        case port: wir.Bundle =>
          port.getMixedPorts.foreach { case (innerIndex, innerPort) =>
            recursiveSetNotConnected(portPath + innerIndex, innerPort)
          }
        case _ =>  // no recursion at leaf
      }
    }

    port match {
      case _: wir.Bundle | _: wir.Port => constraintExpr match {
        case Some((constrName, expr.ValueExpr.Expr.Connected(connected))) =>
          require(container.isInstanceOf[wir.Block])
          constProp.setValue(containerPath.asIndirect ++ portPostfix + IndirectStep.IsConnected,
            BooleanValue(true),
            s"$containerPath.$constrName")
        case Some((constrName, expr.ValueExpr.Expr.Exported(exported))) =>
          constProp.addDirectedEquality(containerPath.asIndirect ++ portPostfix + IndirectStep.IsConnected,
            containerPath.asIndirect ++ exported.getExteriorPort.getRef + IndirectStep.IsConnected,
            containerPath, s"$containerPath.$constrName")
        case None =>
          recursiveSetNotConnected(containerPath ++ portPostfix, port)
        case Some((_, _)) => throw new IllegalArgumentException
      }
      case _: wir.PortLibrary => throw new IllegalArgumentException
      case _: wir.PortArray => throw new IllegalArgumentException  // must be lowered before
    }
  }

  // Called for each param declaration, currently just registers the declaration and type signature.
  protected def processParamDeclarations(path: DesignPath, hasParams: wir.HasParams): Unit = {
    for ((paramName, param) <- hasParams.getParams) {
      constProp.addDeclaration(path + paramName, param)
    }
  }

  // Elaborates the port, mutating it in-place. Recursive.
  protected def elaboratePort(path: DesignPath, container: wir.HasMutablePorts, port: wir.PortLike): Unit = {
    // Instantiate as needed
    val instantiated = port match {
      case port: wir.PortLibrary =>
        val libraryPath = port.target
        debug(s"Elaborate port @ $path")

        val portPb = library.getPort(libraryPath) match {
          case Errorable.Success(portPb) => portPb
          case Errorable.Error(err) =>
            import edgir.elem.elem, edg.IrPort
            errors += CompilerError.LibraryError(path, libraryPath, err)
            IrPort.Port(elem.Port())
        }
        val newPort = wir.PortLike.fromIrPort(portPb)
        container.elaborate(path.lastString, newPort)
        newPort
      case port: wir.PortArray => port  // no instantiation needed
      case port => throw new NotImplementedError(s"unknown unelaborated port $port")
    }

    // Process and recurse as needed
    instantiated match {
      case port: wir.Port =>
        constProp.setValue(path.asIndirect + IndirectStep.Name, TextValue(path.toString))
        processParamDeclarations(path, port)
      case port: wir.Bundle =>
        constProp.setValue(path.asIndirect + IndirectStep.Name, TextValue(path.toString))
        processParamDeclarations(path, port)
        for ((childPortName, childPort) <- port.getUnelaboratedPorts) {
          elaboratePort(path + childPortName, port, childPort)
        }
      case port: wir.PortArray =>
        if (port.portsSet) {  // set ELEMENTS if ports is defined by array, otherwise ports are dependent on ELEMENTS
          constProp.setValue(path.asIndirect + IndirectStep.Elements,
            ArrayValue(port.getUnelaboratedPorts.keys.toSeq.map(TextValue(_))))
        }
        elaboratePending.addNode(ElaborateRecord.ElaboratePortArray(path), Seq(  // does recursive elaboration + LENGTH
          ElaborateRecord.ParamValue(path.asIndirect + IndirectStep.Elements)
        ))
      case port => throw new NotImplementedError(s"unknown instantiated port $port")
    }
  }

  // Attempts to process a parameter constraint, returning true if it is a matching constraint
  def processParamConstraint(blockPath: DesignPath, constrName: String, constr: expr.ValueExpr,
                             constrValue: expr.ValueExpr): Boolean = constrValue.expr match {
    case expr.ValueExpr.Expr.Assign(assign) =>
      constProp.addAssignment(
        blockPath.asIndirect ++ assign.dst.get,
        blockPath, assign.src.get, constrName) // TODO add sourcelocators
      true
    case expr.ValueExpr.Expr.Binary(_) | expr.ValueExpr.Expr.BinarySet(_) |
        expr.ValueExpr.Expr.Unary(_) | expr.ValueExpr.Expr.UnarySet(_) |
        expr.ValueExpr.Expr.IfThenElse(_) =>
      assertions += ((blockPath, constrName, constr, SourceLocator.empty))  // TODO add source locators
      true
    case expr.ValueExpr.Expr.Ref(target)
      if target.steps.last.step.isReservedParam
          && target.steps.last.getReservedParam == ref.Reserved.IS_CONNECTED =>
      assertions += ((blockPath, constrName, constr, SourceLocator.empty))  // TODO add source locators
      true
    case _ => false
  }

  // Attempts to process a connected constraint, returning true if it is a matching constraint
  def processConnectedConstraint(blockPath: DesignPath, constrName: String, constr: expr.ValueExpr,
                                 isLink: Boolean): Boolean = {
    import edg.ExprBuilder.ValueExpr
    constr.expr match {
      case expr.ValueExpr.Expr.Connected(connected) => (connected.getBlockPort, connected.getLinkPort) match {
        case (ValueExpr.Ref(blockPort), ValueExpr.Ref(linkPort)) =>
          require(!isLink)
          elaboratePending.addNode(
            ElaborateRecord.Connect(blockPath ++ linkPort, blockPath ++ blockPort),
            Seq(ElaborateRecord.ConnectedLink(blockPath ++ linkPort))
          )
          true
        case _ => false  // anything with allocates is not processed
      }
      case expr.ValueExpr.Expr.Exported(exported) => (exported.getExteriorPort, exported.getInternalBlockPort) match {
        case (ValueExpr.Ref(extPort), ValueExpr.Ref(intPort)) =>
          if (!isLink) {
            elaboratePending.addNode(
              ElaborateRecord.Connect(blockPath ++ extPort, blockPath ++ intPort),
              Seq(ElaborateRecord.ConnectedLink(blockPath ++ extPort))
            )
          } else {  // for links, the external port faces to the block, so args must be flipped
            elaboratePending.addNode(
              ElaborateRecord.Connect(blockPath ++ intPort, blockPath ++ extPort),
              Seq(ElaborateRecord.ConnectedLink(blockPath ++ intPort))
            )
          }
          true
        case _ => false  // anything with allocates is not processed
      }
      case _ => false  // not defined
    }
  }

  // Given a block library at some path, expand it and return the instantiated block.
  // Handles class type refinements and adds default parameters and class-based value refinements
  // For the generator, this will be a skeleton block.
  protected def expandBlock(path: DesignPath, block: wir.BlockLibrary): wir.Block = {
    val libraryPath = block.target

    val (refinedLibraryPath, unrefinedType) = refinements.instanceRefinements.get(path) match {
      case Some(refinement) => (refinement, Some(libraryPath))
      case None => refinements.classRefinements.get(libraryPath) match {
        case Some(refinement) => (refinement, Some(libraryPath))
        case None => (libraryPath, None)
      }
    }

    val blockPb = library.getBlock(refinedLibraryPath) match {
      case Errorable.Success(blockPb) =>
        blockPb
      case Errorable.Error(err) =>
        import edgir.elem.elem
        errors += CompilerError.LibraryError(path, refinedLibraryPath, err)
        elem.HierarchyBlock()
    }

    // additional processing needed for the refinement case
    if (unrefinedType.isDefined) {
      if (!library.isSubclassOf(refinedLibraryPath, libraryPath)) {  // check refinement validity
        errors += CompilerError.RefinementSubclassError(path, refinedLibraryPath, libraryPath)
      }

      val unrefinedPb = library.getBlock(libraryPath) match {  // add subclass (refinement) default params
        case Errorable.Success(unrefinedPb) =>
          unrefinedPb
        case Errorable.Error(err) =>  // this doesn't stop elaboration, but does raise an error
          import edgir.elem.elem
          errors += CompilerError.LibraryError(path, libraryPath, err)
          elem.HierarchyBlock()
      }
      val refinedNewParams = blockPb.params.keys.toSet -- unrefinedPb.params.keys
      refinedNewParams.foreach { refinedNewParam =>
        blockPb.paramDefaults.get(refinedNewParam).foreach { refinedDefault =>
          constProp.addAssignment(path.asIndirect + refinedNewParam, path, refinedDefault,
            s"(default)${refinedLibraryPath.toSimpleString}.$refinedNewParam")
        }
      }
    }

    // add class-based refinements
    refinements.classValues.get(refinedLibraryPath).foreach { classValueRefinements =>
      for ((subpath, value) <- classValueRefinements) {
        constProp.setForcedValue(path.asIndirect ++ subpath, value,
          s"${refinedLibraryPath.getTarget.getName} class refinement")
      }
    }

    val newBlock = if (blockPb.generators.isEmpty) {
      new wir.Block(blockPb, unrefinedType)
    } else {
      new wir.Generator(blockPb, unrefinedType)
    }

    constProp.setValue(path.asIndirect + IndirectStep.Name, TextValue(path.toString))
    processParamDeclarations(path, newBlock)

    newBlock.getUnelaboratedPorts.foreach { case (portName, port) =>  // all other cases, elaborate in place
      elaboratePort(path + portName, newBlock, port)
    }

    val deps = newBlock match {
      case newBlock: wir.Generator =>
        val generatorParams = newBlock.getDependencies.map { depPath =>
          ElaborateRecord.ParamValue(path.asIndirect ++ depPath)
        }
        val generatorPorts = newBlock.getDependenciesPorts.map { depPort =>  // TODO remove this with refactoring
          ElaborateRecord.ConnectedLink(path ++ depPort)
        }
        generatorParams ++ generatorPorts
      case _ => Seq()
    }
    elaboratePending.addNode(ElaborateRecord.Block(path), deps)

    newBlock
  }

  // Given a link library at some path, expand it and return the instantiated block.
  protected def expandLink(path: DesignPath, link: wir.LinkLibrary): wir.Link = {
    val libraryPath = link.target

    val linkPb = library.getLink(libraryPath) match {
      case Errorable.Success(linkPb) => linkPb
      case Errorable.Error(err) =>
        import edgir.elem.elem
        errors += CompilerError.LibraryError(path, libraryPath, err)
        elem.Link()
    }

    val newLink = new wir.Link(linkPb)

    // Elaborate ports and parameters
    constProp.setValue(path.asIndirect + IndirectStep.Name, TextValue(path.toString))
    processParamDeclarations(path, newLink)
    linkParams.put(path, linkPb.params.keys.toSeq.map(IndirectStep.Element(_)))

    newLink.getUnelaboratedPorts.foreach { case (portName, port) =>
      elaboratePort(path + portName, newLink, port)
    }

    // For link-side port arrays: set ALLOCATED -> ELEMENTS and allow it to expand later
    newLink.getMixedPorts.collect { case (portName, port: wir.PortArray) =>
      require(!port.portsSet) // links can't have fixed array elts
      constProp.addDirectedEquality(
        path.asIndirect + portName + IndirectStep.Elements, path.asIndirect + portName + IndirectStep.Allocated,
          path, s"$path.$portName (link array-from-connects)")
    }

    // Links can only elaborate when their port arrays are ready
    val arrayDeps = newLink.getMixedPorts.collect {
      case (portName, arr: wir.PortArray) => ElaborateRecord.ElaboratePortArray(path + portName)
    }.toSeq
    elaboratePending.addNode(ElaborateRecord.Link(path), arrayDeps)

    newLink
  }

  protected def runGenerator(path: DesignPath, generator: wir.Generator): Unit = {
    val reqParamValues = generator.getDependencies.map { reqParam =>
      reqParam -> constProp.getValue(path.asIndirect ++ reqParam).get
    }
    val reqPortValues = generator.getDependenciesPorts.flatMap { reqPort =>
      val isConnectedSuffix = PathSuffix() ++ reqPort + IndirectStep.IsConnected
      val connectedNameSuffix = PathSuffix() ++ reqPort + IndirectStep.ConnectedLink + IndirectStep.Name
      Seq(
        isConnectedSuffix -> constProp.getValue(path.asIndirect ++ isConnectedSuffix).get,
        connectedNameSuffix -> constProp.getValue(path.asIndirect ++ connectedNameSuffix).getOrElse(TextValue("")),
      )
    }.map { case (param, value) =>
      param.asLocalPath() -> value
    }

    // Run generator and plug in
    library.runGenerator(generator.getBlockClass, generator.getFnName,
      (reqParamValues ++ reqPortValues).toMap
    ) match {
      case Errorable.Success(generatedPb) =>
        val generatedPorts = generator.applyGenerated(generatedPb)
        generatedPorts.foreach { portName =>
          val portArray = generator.getUnelaboratedPorts(portName).asInstanceOf[wir.PortArray]
          constProp.setValue(path.asIndirect + portName + IndirectStep.Elements,
            ArrayValue(portArray.getUnelaboratedPorts.keys.toSeq.map(TextValue(_))))
          // the rest was already handled when elaboratePorts on the generator stub
        }
      case Errorable.Error(err) =>
        errors += CompilerError.GeneratorError(path, generator.getBlockClass, generator.getFnName, err)
    }
  }

  /** Elaborate the unelaborated block at path (but where the parent has been elaborated and is reachable from root),
    * and adds it to the parent and replaces the lib_elem proto entry with a placeholder unknown.
    * Adds children to the pending queue, and adds constraints to constProp.
    * Expands connects in the parent, as needed.
    */
  protected def elaborateBlock(path: DesignPath): Unit = {
    val block = resolveBlock(path).asInstanceOf[wir.Block]

    block match {
      case block: wir.Generator => runGenerator(path, block)
      case _ =>  // ignored
    }

    // Queue up sub-trees that need elaboration - needs to be post-generate for generators
    // subtree ports can't know connected state until own connected state known
    block.getUnelaboratedBlocks.foreach { case (innerBlockName, innerBlock) =>
      val innerBlockElaborated = expandBlock(path + innerBlockName, innerBlock.asInstanceOf[wir.BlockLibrary])
      block.elaborate(innerBlockName, innerBlockElaborated)
    }

    block.getUnelaboratedLinks.foreach { case (innerLinkName, innerLink) =>
      val innerLinkElaborated = expandLink(path + innerLinkName, innerLink.asInstanceOf[wir.LinkLibrary])
      block.elaborate(innerLinkName, innerLinkElaborated)
    }

    // Find allocate ports and generate the port array lowering compiler tasks
    val blockAllocateConstraints = mutable.HashMap[Seq[String], mutable.ListBuffer[String]]()  // port array path -> constraint names
    val linkAllocateConstraints = mutable.HashMap[Seq[String], mutable.ListBuffer[String]]()  // port array path -> constraint names
    val blockConnectedConstraint = SingleWriteHashMap[Seq[String], String]()  // port path -> constraint name
    val linkConnectedConstraint = SingleWriteHashMap[Seq[String], String]()  // port path -> constraint name
    val connectedPortArrays = mutable.Set[DesignPath]()

    import edg.ExprBuilder.ValueExpr
    block.getConstraints.foreach { case (constrName, constr) => constr.expr match {
      case expr.ValueExpr.Expr.Connected(connected) => (connected.getBlockPort, connected.getLinkPort) match {
        case (ValueExpr.RefAllocate(blockPortArray, _), ValueExpr.RefAllocate(linkPortArray, _)) =>
          blockAllocateConstraints.getOrElseUpdate(blockPortArray, mutable.ListBuffer()).append(constrName)
          linkAllocateConstraints.getOrElseUpdate(linkPortArray, mutable.ListBuffer()).append(constrName)

          require(blockPortArray.length == 2)
          connectedPortArrays.add(path ++ blockPortArray)
        case (ValueExpr.RefAllocate(blockPortArray, _), ValueExpr.Ref(linkPort)) =>
          blockAllocateConstraints.getOrElseUpdate(blockPortArray, mutable.ListBuffer()).append(constrName)
          linkConnectedConstraint.put(linkPort, constrName)

          require(blockPortArray.length == 2)
          connectedPortArrays.add(path ++ blockPortArray)
        case (ValueExpr.Ref(blockPort), ValueExpr.RefAllocate(linkPortArray, _)) =>
          blockConnectedConstraint.put(blockPort, constrName)
          linkAllocateConstraints.getOrElseUpdate(linkPortArray, mutable.ListBuffer()).append(constrName)
        case (ValueExpr.Ref(blockPort), ValueExpr.Ref(linkPort)) =>
          blockConnectedConstraint.put(blockPort, constrName)
          linkConnectedConstraint.getOrElseUpdate(linkPort, constrName)
        case _ => throw new AssertionError("impossible connected format")
      }
      case expr.ValueExpr.Expr.Exported(exported) => (exported.getExteriorPort, exported.getInternalBlockPort) match {
        case (_, ValueExpr.RefAllocate(intPortArray, _)) =>
          blockAllocateConstraints.getOrElseUpdate(intPortArray, mutable.ListBuffer()).append(constrName)

          require(intPortArray.length == 2)
          connectedPortArrays.add(path ++ intPortArray)
        case (_, ValueExpr.Ref(intPort)) =>
          blockConnectedConstraint.put(intPort, constrName)

        case _ => throw new AssertionError("impossible exported format")
      }
      case _ =>  // all other constraints ignored
    }}

    // Set IsConnected
    block.getElaboratedBlocks.foreach { case (innerBlockName, innerBlock) =>
      innerBlock.asInstanceOf[wir.Block].getMixedPorts.foreach { case (portName, port) =>
        val portPostfix = Seq(innerBlockName, portName)
        port match {
          case _: wir.PortArray =>  // array case: ignored, handled in lowering
            val constrNames = blockAllocateConstraints.getOrElse(portPostfix, Seq()).toSeq
            val lowerArrayTask = ElaborateRecord.LowerArrayAllocateConnections(path, portPostfix, constrNames, false)
            elaboratePending.addNode(lowerArrayTask, Seq())  // TODO add array-connect dependencies
          case _ =>
            val constraintOption = blockConnectedConstraint.get(portPostfix).map { constrName =>
              (constrName, block.getConstraints(constrName))
            }
            resolvePortConnectivity(path, portPostfix, constraintOption)
        }
      }
    }

    block.getElaboratedLinks.foreach { case (innerLinkName, innerLink) =>
      innerLink.asInstanceOf[wir.Link].getMixedPorts.foreach { case (portName, port) =>
        val portPostfix = Seq(innerLinkName, portName)
        port match {
          case _: wir.PortArray =>  // array case: ignored, handled in lowering
            val constraints = linkAllocateConstraints.getOrElse(portPostfix, Seq()).toSeq
            val lowerArrayTask = ElaborateRecord.LowerArrayAllocateConnections(
              path, portPostfix, constraints, false)
            elaboratePending.addNode(lowerArrayTask, Seq())  // TODO add array-connect dependencies
          case _ =>
            val constraintOption = linkConnectedConstraint.get(portPostfix).map { constrName =>
              (constrName, block.getConstraints(constrName))
            }
            resolvePortConnectivity(path, portPostfix, constraintOption)
        }
      }
    }

    // Process all the process-able constraints: parameter constraints and non-allocate connected
    block.getConstraints.foreach { case (constrName, constr) =>
      processParamConstraint(path, constrName, constr, constr)
      processConnectedConstraint(path, constrName, constr, false)
    }
  }

  /** Elaborate the unelaborated link at path (but where the parent has been elaborated and is reachable from root),
    * and adds it to the parent and replaces the lib_elem proto entry with a placeholder unknown.
    * Adds children to the pending queue, and adds constraints to constProp.
    * Expands connects in the parent, as needed.
    */
  protected def elaborateLink(path: DesignPath): Unit = {
    import edg.ExprBuilder.{Ref, ValueExpr}
    val link = resolveLink(path).asInstanceOf[wir.Link]

    // Queue up sub-trees that need elaboration
    link.getUnelaboratedLinks.foreach { case (innerLinkName, innerLink) =>
      val innerLinkElaborated = expandLink(path + innerLinkName, innerLink.asInstanceOf[wir.LinkLibrary])
      link.elaborate(innerLinkName, innerLinkElaborated)
    }

    def setConnectedLink(portPath: DesignPath, port: PortLike): Unit = (port: @unchecked) match {
      case _: wir.Port | _: wir.Bundle =>
        elaboratePending.setValue(ElaborateRecord.ConnectedLink(portPath), None)
        connectedLink.put(portPath, path)
      case port: wir.PortArray =>
        port.getElaboratedPorts.foreach { case (subPortName, subPort) =>
          setConnectedLink(portPath + subPortName, subPort)
        }
    }
    for ((portName, port) <- link.getElaboratedPorts) {
      setConnectedLink(path + portName, port)
    }
    require(link.getUnelaboratedPorts.isEmpty)  // make sure we set ConnectedLink on all ports

    // Aggregate by inner link ports
    val linkAllocateConstraints = mutable.HashMap[Seq[String], mutable.ListBuffer[String]]()  // port array path -> constraint names
    val linkArrayDependencies = mutable.HashMap[Seq[String], mutable.ListBuffer[Seq[String]]]()  // port array path -> port arrays that must be expanded
    val linkConnectedConstraint = SingleWriteHashMap[Seq[String], String]()  // port path -> constraint name

    link.getConstraints.foreach { case (constrName, constr) => constr.expr match {
      case expr.ValueExpr.Expr.Exported(exported) => (exported.getExteriorPort, exported.getInternalBlockPort) match {
        case (_, ValueExpr.RefAllocate(intPortArray, _)) =>
          linkAllocateConstraints.getOrElseUpdate(intPortArray, mutable.ListBuffer()).append(constrName)
        case (_, ValueExpr.Ref(intPort)) =>
          linkConnectedConstraint.put(intPort, constrName)
        case (ValueExpr.MapExtract(ValueExpr.Ref(extPortArray), Ref(_)), ValueExpr.RefAllocate(intPortArray, None)) => // TODO array-export stmt
          linkAllocateConstraints.getOrElseUpdate(intPortArray, mutable.ListBuffer()).append(constrName)
          linkArrayDependencies.getOrElseUpdate(intPortArray, mutable.ListBuffer()).append(extPortArray)

        case _ => throw new AssertionError("impossible exported format")
      }
      case _ => // all other constraints ignored
    } }

    link.getElaboratedLinks.foreach { case (innerLinkName, innerLink) =>
      innerLink.asInstanceOf[wir.Link].getMixedPorts.foreach { case (portName, port) =>
        val portPostfix = Seq(innerLinkName, portName)
        port match {
          case _: wir.PortArray => // array case: ignored, handled in lowering
            val constrNames = linkAllocateConstraints.getOrElse(portPostfix, Seq()).toSeq
            val lowerArrayTask = ElaborateRecord.LowerArrayAllocateConnections(path, portPostfix, constrNames, true)
            val arrayDependencies = linkArrayDependencies.getOrElse(portPostfix, Seq()).toSeq.map { portArray =>
              ElaborateRecord.ElaboratePortArray(path ++ portArray)
            }
            elaboratePending.addNode(lowerArrayTask, arrayDependencies)
          case _ =>  // everything else generated
            val constraintOption = linkConnectedConstraint.get(portPostfix).map { constrName =>
              (constrName, link.getConstraints(constrName))
            }
            resolvePortConnectivity(path, portPostfix, constraintOption)
        }
      }
    }

    // Process constraints, as in the block case
    link.getConstraints.foreach { case (constrName, constr) =>
      processParamConstraint(path, constrName, constr, constr)
      processConnectedConstraint(path, constrName, constr, true)
    }
  }

  def elaboratePortArray(path: DesignPath): Unit = {
    val port = resolvePort(path).asInstanceOf[wir.PortArray]
    if (!port.portsSet) {
      val childPortNames = ArrayValue.ExtractText(constProp.getValue(path.asIndirect + IndirectStep.Elements).get)
      val childPortLibraries = SeqMap.from(childPortNames map { childPortName =>
        childPortName -> wir.PortLibrary.apply(port.getType)
      })
      port.setPorts(childPortLibraries)
    }
    constProp.setValue(path.asIndirect + IndirectStep.Length, IntValue(port.getUnelaboratedPorts.size))
    for ((childPortName, childPort) <- port.getUnelaboratedPorts) {
      elaboratePort(path + childPortName, port, childPort)
    }
  }

  // Given a leaf connect constraint (connect or export) that contains an allocate to the specified portPath (on either
  // the link, exported, or block ref), returns the same constraint with the allocate with a fixed step named by the
  // input function (which is provided the option suggested name).
  // Raises an exception if this is not a leaf connect, or if there is not exactly one connected ref that matches
  // the specified portPath.
  protected def mapLeafConnectAllocate(constr: expr.ValueExpr, portPath: Seq[String])(fn: Option[String] => String):
      expr.ValueExpr = {
    import edg.ExprBuilder.{Ref, ValueExpr}
    val ExpectedPortPath = portPath
    constr.expr match {
      case expr.ValueExpr.Expr.Connected(connected) => (connected.getBlockPort, connected.getLinkPort) match {
        case (ValueExpr.RefAllocate(ExpectedPortPath, _), ValueExpr.RefAllocate(ExpectedPortPath, _)) =>
          throw new AssertionError("both block and link ref matches port")
        case (ValueExpr.RefAllocate(ExpectedPortPath, suggestedName), _) =>
          val newStep = ref.LocalStep(step=ref.LocalStep.Step.Name(fn(suggestedName)))
          constr.update(_.connected.blockPort.ref.steps.last := newStep)
        case (_, ValueExpr.RefAllocate(ExpectedPortPath, suggestedName)) =>
          val newStep = ref.LocalStep(step=ref.LocalStep.Step.Name(fn(suggestedName)))
          constr.update(_.connected.linkPort.ref.steps.last := newStep)
        case _ =>
          throw new AssertionError("neither block nor link ref matches port")
      }
      case expr.ValueExpr.Expr.Exported(exported) => (exported.getExteriorPort, exported.getInternalBlockPort) match {
        case (ValueExpr.RefAllocate(ExpectedPortPath, _), ValueExpr.RefAllocate(ExpectedPortPath, _)) =>
          throw new AssertionError("both external and internal ref matches port")
        case (ValueExpr.RefAllocate(ExpectedPortPath, suggestedName), _) =>
          val newStep = ref.LocalStep(step=ref.LocalStep.Step.Name(fn(suggestedName)))
          constr.update(_.exported.exteriorPort.ref.steps.last := newStep)
        case (_, ValueExpr.RefAllocate(ExpectedPortPath, suggestedName)) =>
          val newStep = ref.LocalStep(step=ref.LocalStep.Step.Name(fn(suggestedName)))
          constr.update(_.exported.internalBlockPort.ref.steps.last := newStep)
        case _ =>
          throw new AssertionError("neither external nor internal ref matches port")
      }
      case _ => throw new AssertionError("not a connected or exported constraint")
    }
  }

  // Once all array-connects have defined lengths, this lowers the array-connect statements by replacing them
  // with single leaf-level connections. This also defines ALLOCATED for the relevant port and creates the task
  // to lower the ALLOCATE connections to concrete indices once the port is known.
  protected def lowerArrayAllocateConnections(record: ElaborateRecord.LowerArrayAllocateConnections): Unit = {
    val parentBlock = resolve(record.parent).asInstanceOf[wir.HasMutableConstraints]  // can be block or link

    // Lower array-allocate constraints
    // TODO support more array-type constraints
    import edg.ExprBuilder.{Ref, ValueExpr}
    val newConstrNames = record.constraintNames.flatMap { constrName => parentBlock.getConstraints(constrName).expr match {
      case expr.ValueExpr.Expr.Exported(exported) => (exported.getExteriorPort, exported.getInternalBlockPort) match {
        case (ValueExpr.MapExtract(ValueExpr.Ref(extPortArray), Ref(extPortInner)), ValueExpr.RefAllocate(intPortArray, None)) =>
          val extPortArrayElts = ArrayValue.ExtractText(
            constProp.getValue(record.parent.asIndirect ++ extPortArray + IndirectStep.Elements).get)
          parentBlock.mapMultiConstraint(constrName) { constr =>
            extPortArrayElts.map { index =>
              val extPortPostfix = (extPortArray :+ index) ++ extPortInner
              s"$constrName.$index" -> constr.update(
                _.exported.exteriorPort.ref := Ref(extPortPostfix: _*)
              )
            }
          }
          extPortArrayElts.map { index => s"$constrName.$index" }
        case _ => Seq(constrName)  // ignored
      }
      case _ => Seq(constrName)  // ignored
    } }

    // Given leaf level constraints, create allocations
    var prevPortIndex: Int = -1
    val allocatedIndices = mutable.SeqMap[String, String]()  // constraint name -> allocated name
    newConstrNames foreach { constrName =>
      mapLeafConnectAllocate(parentBlock.getConstraints(constrName), record.portPath) {
        case Some(suggestedName) =>
          allocatedIndices.put(constrName, suggestedName)
          ""  // don't need the map functionality, the result is discarded anyways
        case None =>
          prevPortIndex += 1
          allocatedIndices.put(constrName, prevPortIndex.toString)
          ""  // don't need the map functionality, the result is discarded anyways
      }
    }
    constProp.setValue(record.parent.asIndirect ++ record.portPath + IndirectStep.Allocated,
      ArrayValue(allocatedIndices.values.toSeq.map(TextValue(_))))

    val lowerAllocateTask = ElaborateRecord.LowerAllocateConnections(record.parent, record.portPath,
      newConstrNames, record.portIsLink)
    elaboratePending.addNode(lowerAllocateTask, Seq(
      ElaborateRecord.ElaboratePortArray(record.parent ++ record.portPath)
    ))
  }

  // Once a block-side port array has all its element widths available, this lowers the connect statements
  // by replacing ALLOCATEs with concrete indices.
  // This must also handle internal-side export statements.
  protected def lowerAllocateConnections(record: ElaborateRecord.LowerAllocateConnections): Unit = {
    val parentBlock = resolve(record.parent).asInstanceOf[wir.HasMutableConstraints]  // can be block or link
    val portElements = ArrayValue.ExtractText(
      constProp.getValue(record.parent.asIndirect ++ record.portPath + IndirectStep.Elements).get)

    val suggestedNames = mutable.Set[String]()

    record.constraintNames foreach { constrName =>
      mapLeafConnectAllocate(parentBlock.getConstraints(constrName), record.portPath) {
        case Some(suggestedName) =>
          suggestedNames.add(suggestedName)
          ""  // don't need the map functionality, the result is discarded anyways
        case None =>
          ""  // don't need the map functionality, the result is discarded anyways
      }
    }

    val allocatableNames = portElements.filter(!suggestedNames.contains(_)).to(mutable.ListBuffer)
    val allocatedIndexToConstraint = SingleWriteHashMap[String, String]()

    record.constraintNames foreach { constrName =>
      parentBlock.mapConstraint(constrName) { constr =>
        mapLeafConnectAllocate(constr, record.portPath) { suggestedName =>
          val allocatedName = suggestedName match {
            case Some(suggestedName) => suggestedName  // will later check as a bad ref if this doesn't exist
            case None => allocatableNames.remove(0)
          }
          allocatedIndexToConstraint.put(allocatedName, constrName)
          allocatedName
        }
      }
    }

    val portArray = resolve(record.parent ++ record.portPath).asInstanceOf[wir.PortArray]
    portArray.getMixedPorts.foreach { case (index, innerPort) =>
      val constraintOption = allocatedIndexToConstraint.get(index).map { constrName =>
        (constrName, parentBlock.getConstraints(constrName))
      }
      resolvePortConnectivity(record.parent, record.portPath :+ index, constraintOption)
    }

    record.constraintNames foreach { constrName =>
      // note no guarantee these are fully lowered, since the other side may have un-lowered allocates
      processConnectedConstraint(record.parent, constrName, parentBlock.getConstraints(constrName), record.portIsLink)
    }
  }

  /** Performs full compilation and returns the resulting design. Might take a while.
    */
  def compile(): schema.Design = {
    import edg.ElemBuilder

    while (elaboratePending.getReady.nonEmpty) {
      elaboratePending.getReady.foreach { elaborateRecord =>
        onElaborate(elaborateRecord)
        elaborateRecord match {
          case elaborateRecord@ElaborateRecord.Block(blockPath) =>
            debug(s"Elaborate block @ $blockPath")
            elaborateBlock(blockPath)
            elaboratePending.setValue(elaborateRecord, None)
          case elaborateRecord@ElaborateRecord.Link(linkPath) =>
            debug(s"Elaborate link @ $linkPath")
            elaborateLink(linkPath)
            elaboratePending.setValue(elaborateRecord, None)
          case connect: ElaborateRecord.Connect =>
            debug(s"Elaborate connect $connect")
            elaborateConnect(connect)
            elaboratePending.setValue(elaborateRecord, None)

          case elaborateRecord: ElaborateRecord.ElaboratePortArray =>
            elaboratePortArray(elaborateRecord.path)
            elaboratePending.setValue(elaborateRecord, None)
          case elaborateRecord: ElaborateRecord.LowerArrayAllocateConnections =>
            lowerArrayAllocateConnections(elaborateRecord)
            elaboratePending.setValue(elaborateRecord, None)
          case elaborateRecord: ElaborateRecord.LowerAllocateConnections =>
            lowerAllocateConnections(elaborateRecord)
            elaboratePending.setValue(elaborateRecord, None)

          case _: ElaborateRecord.ElaborateDependency =>
            throw new IllegalArgumentException(s"can't elaborate dependency-only record $elaborateRecord")
        }
      }
    }

    ElemBuilder.Design(root.toPb)
  }

  def evaluateExpr(root: DesignPath, value: expr.ValueExpr): ExprResult = {
    new ExprEvaluatePartial(constProp, root).map(value)
  }

  def getParamValue(param: IndirectDesignPath): Option[ExprValue] = constProp.getValue(param)
  def getAllSolved: Map[IndirectDesignPath, ExprValue] = constProp.getAllSolved
  def getConnectedLink(port: DesignPath): Option[DesignPath] = connectedLink.get(port)
}
