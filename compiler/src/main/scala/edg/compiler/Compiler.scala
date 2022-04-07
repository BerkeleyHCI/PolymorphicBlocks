package edg.compiler

import scala.collection.{SeqMap, mutable}
import edgir.schema.schema
import edgir.expr.expr
import edgir.ref.ref
import edg.wir.{ConnectedConstraintManager, DesignPath, HasMutableConstraints, IndirectDesignPath, IndirectStep, PathSuffix, PortConnections, PortLike, Refinements}
import edg.{EdgirUtils, wir}
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
  // Created but never run for abstract blocks with abstract port array.
  case class ElaboratePortArray(path: DesignPath) extends ElaborateTask

  // Defines the ALLOCATED param of the port array (giving an arbitrary name to anonymous ALLOCATEs) and creates
  // the task to lower the ALLOCATE steps (which gives a final name once the port array's elements are defined).
  // For array-export operations, the incoming ALLOCATED ports must be resolved.
  case class SetPortArrayAllocated(parent: DesignPath, portPath: Seq[String], constraintNames: Seq[String],
                                   arrayConstraintNames: Seq[String], portIsLink: Boolean) extends ElaborateTask

  // Lowers array-allocate connections to individual leaf-level allocate connections, once all array connections to
  // a port array are of known length.
  case class LowerArrayConnections(parent: DesignPath, constraintName: String) extends ElaborateTask
      with ElaborateDependency

  // Lowers leaf-level allocate connections by replacing the ALLOCATE with a port name.
  // Requires array-allocate connections have been already lowered to leaf-level allocate connections, and that
  // the port's ELEMENTS have been defined.
  case class LowerAllocateConnections(parent: DesignPath, portPath: Seq[String], constraintNames: Seq[String],
                                      arrayConstraintNames: Seq[String], portIsLink: Boolean) extends ElaborateTask

  case class ParamValue(paramPath: IndirectDesignPath) extends ElaborateDependency  // when solved

  // Set when the connection from the link's port to portPath have been elaborated, or for link ports
  // when the link has been elaborated.
  // When this is completed, connectedLink for the port and linkParams for the link will be set.
  // Never set for port arrays.
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
  case class GeneratorError(path: DesignPath, target: ref.LibraryPath, err: String) extends CompilerError {
    override def toString: String = s"Generator error ${target.toSimpleString} @ $path: $err"
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
  private val expandedArrayConnectConstraints = SingleWriteHashMap[DesignPath, Seq[String]]()  // constraint path -> new constraint names

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
        case _: wir.Link =>  // links set these on all ports, so this is ignored here. TODO: unify code paths?
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
        expr.ValueExpr.Expr.IfThenElse(_) =>  // raw ValueExprs interpreted as assertions
      assertions += ((blockPath, constrName, constr, SourceLocator.empty))  // TODO add source locators
      true
    case expr.ValueExpr.Expr.Ref(target)  // IsConnected also treated as assertion
      if target.steps.last.step.isReservedParam
          && target.steps.last.getReservedParam == ref.Reserved.IS_CONNECTED =>
      assertions += ((blockPath, constrName, constr, SourceLocator.empty))  // TODO add source locators
      true
    case _ => false
  }

  // Attempts to process a connected constraint, returning true if it is a matching constraint
  def processConnectedConstraint(blockPath: DesignPath, constrName: String, constr: expr.ValueExpr,
                                 isInLink: Boolean): Boolean = {
    import edg.ExprBuilder.ValueExpr
    constr.expr match {
      case expr.ValueExpr.Expr.Connected(connected) => (connected.getBlockPort, connected.getLinkPort) match {
        case (ValueExpr.Ref(blockPort), ValueExpr.Ref(linkPort)) =>
          require(!isInLink)
          elaboratePending.addNode(
            ElaborateRecord.Connect(blockPath ++ linkPort, blockPath ++ blockPort),
            Seq(ElaborateRecord.ConnectedLink(blockPath ++ linkPort))
          )
          true
        case _ => false  // anything with allocates is not processed
      }
      case expr.ValueExpr.Expr.Exported(exported) => (exported.getExteriorPort, exported.getInternalBlockPort) match {
        case (ValueExpr.Ref(extPort), ValueExpr.Ref(intPort)) =>
          if (!isInLink) {
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

    val newBlock = if (blockPb.generator.isEmpty) {
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
    val reqPortValues = generator.getDependenciesPorts.flatMap { reqPort =>  // TODO remove when refactored out
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
    library.runGenerator(generator.getBlockClass, (reqParamValues ++ reqPortValues).toMap) match {
      case Errorable.Success(generatedPb) =>
        val generatedPorts = generator.applyGenerated(generatedPb)
        generatedPorts.foreach { portName =>
          val portArray = generator.getUnelaboratedPorts(portName).asInstanceOf[wir.PortArray]
          constProp.setValue(path.asIndirect + portName + IndirectStep.Elements,
            ArrayValue(portArray.getUnelaboratedPorts.keys.toSeq.map(TextValue(_))))
          // the rest was already handled when elaboratePorts on the generator stub
        }
      case Errorable.Error(err) =>
        errors += CompilerError.GeneratorError(path, generator.getBlockClass, err)
    }
  }

  /** Elaborate a block, mainly processing its internal blocks, links, and connected and parameter constraints.
    * The block should already have had its interface (ports and parameters) expanded.
    */
  protected def elaborateBlock(path: DesignPath): Unit = {
    val block = resolveBlock(path).asInstanceOf[wir.Block]

    block match {
      case block: wir.Generator => runGenerator(path, block)
      case _ =>  // ignored
    }

    // Queue up sub-trees that need elaboration - needs to be post-generate for generators
    block.getUnelaboratedBlocks.foreach { case (innerBlockName, innerBlock) =>
      val innerBlockElaborated = expandBlock(path + innerBlockName, innerBlock.asInstanceOf[wir.BlockLibrary])
      block.elaborate(innerBlockName, innerBlockElaborated)
    }

    block.getUnelaboratedLinks.foreach {
      case (innerLinkName, innerLink: wir.LinkLibrary) =>
        block.elaborate(innerLinkName, expandLink(path + innerLinkName, innerLink))
      case (_, innerLink: wir.LinkArray) => // ignored - expanded in place
      case _ => throw new NotImplementedError()
    }

    val connectedConstraints = new ConnectedConstraintManager(block)
    // Set IsConnected and generate constraint expansion records
    import edg.ExprBuilder.ValueExpr
    block.getElaboratedBlocks.foreach { case (innerBlockName, innerBlock) =>
      innerBlock.asInstanceOf[wir.Block].getMixedPorts.foreach { case (portName, port) =>
        val portPostfix = Seq(innerBlockName, portName)
        port match {
          case _: wir.PortArray =>  // array case: connectivity delayed to lowering
            connectedConstraints.connectionsByBlockPort(portPostfix) match {
              case PortConnections.ArrayConnect(constrName, constr) => constr.expr match {
                case expr.ValueExpr.Expr.ConnectedArray(connected) =>
                  // TODO add dependency to link - this case has no precedent yet
                  throw new NotImplementedError()
                case expr.ValueExpr.Expr.ExportedArray(exported) =>
                  val ValueExpr.Ref(extPostfix) = exported.getExteriorPort
                  val ValueExpr.Ref(intPostfix) = exported.getInternalBlockPort
                  constProp.addDirectedEquality(path.asIndirect ++ extPostfix + IndirectStep.Elements,
                    path.asIndirect ++ intPostfix + IndirectStep.Elements,
                    path, constrName)
                  elaboratePending.addNode(
                    ElaborateRecord.LowerArrayConnections(path, constrName),
                    Seq(
                      ElaborateRecord.ParamValue(path.asIndirect ++ intPostfix + IndirectStep.Elements),
                      // allocated must run first, it depends on constraints not being lowered
                      ElaborateRecord.ParamValue(path.asIndirect ++ intPostfix + IndirectStep.Allocated)
                  ))
                  elaboratePending.addNode(
                    ElaborateRecord.SetPortArrayAllocated(path, portPostfix, Seq(), Seq(constrName), false),
                    Seq(ElaborateRecord.ParamValue(path.asIndirect ++ extPostfix + IndirectStep.Allocated))
                  )
                case _ => throw new IllegalArgumentException(s"invalid array connect to array $constr")
              }
              case PortConnections.AllocatedConnect(singleConnects, arrayConnects) =>
              require(arrayConnects.isEmpty)
                elaboratePending.addNode(
                  ElaborateRecord.SetPortArrayAllocated(path, portPostfix, singleConnects.map(_._2), Seq(), false),
                  Seq()
                )

              case PortConnections.NotConnected =>
              case connects => throw new IllegalArgumentException(s"invalid connections to array $connects")
            }

          case _ =>  // leaf only, no array support
            connectedConstraints.connectionsByBlockPort(portPostfix) match {
              case PortConnections.SingleConnect(constrName, constr) =>
                resolvePortConnectivity(path, portPostfix, Some(constrName, constr))
              case PortConnections.NotConnected =>
                resolvePortConnectivity(path, portPostfix, None)
              case connects => throw new IllegalArgumentException(s"invalid connections to element $connects")
            }
        }
      }
    }

    block.getElaboratedLinks.foreach { case (innerLinkName, innerLink) =>
      innerLink.asInstanceOf[wir.Link].getMixedPorts.foreach { case (portName, port) =>
        val portPostfix = Seq(innerLinkName, portName)
        port match {
          case _: wir.PortArray =>  // array case: connectivity delayed to lowering
            connectedConstraints.connectionsByLinkPort(portPostfix, false) match {
              case PortConnections.ArrayConnect(constrName, constr) =>
                throw new NotImplementedError()
              case PortConnections.AllocatedConnect(singleConnects, arrayConnects) =>
                require(arrayConnects.isEmpty)
                elaboratePending.addNode(
                  ElaborateRecord.SetPortArrayAllocated(path, portPostfix, singleConnects.map(_._2), Seq(), false),
                  Seq()
                )
              case PortConnections.NotConnected =>
                elaboratePending.addNode(
                  ElaborateRecord.SetPortArrayAllocated(path, portPostfix, Seq(), Seq(), false),
                  Seq()
                )
              case connects => throw new IllegalArgumentException(s"invalid connections to element $connects")
            }

          case _ =>
            connectedConstraints.connectionsByLinkPort(portPostfix, false) match {
              case PortConnections.SingleConnect(constrName, constr) =>
                resolvePortConnectivity(path, portPostfix, Some(constrName, constr))
              case PortConnections.NotConnected =>
                resolvePortConnectivity(path, portPostfix, None)
              case connects => throw new IllegalArgumentException(s"invalid connections to element $connects")
            }
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
    val connectedConstraints = new ConnectedConstraintManager(link)

    link.getElaboratedLinks.foreach { case (innerLinkName, innerLink) =>
      innerLink.asInstanceOf[wir.Link].getMixedPorts.foreach { case (portName, port) =>
        val portPostfix = Seq(innerLinkName, portName)
        port match {
          case _: wir.PortArray => // array case: ignored, handled in lowering
            connectedConstraints.connectionsByLinkPort(portPostfix, true) match {
              case PortConnections.AllocatedConnect(singleConnects, arrayConnects) =>
                val deps = arrayConnects.map { case (allocated, constrName, constr) =>
                  val extPostfix = constr.getExportedArray.getExteriorPort match {
                    case ValueExpr.MapExtract(ValueExpr.Ref(extPostfix), Ref(_)) => extPostfix
                    case extPort => throw new IllegalArgumentException(s"unknown exported exterior $extPort")
                  }
                  ElaborateRecord.ParamValue(path.asIndirect ++ extPostfix + IndirectStep.Allocated)
                }
                arrayConnects.foreach { case (allocated, constrName, constr) =>
                  val extPostfix = constr.getExportedArray.getExteriorPort match {
                    case ValueExpr.MapExtract(ValueExpr.Ref(extPostfix), Ref(_)) => extPostfix
                    case extPort => throw new IllegalArgumentException(s"unknown exported exterior $extPort")
                  }
                  val ValueExpr.RefAllocate(intPostfix, _) = constr.getExportedArray.getInternalBlockPort
                  elaboratePending.addNode(ElaborateRecord.LowerArrayConnections(path, constrName), Seq(
                    ElaborateRecord.ParamValue(path.asIndirect ++ extPostfix + IndirectStep.Elements),
                    // allocated must run first, it depends on constraints not being lowered
                    ElaborateRecord.ParamValue(path.asIndirect ++ intPostfix + IndirectStep.Allocated)
                  ))
                }
                elaboratePending.addNode(
                  ElaborateRecord.SetPortArrayAllocated(path, portPostfix, singleConnects.map(_._2), arrayConnects.map(_._2), true),
                  deps
                )
              case PortConnections.NotConnected =>
                elaboratePending.addNode(
                  ElaborateRecord.SetPortArrayAllocated(path, portPostfix, Seq(), Seq(), false),
                  Seq()
                )
              case connects => throw new IllegalArgumentException(s"invalid connections to element $connects")
            }
          case _ =>  // everything else generated
            connectedConstraints.connectionsByLinkPort(portPostfix, true) match {
              case PortConnections.SingleConnect(constrName, constr) =>
                resolvePortConnectivity(path, portPostfix, Some(constrName, constr))
              case PortConnections.NotConnected =>
                resolvePortConnectivity(path, portPostfix, None)
              case connects => throw new IllegalArgumentException(s"invalid connections to element $connects")
            }
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
    import edg.ExprBuilder.ValueExpr
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
  protected def lowerArrayConnections(record: ElaborateRecord.LowerArrayConnections): Unit = {
    val parentBlock = resolve(record.parent).asInstanceOf[wir.HasMutableConstraints]  // can be block or link

    // Lower array-allocate constraints
    import edg.ExprBuilder.{Ref, ValueExpr}
    import edg.ElemBuilder
    val newConstrNames = parentBlock.getConstraints(record.constraintName).expr match {
      case expr.ValueExpr.Expr.ExportedArray(exported) => (exported.getExteriorPort, exported.getInternalBlockPort) match {
        case (ValueExpr.Ref(extPortArray), ValueExpr.Ref(intPortArray)) =>
          val intPortArrayElts = ArrayValue.ExtractText(
            constProp.getValue(record.parent.asIndirect ++ intPortArray + IndirectStep.Elements).get)
          parentBlock.mapMultiConstraint(record.constraintName) { constr =>
            intPortArrayElts.map { index =>
              s"${record.constraintName}.$index" -> ElemBuilder.Constraint.Exported(
                Ref((extPortArray :+ index): _*), Ref.Allocate(Ref(intPortArray: _*), Some(index)))
            }
          }
          intPortArrayElts.map { index => s"${record.constraintName}.$index" }

        case (ValueExpr.MapExtract(ValueExpr.Ref(extPortArray), Ref(extPortInner)), ValueExpr.RefAllocate(intPortArray, None)) =>
          val extPortArrayElts = ArrayValue.ExtractText(
            constProp.getValue(record.parent.asIndirect ++ extPortArray + IndirectStep.Elements).get)
          parentBlock.mapMultiConstraint(record.constraintName) { constr =>
            extPortArrayElts.map { index =>
              val extPortPostfix = (extPortArray :+ index) ++ extPortInner
              s"${record.constraintName}.$index" -> ElemBuilder.Constraint.Exported(
                Ref(extPortPostfix: _*), Ref.Allocate(Ref(intPortArray: _*), None))
            }
          }
          extPortArrayElts.map { index => s"${record.constraintName}.$index" }

        case _ => throw new IllegalArgumentException("unsupported array export")
      }
      case _ => throw new IllegalArgumentException("not a connected-array or exported-array constraint")
    }

    expandedArrayConnectConstraints.put(record.parent + record.constraintName, newConstrNames)
    newConstrNames foreach { constrName =>
      // note no guarantee these are fully lowered, since the other side may have un-lowered allocates
      processConnectedConstraint(record.parent, constrName, parentBlock.getConstraints(constrName),
        parentBlock.isInstanceOf[wir.Link])
    }
  }

  // Sets the ALLOCATED on a port array, once all connections are of known length.
  // Array-connects must not have been lowered.
  protected def setPortArrayAllocated(record: ElaborateRecord.SetPortArrayAllocated): Unit = {
    val parentBlock = resolve(record.parent).asInstanceOf[wir.HasMutableConstraints]  // can be block or link

    // Given leaf level constraints, create allocations
    var prevPortIndex: Int = -1
    val allocatedIndices = mutable.SeqMap[String, String]()  // constraint name -> allocated name
    record.constraintNames foreach { constrName =>
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
    import edg.ExprBuilder.{Ref, ValueExpr}
    record.arrayConstraintNames foreach { constrName => parentBlock.getConstraints(constrName).expr match {
      case expr.ValueExpr.Expr.ExportedArray(exported) => (exported.getExteriorPort, exported.getInternalBlockPort) match {
        case (ValueExpr.Ref(extPortArray), ValueExpr.Ref(intPortArray)) =>
          require(record.constraintNames.isEmpty && record.arrayConstraintNames.length == 1)  // non-allocating export only allowed once
          val extPortArrayElts = ArrayValue.ExtractText(
            constProp.getValue(record.parent.asIndirect ++ extPortArray + IndirectStep.Allocated).get)
          extPortArrayElts.foreach { i =>
            allocatedIndices.put(s"$constrName.$i", i)
          }
        case (ValueExpr.MapExtract(ValueExpr.Ref(extPortArray), Ref(_)), ValueExpr.RefAllocate(intPortArray, None)) =>
          val extPortArrayLength = ArrayValue.ExtractText(
            constProp.getValue(record.parent.asIndirect ++ extPortArray + IndirectStep.Allocated).get).length
          // note since suggestedName is empty we just allocate names arbitrarily
          (0 until extPortArrayLength).foreach { i =>
            prevPortIndex += 1
            allocatedIndices.put(s"$constrName.$i", prevPortIndex.toString)
          }
        case _ => throw new AssertionError("impossible exported-array format")
      }
      case _ => throw new AssertionError("unexpected array connection constraint")
    } }
    constProp.setValue(record.parent.asIndirect ++ record.portPath + IndirectStep.Allocated,
      ArrayValue(allocatedIndices.values.toSeq.map(TextValue(_))))

    val lowerAllocateTask = ElaborateRecord.LowerAllocateConnections(record.parent, record.portPath,
      record.constraintNames, record.arrayConstraintNames, record.portIsLink)
    val lowerArrayDependencies = record.arrayConstraintNames.map { constrName =>
      ElaborateRecord.LowerArrayConnections(record.parent, constrName)
    }
    elaboratePending.addNode(lowerAllocateTask, Seq(
      ElaborateRecord.ElaboratePortArray(record.parent ++ record.portPath),
    ) ++ lowerArrayDependencies)
  }

  // Once a block-side port array has all its element widths available, this lowers the connect statements
  // by replacing ALLOCATEs with concrete indices.
  // This must also handle internal-side export statements.
  protected def lowerAllocateConnections(record: ElaborateRecord.LowerAllocateConnections): Unit = {
    val parentBlock = resolve(record.parent).asInstanceOf[wir.HasMutableConstraints]  // can be block or link
    val portElements = ArrayValue.ExtractText(
      constProp.getValue(record.parent.asIndirect ++ record.portPath + IndirectStep.Elements).get)

    val suggestedNames = mutable.Set[String]()

    // Update constraint names given expanded array constraints
    val combinedConstrNames = record.constraintNames ++
        record.arrayConstraintNames.flatMap(constrName => expandedArrayConnectConstraints(record.parent + constrName))

    combinedConstrNames foreach { constrName =>
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

    combinedConstrNames foreach { constrName =>
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

    combinedConstrNames foreach { constrName =>
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
          case elaborateRecord: ElaborateRecord.LowerArrayConnections =>
            lowerArrayConnections(elaborateRecord)
            elaboratePending.setValue(elaborateRecord, None)
          case elaborateRecord: ElaborateRecord.SetPortArrayAllocated =>
            setPortArrayAllocated(elaborateRecord)
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
