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

  case class BlockElaborated(blockPath: DesignPath) extends ElaborateDependency  // accounts for generators

  // Connection to be elaborated, to set port parameter, IS_CONNECTED, and CONNECTED_LINK equivalences.
  // Only elaborates the direct connect, and for bundles, creates sub-Connect tasks since it needs
  // connectedLink and linkParams.
  case class Connect(toLinkPortPath: DesignPath, toBlockPortPath: DesignPath)
      extends ElaborateTask

  case class Generator(blockPath: DesignPath, blockClass: LibraryPath, fnName: String,
                       unrefinedClass: Option[LibraryPath],
                       requiredParams: Seq[ref.LocalPath], requiredPorts: Seq[ref.LocalPath]
                      ) extends ElaborateTask {
    override def toString: String = s"Generator(${blockClass.toSimpleString}.$fnName @ $blockPath)"
  }

  // When port arrays have been lowered and the block elaborated (so ports are available), mark unconnected
  // ports are not-connected and set IsConnected.
  // NOTE: generator IsConnected dependencies are handled separately, since they must be available pre-elaborate.
  case class BlockPortNotConnected(path: DesignPath) extends ElaborateTask

  // In connect and export constraints, replaces all (internal) block-side ALLOCATEs with concrete subelt names.
  // When a connect is fully resolved (no more ALLOCATEs), generates the Connect elaboration task.
  case class BlockPortArray(parent: DesignPath, portArray: Seq[String], constraintNames: Seq[String])
      extends ElaborateTask with ElaborateDependency
  // In connect constraints, replaces all link-side ALLOCATEs with concrete subelt names.
  // When a connect is fully resolved (no more ALLOCATEs), generates the Connect elaboration task.
  case class LinkPortArray(parent: DesignPath, portArray: Seq[String], constraintNames: Seq[String])
      extends ElaborateTask with ElaborateDependency

  case class ParamValue(paramPath: IndirectDesignPath) extends ElaborateDependency  // when solved

  // Set when the connection from the link's port to portPath have been elaborated, or for link ports
  // when the link has been elaborated.
  // When this is completed, connectedLink for the port and linkParams for the link will be set.
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

  case class AbstractBlock(path: DesignPath, blockType: ref.LibraryPath) extends CompilerError {
    override def toString: String = s"Abstract block: $path (of type ${blockType.toSimpleString})"
  }

  case class FailedAssertion(root: DesignPath, constrName: String,
                             value: expr.ValueExpr, result: ExprValue) extends CompilerError {
    override def toString: String =
      s"Failed assertion: $root.$constrName, ${ExprToString.apply(value)} => $result"
  }
  case class MissingAssertion(root: DesignPath, constrName: String,
                              value: expr.ValueExpr, missing: Set[ExprRef]) extends CompilerError {
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

  // Set true when a connect involving the port is seen, or false when a port is known not-connected
  // Not a recursive data structure
  private val portDirectlyConnected = SingleWriteHashMap[DesignPath, Boolean]()

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

    connectedLink.get(connect.toLinkPortPath) match {
      case Some(linkPath) =>  // Generate the CONNECTED_LINK equalities, if there is a connected link
        connectedLink.put(connect.toBlockPortPath, linkPath)  // propagate CONNECTED_LINK params
        val allParams = linkParams(linkPath) :+ IndirectStep.Name
        for (linkParam <- allParams) {
          constProp.addEquality(
            connect.toBlockPortPath.asIndirect + IndirectStep.ConnectedLink + linkParam,
            linkPath.asIndirect + linkParam,
          )
        }
      case None =>
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
        // arrays have no params (including name), but we need to instantiate the array
        val childPortNames = constProp.getArrayElts(path) match {
          case Some(elts) => elts
          case None =>  // TODO can the empty case be set with everything else?
            constProp.setArrayElts(path, Seq())
            constProp.setValue(path.asIndirect + IndirectStep.Length, IntValue(0))
            Seq()
        }
        val childPortLibraries = SeqMap.from(childPortNames map { childPortName =>
          childPortName -> wir.PortLibrary.apply(port.getType)
        })
        port.setPorts(childPortLibraries)
        for ((childPortName, childPort) <- port.getUnelaboratedPorts) {
          elaboratePort(path + childPortName, port, childPort)
        }
      case port => throw new NotImplementedError(s"unknown instantiated port $port")
    }
  }

  // TODO clean this up... by a lot
  def processParamConstraint: PartialFunction[(DesignPath, String, expr.ValueExpr, expr.ValueExpr.Expr), Unit] = {
    case (path, constrName, constr, expr.ValueExpr.Expr.Assign(assign)) =>
      constProp.addAssignment(
        path.asIndirect ++ assign.dst.get,
        path, assign.src.get,
        constrName) // TODO add sourcelocators
    case (path, constrName, constr,
        expr.ValueExpr.Expr.Binary(_) | expr.ValueExpr.Expr.BinarySet(_) |
        expr.ValueExpr.Expr.Unary(_) | expr.ValueExpr.Expr.UnarySet(_) |
        expr.ValueExpr.Expr.IfThenElse(_)) =>
      assertions += ((path, constrName, constr, SourceLocator.empty))  // TODO add source locators
    case (path, constrName, constr, expr.ValueExpr.Expr.Ref(target))
      if target.steps.last.step.isReservedParam
          && target.steps.last.getReservedParam == ref.Reserved.IS_CONNECTED =>
      assertions += ((path, constrName, constr, SourceLocator.empty))  // TODO add source locators
  }

  def processConnectedConstraint(blockPath: DesignPath, constrName: String, constr: expr.ValueExpr.Expr): Option[Unit] = {
    import edg.ExprBuilder.ValueExpr
    constr match {
      case expr.ValueExpr.Expr.Connected(connected) => (connected.getBlockPort, connected.getLinkPort) match {
        case (ValueExpr.Ref(blockPort), ValueExpr.Ref(linkPort)) =>
          elaboratePending.addNode(
            ElaborateRecord.Connect(blockPath ++ linkPort, blockPath ++ blockPort),
            Seq(ElaborateRecord.ConnectedLink(blockPath ++ linkPort))
          )
          portDirectlyConnected.put(blockPath ++ blockPort, true)
          portDirectlyConnected.put(blockPath ++ linkPort, true)
          constProp.setValue(blockPath.asIndirect ++ blockPort + IndirectStep.IsConnected, BooleanValue(true))
          constProp.setValue(blockPath.asIndirect ++ linkPort + IndirectStep.IsConnected, BooleanValue(true))
          Some(())
        case _ => None  // anything with allocates is not processed
      }
      case expr.ValueExpr.Expr.Exported(exported) => (exported.getExteriorPort, exported.getInternalBlockPort) match {
        case (ValueExpr.Ref(extPort), ValueExpr.Ref(intPort)) =>
          elaboratePending.addNode(
            ElaborateRecord.Connect(blockPath ++ extPort, blockPath ++ intPort),
            Seq(ElaborateRecord.ConnectedLink(blockPath ++ extPort))
          )
          portDirectlyConnected.put(blockPath ++ intPort, true)
          constProp.addEquality(blockPath.asIndirect ++ intPort + IndirectStep.IsConnected,
            blockPath.asIndirect ++ extPort + IndirectStep.IsConnected)
          Some(())
        case _ => None  // anything with allocates is not processed
      }
      case _ => None  // not defined
    }
  }

  protected def processBlock(path: DesignPath, block: wir.Block): Unit = {
    import edg.ExprBuilder.ValueExpr
    constProp.setValue(path.asIndirect + IndirectStep.Name, TextValue(path.toString))

    // Elaborate ports, generating equivalence constraints as needed
    processParamDeclarations(path, block)
    for ((portName, port) <- block.getUnelaboratedPorts) {
      elaboratePort(path + portName, block, port)
    }

    // Find allocate ports and generate the port array lowering compiler tasks
    val blockPortArrayConstraints = mutable.HashMap[Seq[String], mutable.ListBuffer[String]]()  // port array path -> constraint names
    val linkPortArrayConstraints = mutable.HashMap[Seq[String], mutable.ListBuffer[String]]()  // port array path -> constraint names

    // This is used to track generators to know which ports might (for arrays) or are be connected
    val blockTopPortsConnected = mutable.Set[(String, String)]()  // as block, top port, that has a connect to it

    block.getConstraints.foreach { case (constrName, constr) => constr.expr match {
      case expr.ValueExpr.Expr.Connected(connected) =>
        (connected.getBlockPort, connected.getLinkPort) match {
          case (ValueExpr.RefAllocate(blockPortArray), ValueExpr.RefAllocate(linkPortArray)) =>
            blockPortArrayConstraints.getOrElseUpdate(blockPortArray, mutable.ListBuffer()).append(constrName)
            linkPortArrayConstraints.getOrElseUpdate(linkPortArray, mutable.ListBuffer()).append(constrName)
            blockTopPortsConnected.add((blockPortArray(0), blockPortArray(1)))
          case (ValueExpr.RefAllocate(blockPortArray), _) =>
            blockPortArrayConstraints.getOrElseUpdate(blockPortArray, mutable.ListBuffer()).append(constrName)
            blockTopPortsConnected.add((blockPortArray(0), blockPortArray(1)))
          case (ValueExpr.Ref(blockPort), ValueExpr.RefAllocate(linkPortArray)) =>
            linkPortArrayConstraints.getOrElseUpdate(linkPortArray, mutable.ListBuffer()).append(constrName)
            blockTopPortsConnected.add((blockPort(0), blockPort(1)))
          case (ValueExpr.Ref(blockPort), _) =>
            blockTopPortsConnected.add((blockPort(0), blockPort(1)))
        }
      case expr.ValueExpr.Expr.Exported(exported) =>
        (exported.getExteriorPort, exported.getInternalBlockPort) match {
          case (_, ValueExpr.RefAllocate(blockPortArray)) =>
            blockPortArrayConstraints.getOrElseUpdate(blockPortArray, mutable.ListBuffer()).append(constrName)
            blockTopPortsConnected.add((blockPortArray(0), blockPortArray(1)))
          case (_, ValueExpr.Ref(blockPort)) =>
            blockTopPortsConnected.add((blockPort(0), blockPort(1)))
          case _ =>
        }
      case _ =>
    }}

    // Since links can only be elaborated after all arrays defined, build up the list of all array tasks for links
    val linkArrayRecords = mutable.HashMap[String, mutable.ListBuffer[ElaborateRecord]]()
    val blockArrayRecords = mutable.HashMap[String, mutable.ListBuffer[ElaborateRecord]]()
    blockPortArrayConstraints.foreach { case (portArrayPath, constrNames) =>
      val blockArrayTask = ElaborateRecord.BlockPortArray(path, portArrayPath, constrNames.toSeq)
      blockArrayRecords.getOrElseUpdate(portArrayPath.head, mutable.ListBuffer()).append(blockArrayTask)
      elaboratePending.addNode(blockArrayTask, Seq())
    }
    linkPortArrayConstraints.foreach { case (portArrayPath, constrNames) =>
      val linkArrayTask = ElaborateRecord.LinkPortArray(path, portArrayPath, constrNames.toSeq)
      linkArrayRecords.getOrElseUpdate(portArrayPath.head, mutable.ListBuffer()).append(linkArrayTask)
      elaboratePending.addNode(linkArrayTask, Seq())
    }

    // Process all the process-able constraints: parameter constraints and non-allocate connected
    block.getConstraints.foreach { case (constrName, constr) =>
      constr.expr match {
        case expr if processParamConstraint.isDefinedAt(path, constrName, constr, expr) =>
          processParamConstraint(path, constrName, constr, expr)
        case _ =>
      }
      processConnectedConstraint(path, constrName, constr.expr)
    }

    // Queue up sub-trees that need elaboration - needs to be post-generate for generators
    // subtree ports can't know connected state until own connected state known
    for (blockName <- block.getUnelaboratedBlocks.keys) {
      debug(s"Push block to pending: ${path + blockName}")
      elaboratePending.addNode(ElaborateRecord.Block(path + blockName), Seq())
      elaboratePending.addNode(ElaborateRecord.BlockPortNotConnected(path + blockName),
        Seq(ElaborateRecord.BlockElaborated(path + blockName)) ++ blockArrayRecords.getOrElse(blockName, Seq()))
    }
    for (linkName <- block.getUnelaboratedLinks.keys) {
      debug(s"Push link to pending: ${path + linkName}")
      val linkTask = ElaborateRecord.Link(path + linkName)
      elaboratePending.addNode(linkTask,
        linkArrayRecords.getOrElse(linkName, Seq()).toSeq)
      elaboratePending.addNode(ElaborateRecord.BlockPortNotConnected(path + linkName),
        Seq(linkTask) ++ linkArrayRecords.getOrElse(linkName, Seq()))
    }

    // Mark this block as done
    elaboratePending.setValue(ElaborateRecord.BlockElaborated(path), None)
  }

  /** Elaborate the unelaborated block at path (but where the parent has been elaborated and is reachable from root),
    * and adds it to the parent and replaces the lib_elem proto entry with a placeholder unknown.
    * Adds children to the pending queue, and adds constraints to constProp.
    * Expands connects in the parent, as needed.
    */
  protected def elaborateBlock(path: DesignPath): Unit = {
    // Instantiate block from library element to wir.Block
    val libraryPath = resolveBlock(path).asInstanceOf[wir.BlockLibrary].target

    val (refinedLibrary, unrefinedType) = refinements.instanceRefinements.get(path) match {
      case Some(refinement) => (refinement, Some(libraryPath))
      case None => refinements.classRefinements.get(libraryPath) match {
        case Some(refinement) => (refinement, Some(libraryPath))
        case None => (libraryPath, None)
      }
    }

    val blockPb = library.getBlock(refinedLibrary) match {
      case Errorable.Success(blockPb) =>
        if (unrefinedType.isDefined) {  // check refinement validity and add default params
          if (!library.isSubclassOf(refinedLibrary, libraryPath)) {
            errors += CompilerError.RefinementSubclassError(path, refinedLibrary, libraryPath)
          }
          library.getBlock(libraryPath) match {
            case Errorable.Success(unrefinedPb) =>
              val refinedNewParams = blockPb.params.keys.toSet -- unrefinedPb.params.keys
              refinedNewParams.foreach { refinedNewParam =>
                blockPb.paramDefaults.get(refinedNewParam) match {
                  case Some(refinedDefault) =>
                    constProp.addAssignment(path.asIndirect + refinedNewParam, path, refinedDefault,
                        s"(default)${refinedLibrary.toSimpleString}.$refinedNewParam")
                  case None =>  // ignored
                }
              }
            case Errorable.Error(err) =>  // TODO cleaner error handling
              import edgir.elem.elem
              errors += CompilerError.LibraryError(path, libraryPath, err)
              elem.HierarchyBlock()
          }
          blockPb
        } else {  // no default params
          blockPb
        }
      case Errorable.Error(err) =>
        import edgir.elem.elem
        errors += CompilerError.LibraryError(path, refinedLibrary, err)
        elem.HierarchyBlock()
    }

    // Populate class-based value refinements
    refinements.classValues.get(refinedLibrary) match {
      case Some(classValueRefinements) => for ((subpath, value) <- classValueRefinements) {
        constProp.setForcedValue(
          path.asIndirect ++ subpath, value,
          s"${refinedLibrary.getTarget.getName} class refinement")
      }
      case None =>
    }

    if (blockPb.generators.isEmpty) {  // non-generators: directly instantiate the block
      val block = new wir.Block(blockPb, unrefinedType)
      processBlock(path, block)
      if (path.steps.nonEmpty) {
        val (parentPath, name) = path.split
        val parent = resolveBlock(parentPath).asInstanceOf[wir.Block]
        parent.elaborate(name, block)  // link block in parent
      } else {
        root = block
      }
    } else {  // Generators: add to queue without changing the block
      require(blockPb.generators.size == 1)  // TODO proper single generator structure
      val (generatorFnName, generator) = blockPb.generators.head
      elaboratePending.addNode(ElaborateRecord.Generator(path, refinedLibrary, generatorFnName,
          unrefinedType, generator.requiredParams, generator.requiredPorts),
        generator.requiredParams.map { depPath =>
          ElaborateRecord.ParamValue(path.asIndirect ++ depPath)
        } ++ generator.requiredPorts.flatMap { depPort =>
            if (portDirectlyConnected.contains(path ++ depPort)) {
              Some(ElaborateRecord.ConnectedLink(path ++ depPort))
            } else {  // don't block on non-connected ports
              // TODO the disconnected logic is very spread around, this needs to be centralized
              None
            }
        }
      )
    }
  }

  // Elaborates the generator, replacing the block stub with the generated implementation.
  //
  protected def elaborateGenerator(generator: ElaborateRecord.Generator): Unit = {
    // Get required values for the generator
    val reqParamValues = generator.requiredParams.map { reqParam =>
      reqParam -> constProp.getValue(generator.blockPath.asIndirect ++ reqParam).get
    }.toMap

    val reqPortValues = generator.requiredPorts.flatMap { reqPort =>
      val isConnectedSuffix = PathSuffix() ++ reqPort + IndirectStep.IsConnected
      // TODO centralize not-connected logic
      if (portDirectlyConnected.contains(generator.blockPath ++ reqPort)) {
        val connectedNameSuffix = PathSuffix() ++ reqPort + IndirectStep.ConnectedLink + IndirectStep.Name
        Map(
          isConnectedSuffix -> BooleanValue(true),
          connectedNameSuffix -> constProp.getValue(generator.blockPath.asIndirect ++ connectedNameSuffix).get,
        )
      } else {
        Map(isConnectedSuffix -> BooleanValue(false))
      }
    }.map { case (param, value) =>
      param.asLocalPath() -> value
    }

    // Run generator and plug in
    val generatedPb = library.runGenerator(generator.blockClass, generator.fnName,
      reqParamValues ++ reqPortValues
    ) match {
      case Errorable.Success(generatedPb) =>
        if (generatedPb.getSelfClass != generator.blockClass) {
          errors += CompilerError.GeneratorError(generator.blockPath, generator.blockClass, generator.fnName,
            s"Generated class ${generatedPb.getSelfClass.toSimpleString} not equal to " +
                s"generator class ${generator.blockClass.toSimpleString}")
        }
        if (generatedPb.generators.nonEmpty) {
          errors += CompilerError.GeneratorError(generator.blockPath, generator.blockClass, generator.fnName,
            s"Generated ${generatedPb.getSelfClass.toSimpleString} still contains generators")
        }
        generatedPb
      case Errorable.Error(err) =>
        import edgir.elem.elem
        errors += CompilerError.GeneratorError(generator.blockPath, generator.blockClass, generator.fnName, err)
        elem.HierarchyBlock()
    }
    val block = new wir.Block(generatedPb, generator.unrefinedClass)
    processBlock(generator.blockPath, block)

    // Link block in parent
    if (generator.blockPath.steps.nonEmpty) {
      val (parentPath, name) = generator.blockPath.split
      val parent = resolveBlock(parentPath).asInstanceOf[wir.Block]
      parent.elaborate(name, block)
    } else {
      root = block
    }
  }

  protected def processLink(path: DesignPath, link: wir.Link): Unit = {
    import edg.ExprBuilder.{Ref, ValueExpr}

    // Set my parameters in the global data structure
    constProp.setValue(path.asIndirect + IndirectStep.Name, TextValue(path.toString))
    linkParams.put(path, link.getParams.keys.toSeq.map(IndirectStep.Element(_)))

    // Elaborate ports, generating equivalence constraints as needed
    processParamDeclarations(path, link)
    for ((portName, port) <- link.getUnelaboratedPorts) {
      elaboratePort(path + portName, link, port)
    }

    def setConnectedLink(portPath: DesignPath, port: PortLike): Unit = (port: @unchecked) match {
      case _: wir.Port | _: wir.Bundle =>
        if (portDirectlyConnected.contains(portPath)) {
          connectedLink.put(portPath, path)
          elaboratePending.setValue(ElaborateRecord.ConnectedLink(portPath), None)
        }
      case port: wir.PortArray =>
        port.getElaboratedPorts.foreach { case (subPortName, subPort) =>
          setConnectedLink(portPath + subPortName, subPort)
        }
    }
    for ((portName, port) <- link.getElaboratedPorts) {
      setConnectedLink(path + portName, port)
    }

    // Find allocate ports and lower them before processing all constraints
    // path to inner link port array -> list of array elements
    val intPortArrayEltss = mutable.HashMap[Seq[String], mutable.ListBuffer[String]]()
    link.getConstraints.view.mapValues(_.expr).collect {  // extract exported constraints only
      case (constrName, expr.ValueExpr.Expr.Exported(exported)) =>
        (constrName, exported.getExteriorPort, exported.getInternalBlockPort)
    }.collect {  // extract array ones that need lowering, into (name, external ports, internal array)
      case (constrName, ValueExpr.MapExtract(ValueExpr.Ref(extPortArray), Ref(extPortInner)),
      ValueExpr.RefAllocate(intPortArray)) =>  // array-array connect
        val extPorts = constProp.getArrayElts(path ++ extPortArray).get.map { extArrayElt =>
          (extPortArray :+ extArrayElt) ++ extPortInner }
        (constrName, extPorts, intPortArray)
      case (constrName, ValueExpr.Ref(extPort), ValueExpr.RefAllocate(intPortArray)) =>  // element-array connect
        val extPorts = Seq(extPort)
        (constrName, extPorts, intPortArray)
    }.foreach { case (constrName, extPorts, intPortArray) =>  // expand the connections
      link.mapMultiConstraint(constrName) { constr =>
        val intPortArrayElts = intPortArrayEltss.getOrElseUpdate(intPortArray, mutable.ListBuffer())
        val startIndex = intPortArrayElts.length
        extPorts.zipWithIndex.map { case (extPort, extPortIndex) =>
          val intPortIndex = (startIndex + extPortIndex).toString
          intPortArrayElts.append(intPortIndex)

          val newConstrName = extPorts.length match {
            case 1 => constrName // constraint doesn't expand
            case _ => constrName + "." + extPortIndex // expands into multiple constraints, each needs a unique name
          }
          val newConstr = constr.update(
            _.exported.exteriorPort.ref.steps := extPort.map { pathElt =>
              ref.LocalStep(ref.LocalStep.Step.Name(pathElt))
            },
            _.exported.internalBlockPort.ref.steps := (intPortArray :+ intPortIndex).map { pathElt =>
              ref.LocalStep(ref.LocalStep.Step.Name(pathElt))
            },
          )

          newConstrName -> newConstr
        }
      }
    }

    // Actually define arrays
    intPortArrayEltss.foreach { case (intPortArray, intPortArrayElts) =>
      debug(s"Array defined: ${path ++ intPortArray} = $intPortArrayElts")
      constProp.setArrayElts(path ++ intPortArray, intPortArrayElts.toSeq)
      constProp.setValue(path.asIndirect ++ intPortArray + IndirectStep.Length, IntValue(intPortArrayElts.length))
    }

    // Process constraints, as in the block case
    // TODO UNIFY w/ PROCESS CONNECTED CONSTRAINT
    link.getConstraints.foreach { case (constrName, constr) => constr.expr match {
      case expr if processParamConstraint.isDefinedAt(path, constrName, constr, expr) =>
        processParamConstraint(path, constrName, constr, expr)
      case expr.ValueExpr.Expr.Exported(exported) =>
        (exported.getExteriorPort, exported.getInternalBlockPort) match {
          case (ValueExpr.Ref(extPort), ValueExpr.Ref(intPort)) =>
            elaboratePending.addNode(
              ElaborateRecord.Connect(path ++ intPort, path ++ extPort),
              Seq(ElaborateRecord.ConnectedLink(path ++ intPort))
            )
            portDirectlyConnected.put(path ++ intPort, true)
            constProp.addEquality(path.asIndirect ++ intPort + IndirectStep.IsConnected,
              path.asIndirect ++ extPort + IndirectStep.IsConnected)  // TODO can be directed assignment
          case _ => throw new IllegalConstraintException(s"unknown export in link $path: $constrName = $exported")
        }
      case _ => throw new IllegalConstraintException(s"unknown constraint in link $path: $constrName = $constr")
    }}

    // Queue up sub-trees that need elaboration - needs to be post-generate for generators
    for (linkName <- link.getUnelaboratedLinks.keys) {
      debug(s"Push link to pending: ${path + linkName}")
      val linkTask = ElaborateRecord.Link(path + linkName)
      elaboratePending.addNode(linkTask, Seq())
      elaboratePending.addNode(ElaborateRecord.BlockPortNotConnected(path + linkName),
        Seq(linkTask))
    }
  }

  /** Elaborate the unelaborated link at path (but where the parent has been elaborated and is reachable from root),
    * and adds it to the parent and replaces the lib_elem proto entry with a placeholder unknown.
    * Adds children to the pending queue, and adds constraints to constProp.
    * Expands connects in the parent, as needed.
    */
  protected def elaborateLink(path: DesignPath): Unit = {
    val (parentPath, name) = path.split

    // Instantiate block from library element to wir.Block
    val parent = resolve(parentPath).asInstanceOf[wir.HasMutableLinks]
    val libraryPath = parent.getUnelaboratedLinks(name).asInstanceOf[wir.LinkLibrary].target

    val linkPb = library.getLink(libraryPath) match {
      case Errorable.Success(linkPb) => linkPb
      case Errorable.Error(err) =>
        import edgir.elem.elem
        errors += CompilerError.LibraryError(path, libraryPath, err)
        elem.Link()
    }
    val link = new wir.Link(linkPb)

    // Process block
    processLink(path, link)

    // Link block in parent
    parent.elaborate(name, link)
  }

  // Additional processing for ports that sets not-connected status (or connected status) recursively once
  // the connections are known (enclosing block elaborated, array / allocate connects lowered) and
  // ports are known (block elaborated).
  protected def elaborateNotConnected(connected: ElaborateRecord.BlockPortNotConnected): Unit = {
    val blockLike = resolve(connected.path)

    def setPortDisconnected(portPath: DesignPath): Unit = {
      constProp.setValue(portPath.asIndirect + IndirectStep.IsConnected, BooleanValue(false))
      if (blockLike.isInstanceOf[wir.Block]) {
        // only set fake connected-link on block-side disconnected ports, the link side
        connectedLink.put(portPath, DesignPath())
        elaboratePending.setValue(ElaborateRecord.ConnectedLink(portPath), None)
      }
    }

    // For the top port, we take connectedness status (and infer disconnected-ness) from portDirectlyConnected
    def processConnectedTop(portPath: DesignPath, port: PortLike): Unit = (port: @unchecked) match {
      case port: wir.Port =>
        if (!portDirectlyConnected.getOrElseUpdate(portPath, false)) {
          setPortDisconnected(portPath)
        }
      case port: wir.Bundle =>
        if (!portDirectlyConnected.getOrElseUpdate(portPath, false)) {
          setPortDisconnected(portPath)
          port.getElaboratedPorts.foreach { case (subPortName, subPort) =>
            setNotConnectedRecursive(portPath + subPortName, subPort)
          }
        }
      case port: wir.PortArray =>
        portDirectlyConnected.put(portPath, false)  // array itself should never be set, this also prevents overwriting
        port.getElaboratedPorts.foreach { case (subPortName, subPort) =>
          processConnectedTop(portPath + subPortName, subPort)
        }
    }

    // For inner ports, we take connectedness status from the top level
    def setNotConnectedRecursive(portPath: DesignPath, port: PortLike): Unit = (port: @unchecked) match {
      case port: wir.Port =>
        portDirectlyConnected.put(portPath, false)  // result is not used, but prevents overwriting
        setPortDisconnected(portPath)
      case port: wir.Bundle =>
        portDirectlyConnected.put(portPath, false)  // result is not used, but prevents overwriting
        setPortDisconnected(portPath)
        port.getElaboratedPorts.foreach { case (subPortName, subPort) =>
          setNotConnectedRecursive(portPath + subPortName, subPort)
        }
    }

    val ports = (blockLike: @unchecked) match {
      case block: wir.Block => block.getElaboratedPorts
      case link: wir.Link => link.getElaboratedPorts
    }
    ports.foreach { case (portName, port) =>
      processConnectedTop(connected.path + portName, port)
    }
  }

  // Once a block-side port array has all its element widths available, this lowers the connect statements
  // by replacing ALLOCATEs with concrete indices.
  // This must also handle internal-side export statements.
  // TODO: can this be de-duplicated with elaborateLinkPortArray?
  protected def elaborateBlockPortArray(record: ElaborateRecord.BlockPortArray): Unit = {
    import edg.ExprBuilder.{Ref, ValueExpr}
    var nextPortIndex: Int = 0
    val arrayElts = mutable.ListBuffer[String]()

    val portArraySteps = Ref.apply(record.portArray: _*).steps
    val block = resolveBlock(record.parent).asInstanceOf[wir.Block]

    record.constraintNames foreach { constrName =>
      block.mapMultiConstraint(constrName) { constr => (constr.expr: @unchecked) match {
        case expr.ValueExpr.Expr.Connected(connected) =>
          require(constr.getConnected.getBlockPort.getRef.steps == portArraySteps :+ Ref.AllocateStep)
          val portIndex = ref.LocalStep(step=ref.LocalStep.Step.Name(nextPortIndex.toString))
          arrayElts.append(nextPortIndex.toString)
          nextPortIndex += 1
          Seq(constrName -> constr.update(_.connected.blockPort.ref.steps := portArraySteps :+ portIndex))
        case expr.ValueExpr.Expr.Exported(exported) =>
          require(constr.getExported.getInternalBlockPort.getRef.steps == portArraySteps :+ Ref.AllocateStep)
          val portIndex = ref.LocalStep(step=ref.LocalStep.Step.Name(nextPortIndex.toString))
          arrayElts.append(nextPortIndex.toString)
          nextPortIndex += 1
          Seq(constrName -> constr.update(_.exported.internalBlockPort.ref.steps := portArraySteps :+ portIndex))
      }}
    }
    // Try expanding the constraint
    record.constraintNames foreach { constrName =>
      processConnectedConstraint(record.parent, constrName, block.getConstraints(constrName).expr)
    }
  }

  // Once a link-side port array has all its element widths available, this lowers the connect statements
  // by replacing ALLOCATEs with concrete indices.
  protected def elaborateLinkPortArray(record: ElaborateRecord.LinkPortArray): Unit = {
    import edg.ExprBuilder.{Ref, ValueExpr}
    var nextPortIndex: Int = 0
    val arrayElts = mutable.ListBuffer[String]()

    val portArraySteps = Ref.apply(record.portArray: _*).steps
    val block = resolveBlock(record.parent).asInstanceOf[wir.Block]

    record.constraintNames foreach { constrName =>
      block.mapMultiConstraint(constrName) { constr => (constr.expr: @unchecked) match {
        case expr.ValueExpr.Expr.Connected(connected) =>
          require(constr.getConnected.getLinkPort.getRef.steps == portArraySteps :+ Ref.AllocateStep)
          val portIndex = ref.LocalStep(step=ref.LocalStep.Step.Name(nextPortIndex.toString))
          arrayElts.append(nextPortIndex.toString)
          nextPortIndex += 1
          Seq(constrName -> constr.update(_.connected.linkPort.ref.steps := portArraySteps :+ portIndex))
      }}
    }
    debug(s"Link-side Port Array defined: ${record.parent ++ record.portArray} = $arrayElts")
    constProp.setArrayElts(record.parent ++ record.portArray, arrayElts.toSeq)
    constProp.setValue(record.parent.asIndirect ++ record.portArray + IndirectStep.Length, IntValue(arrayElts.length))
    // Try expanding the constraint
    record.constraintNames foreach { constrName =>
      processConnectedConstraint(record.parent, constrName, block.getConstraints(constrName).expr)
    }
  }

  /** Performs full compilation and returns the resulting design. Might take a while.
    */
  def compile(): schema.Design = {
    import edg.ElemBuilder

    // We don't use the usual elaboration flow for the root block because it has no parent and breaks the flow
    // TODO unify with BlockLike in Design
    val rootPb = root.toPb.getHierarchy
    require(rootPb.generators.isEmpty, "root generators not supported")
    processBlock(DesignPath(), root)

    // Ports at top break IS_CONNECTED implies CONNECTED_LINK has valid params
    require(root.getElaboratedPorts.isEmpty, "design top may not have ports")

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

          case generator: ElaborateRecord.Generator =>
            debug(s"Elaborate generator '${generator.fnName}' @ ${generator.blockPath}")
            elaborateGenerator(generator)
            elaboratePending.setValue(generator, None)

          case connected: ElaborateRecord.BlockPortNotConnected =>
            elaborateNotConnected(connected)
            elaboratePending.setValue(connected, None)

          case blockPortArray: ElaborateRecord.BlockPortArray =>
            elaborateBlockPortArray(blockPortArray)
            elaboratePending.setValue(blockPortArray, None)
          case linkPortArray: ElaborateRecord.LinkPortArray =>
            elaborateLinkPortArray(linkPortArray)
            elaboratePending.setValue(linkPortArray, None)

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
