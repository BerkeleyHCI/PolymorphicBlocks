package edg.compiler

import scala.collection.{SeqMap, mutable}
import edgir.schema.schema
import edgir.expr.expr
import edgir.ref.ref
import edgir.ref.ref.LocalPath
import edg.wir.{DesignPath, IndirectDesignPath, IndirectStep, PathSuffix, PortLike, Refinements}
import edg.{EdgirUtils, ExprBuilder, wir}
import edg.util.{DependencyGraph, Errorable}
import edg.util.IterableUtils._


class IllegalConstraintException(msg: String) extends Exception(msg)


sealed trait ElaborateRecord
object ElaborateRecord {
  case class Block(blockPath: DesignPath) extends ElaborateRecord
  case class Link(linkPath: DesignPath) extends ElaborateRecord
  case class Param(paramPath: IndirectDesignPath) extends ElaborateRecord
  case class Generator(blockPath: DesignPath, fnName: String) extends ElaborateRecord

  // Dependency source, set when the connection from the link's port to portPath have been elaborated
  // (or in the link port case, when the link has been elaborated).
  case class ConnectedLink(portPath: DesignPath) extends ElaborateRecord

  case class ParamValue(paramPath: IndirectDesignPath) extends ElaborateRecord

  // These are dependency targets only, to expand CONNECTED_LINK and parameter equivalences when ready
  case class Connect(toLinkPortPath: DesignPath, fromLinkPortPath: DesignPath) extends ElaborateRecord
}


sealed trait CompilerError
object CompilerError {
  case class Unelaborated(elaborateRecord: ElaborateRecord, missing: Set[ElaborateRecord]) extends CompilerError  // may be redundant w/ below

  case class LibraryElement(path: DesignPath, target: ref.LibraryPath) extends CompilerError
  case class Generator(path: DesignPath, target: ref.LibraryPath, fn: String) extends CompilerError

  case class LibraryError(path: DesignPath, target: ref.LibraryPath, err: String) extends CompilerError
  case class GeneratorError(path: DesignPath, target: ref.LibraryPath, fn: String, err: String) extends CompilerError
  case class RefinementSubclassError(path: DesignPath, refinedLibrary: ref.LibraryPath, designLibrary: ref.LibraryPath) extends CompilerError

  case class OverAssign(target: IndirectDesignPath,
                        causes: Seq[OverAssignCause]) extends CompilerError

  case class AbstractBlock(path: DesignPath, blockType: ref.LibraryPath) extends CompilerError {
    override def toString: String = {
      s"Abstract block: $path (of type ${EdgirUtils.SimpleLibraryPath(blockType)})"
    }
  }

  case class FailedAssertion(root: DesignPath, constrName: String,
                             value: expr.ValueExpr, result: ExprValue) extends CompilerError {
    override def toString: String = {
      s"Failed assertion: $root.$constrName, ${ExprToString.apply(value)} => $result"
    }
  }
  case class MissingAssertion(root: DesignPath, constrName: String,
                              value: expr.ValueExpr, missing: Set[ExprRef]) extends CompilerError {
    override def toString: String = {
      s"Unevaluated assertion: $root.$constrName (${ExprToString.apply(value)}), missing ${missing.mkString(", ")}"
    }
  }

  // TODO should this be an error? Currently a debugging tool
  case class EmptyRange(param: IndirectDesignPath, root: DesignPath, constrName: String,
                        value: expr.ValueExpr) extends CompilerError

  sealed trait OverAssignCause
  object OverAssignCause {
    case class Assign(target: IndirectDesignPath, root: DesignPath, constrName: String, value: expr.ValueExpr)
        extends OverAssignCause
    case class Equal(target: IndirectDesignPath, source: IndirectDesignPath)  // TODO constraint info once we track that?
        extends OverAssignCause
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
  private val root = new wir.Block(inputDesignPb.getContents, None)
  def resolve(path: DesignPath): wir.Pathable = root.resolve(path.steps)
  def resolveBlock(path: DesignPath): wir.Block = root.resolve(path.steps).asInstanceOf[wir.Block]
  def resolveLink(path: DesignPath): wir.Link = root.resolve(path.steps).asInstanceOf[wir.Link]
  def resolvePort(path: DesignPath): wir.PortLike = root.resolve(path.steps).asInstanceOf[wir.PortLike]

  // Main data structure that tracks the next unit to elaborate
  private val elaboratePending = DependencyGraph[ElaborateRecord, None.type]()
  elaboratePending.addNode(ElaborateRecord.Block(DesignPath()), Seq())  // seed with root to kick off compilation

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
  // link path -> list of params
  private val linkParams = mutable.HashMap[DesignPath, Seq[IndirectStep]]()
  // port -> connected link path
  private val connectedLink = mutable.HashMap[DesignPath, DesignPath]()
  // set of all connected ports, built from root inwards, fully set for a block's boundary ports once its parent has been elaborated
  private val directConnectedPorts = mutable.Set[DesignPath]()  // direct (indicates whether the port is involved in a connect in enclosing)

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
  // including link parameters (through CONNECTED_LINK) and IS_CONNECTED
  // Neither port can be an array (container) port (array connects should be expanded into individual element connects),
  // but ports may be bundle or inner ports (in bundles or arrays).
  protected def elaborateConnect(toLinkPortPath: DesignPath, fromLinkPortPath: DesignPath): Unit = {
    debug(s"Generate connect equalities for $toLinkPortPath <-> $fromLinkPortPath")

    // Generate port-port parameter propagation
    // All connected ports should have params
    val toLinkPort = resolvePort(toLinkPortPath).asInstanceOf[wir.HasParams]
    val fromLinkPort = resolvePort(fromLinkPortPath).asInstanceOf[wir.HasParams]
    for (paramName <- toLinkPort.getParams.keys listEq fromLinkPort.getParams.keys) {
      constProp.addEquality(
        toLinkPortPath.asIndirect + paramName,
        fromLinkPortPath.asIndirect + paramName
      )
    }

    // Generate IS_CONNECTED propagation
    constProp.addEquality(
      toLinkPortPath.asIndirect + IndirectStep.IsConnected,
      fromLinkPortPath.asIndirect + IndirectStep.IsConnected
    )

    // Generate the CONNECTED_LINK equalities
    val linkPath = connectedLink(toLinkPortPath)
    connectedLink.put(fromLinkPortPath, linkPath)  // propagate CONNECTED_LINK params
    for (linkParam <- linkParams(linkPath)) {
      constProp.addEquality(
        toLinkPortPath.asIndirect + IndirectStep.ConnectedLink + linkParam,
        fromLinkPortPath.asIndirect + IndirectStep.ConnectedLink + linkParam
      )
    }

    // Add sub-ports to the elaboration dependency graph, as appropriate
    (toLinkPort, fromLinkPort) match {
      case (toLinkPort: wir.Bundle, fromLinkPort: wir.Bundle) =>
        for (portName <- toLinkPort.getElaboratedPorts.keys listEq fromLinkPort.getElaboratedPorts.keys) {
          elaboratePending.addNode(
            ElaborateRecord.Connect(toLinkPortPath + portName, fromLinkPortPath + portName),
            Seq(ElaborateRecord.ConnectedLink(toLinkPortPath + portName))
          )
        }
      case (toLinkPort, fromLinkPort) => // everything else ignored
    }

    // Register port as finished
    elaboratePending.setValue(ElaborateRecord.ConnectedLink(fromLinkPortPath), None)
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
        debug(s"Elaborate Port at $path: ${readableLibraryPath(libraryPath)}")

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
        processParamDeclarations(path, port)
      case port: wir.Bundle =>
        processParamDeclarations(path, port)
        for ((childPortName, childPort) <- port.getUnelaboratedPorts) {
          elaboratePort(path + childPortName, port, childPort)
        }
      case port: wir.PortArray =>
        // arrays have no params, but we need to instantiate the array
        val childPortNames = constProp.getArrayElts(path) match {
          case Some(elts) => elts
          case None =>  // TODO can the empty case be set with everything else?
            constProp.setArrayElts(path, Seq())
            constProp.setValue(path.asIndirect + IndirectStep.Length, IntValue(0))
            Seq()
        }
        val childPortLibraries = (childPortNames map { childPortName =>
          childPortName -> wir.PortLibrary.apply(port.getType)
        }).toMap
        port.setPorts(childPortLibraries)
        for ((childPortName, childPort) <- port.getUnelaboratedPorts) {
          elaboratePort(path + childPortName, port, childPort)
        }
      case port => throw new NotImplementedError(s"unknown instantiated port $port")
    }
  }

  protected def processPortConnected(portPath: DesignPath, port: wir.PortLike,
                                     setConnects: Boolean): Unit = port match {
    case port @ (_: wir.Port | _: wir.Bundle) =>
      val isConnected = directConnectedPorts.contains(portPath)
      if (!isConnected) {
        constProp.setValue(portPath.asIndirect + IndirectStep.IsConnected,
          BooleanValue(false),
          "top isConnected")
        elaboratePending.setValue(ElaborateRecord.FullConnectedPort(portPath), None)
      } else if (isConnected && setConnects) {
        constProp.setValue(portPath.asIndirect + IndirectStep.IsConnected,
          BooleanValue(true),
          "top isConnected")
      }
    case port: wir.PortArray =>
      port.getElaboratedPorts.foreach { case (name, subport) =>
        processPortConnected(portPath + name, subport, setConnects)
      }
    case port => throw new NotImplementedError(s"unknown unelaborated port $port")
  }

  protected def setPortConnectedLinkParams(portPath: DesignPath, port: wir.PortLike,
                                           linkPath: DesignPath, params: Seq[String],
                                           recursive: Boolean): Unit = {
    port match {
      case port @ (_: wir.Port | _: wir.Bundle) =>
        val allParams = params.map(IndirectStep.Element(_)) :+ IndirectStep.Name
        connectedLinkParams.put(portPath, (linkPath, allParams))
        allParams.foreach { paramName =>
          constProp.addEquality(
            portPath.asIndirect + IndirectStep.ConnectedLink + paramName,
            linkPath.asIndirect + paramName
          )
        }
        elaboratePending.setValue(ElaborateRecord.ConnectedLink(portPath), None)
      case port: wir.PortArray => port.getElaboratedPorts.foreach { case (name, subport) =>
        setPortConnectedLinkParams(portPath + name, subport, linkPath, params, recursive)
      }
      case port => throw new NotImplementedError(s"unknown unelaborated port $port")
    }
    // Recurse (for non mandatory types) if needed
    port match {
      case port: wir.Bundle => if (recursive) {
        port.getElaboratedPorts.foreach { case (name, subport) =>
          setPortConnectedLinkParams(portPath + name, subport, linkPath, params, recursive)
        }
      }
      case _ =>  // ignore
    }
  }

  // TODO clean this up... by a lot
  def processBlocklikeConstraint: PartialFunction[(DesignPath, String, expr.ValueExpr, expr.ValueExpr.Expr), Unit] = {
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

  protected def processBlock(path: DesignPath, block: wir.Block): Unit = {
    import edg.ExprBuilder.{Ref, ValueExpr}
    import edgir.ref.ref

    // Elaborate ports, generating equivalence constraints as needed
    // TODO support port.NAME
    elaborateContainedPorts(path, block)
    processParamDeclarations(path, block)

    // Find allocate ports and lower them before processing all constraints
    val linkPortAllocates = mutable.HashMap[Seq[String], mutable.ListBuffer[(String, Seq[String])]]()
    block.getConstraints.foreach { case (constrName, constr) => constr.expr match {
      case expr.ValueExpr.Expr.Connected(connected) =>
        (connected.getBlockPort, connected.getLinkPort) match {
          case (ValueExpr.Ref(blockPort), ValueExpr.RefAllocate(linkPortArray)) =>
            linkPortAllocates.getOrElseUpdate(linkPortArray, mutable.ListBuffer()) += ((constrName, blockPort))
          case _ =>
        }
      case _ =>
    }}

    // For fully resolved arrays, allocate port numbers and set array elements
    linkPortAllocates.foreach { case (linkPortArray, blockConstrPorts) =>
      val linkPortArrayElts = blockConstrPorts.zipWithIndex.map { case ((constrName, blockPort), index) =>
        block.mapConstraint(constrName) { constr =>
          val steps = constr.getConnected.getLinkPort.getRef.steps
          require(steps.last == Ref.AllocateStep)
          val indexStep = ref.LocalStep(step=ref.LocalStep.Step.Name(index.toString))
          constr.update(
            _.connected.linkPort.ref.steps := steps.slice(0, steps.length - 1) :+ indexStep
          )
        }
        index.toString
      }.toSeq
      debug(s"Array defined: ${path ++ linkPortArray} = $linkPortArrayElts")
      constProp.setArrayElts(path ++ linkPortArray, linkPortArrayElts)
      constProp.setValue(path.asIndirect ++ linkPortArray + IndirectStep.Length,
        IntValue(linkPortArrayElts.length))
    }

    // Process constraints:
    // - for connected constraints, add into the connectivity map
    // - for assignment constraints, add into const prop
    // - for other constraints, add into asserts list
    // TODO ensure constraint processing order?
    // All ports that need to be allocated, with the list of connected ports,
    // as (port array path -> list(constraint name, block port))
    block.getConstraints.foreach { case (constrName, constr) => constr.expr match {
      case expr if processBlocklikeConstraint.isDefinedAt(path, constrName, constr, expr) =>
        processBlocklikeConstraint(path, constrName, constr, expr)
      case expr.ValueExpr.Expr.Connected(connected) =>
        (connected.getBlockPort, connected.getLinkPort) match {
          case (ValueExpr.Ref(blockPort), ValueExpr.Ref(linkPort)) =>
            elaboratePending.addNode(
              ElaborateRecord.Connect(path ++ linkPort, path ++ blockPort),
              Seq(ElaborateRecord.Block(path + blockPort.head),
                ElaborateRecord.Link(path + linkPort.head),
                ElaborateRecord.ConnectedLink(path ++ linkPort))
            )
            directConnectedPorts += (path ++ blockPort)
            directConnectedPorts += (path ++ linkPort)
          case (ValueExpr.Ref(blockPort), ValueExpr.RefAllocate(linkPortArray)) =>
            throw new Exception("This constraint should have been lowered")
          case (ValueExpr.RefAllocate(blockPortArray), ValueExpr.RefAllocate(linkPortArray)) =>
            throw new NotImplementedError(s"TODO: block port array <-> link port array: ${constr.expr}")
          case (ValueExpr.RefAllocate(blockPortArray), ValueExpr.Ref(linkPort)) =>
            throw new NotImplementedError(s"TODO: block port array <-> link port: ${constr.expr}")
          case _ => throw new IllegalConstraintException(s"unknown connect in block $path: $constrName = $connected")
        }
      case expr.ValueExpr.Expr.Exported(exported) =>
        (exported.getExteriorPort, exported.getInternalBlockPort) match {
          case (ValueExpr.Ref(extPort), ValueExpr.Ref(intPort)) =>
            elaboratePending.addNode(
              ElaborateRecord.Connect(path ++ extPort, path ++ intPort),
              Seq(ElaborateRecord.Block(path),
                ElaborateRecord.Block(path + intPort.head),
                ElaborateRecord.ConnectedLink(path ++ extPort))
            )
            // TODO: this allows exporting into exterior ports' inner ports. Is this clean?
            directConnectedPorts += (path ++ intPort)
          case (ValueExpr.RefAllocate(extPortArray), ValueExpr.RefAllocate(intPortArray)) =>
            throw new NotImplementedError(s"TODO: export port array <-> port array: ${constr.expr}")
          case (ValueExpr.RefAllocate(extPortArray), ValueExpr.Ref(intPort)) =>
            throw new NotImplementedError(s"TODO: export port array <-> port: ${constr.expr}")
          case (ValueExpr.Ref(extPort), ValueExpr.RefAllocate(intPortArray)) =>
            throw new NotImplementedError(s"TODO: export port <-> port array: ${constr.expr}")
          case _ => throw new IllegalConstraintException(s"unknown export in block $path: $constrName = $exported")
        }
      case _ => throw new IllegalConstraintException(s"unknown constraint in block $path: $constrName = $constr")
    }}

    // Queue up generators as needed
    for ((generatorFnName, generator) <- block.getGenerators) {
      elaboratePending.addNode(ElaborateRecord.Generator(path, generatorFnName),
        generator.required_params.map { depPath =>
          ElaborateRecord.ParamValue(path.asIndirect ++ depPath)
        } ++ generator.required_ports.map { depPort =>
          ElaborateRecord.FullConnectedPort(path ++ depPort)
        }
      )
    }

    val blockGeneratorsElaborate = block.getGenerators.map { case (generatorFnName, generator) =>
      val generatorRecord = ElaborateRecord.Generator(path, generatorFnName)
      generator.connecting_blocks.map { connectingBlockPath =>
        require(connectingBlockPath.steps.length == 1)  // TODO cleaner way to handle this?
        (connectingBlockPath.steps.head.getName, generatorRecord)
      }
    }.flatten.groupBy(_._1).view.mapValues(_.map(_._2)).toMap

    // Queue up sub-trees that need elaboration - needs to be post-generate for generators
    // subtree ports can't know connected state until own connected state known
    val selfPortsConnectedElaborateRecord = ElaborateRecord.BlockPortsConnected(path)
    for (blockName <- block.getUnelaboratedBlocks.keys) {
      debug(s"Push block to pending: ${path + blockName}")
      val blockElaborateRecord = ElaborateRecord.Block(path + blockName)
      elaboratePending.addNode(blockElaborateRecord, Seq())
      elaboratePending.addNode(ElaborateRecord.BlockPortsConnected(path + blockName),
        Seq(blockElaborateRecord, selfPortsConnectedElaborateRecord) ++
            blockGeneratorsElaborate.getOrElse(blockName, Seq())
      )
    }
    for (linkName <- block.getUnelaboratedLinks.keys) {
      debug(s"Push link to pending: ${path + linkName}")
      elaboratePending.addNode(ElaborateRecord.Link(path + linkName), Seq())
    }
  }

  /** Elaborate the unelaborated block at path (but where the parent has been elaborated and is reachable from root),
    * and adds it to the parent and replaces the lib_elem proto entry with a placeholder unknown.
    * Adds children to the pending queue, and adds constraints to constProp.
    * Expands connects in the parent, as needed.
    */
  protected def elaborateBlock(path: DesignPath): Unit = {
    val (parentPath, name) = path.split

    // Instantiate block from library element to wir.Block
    val parent = resolveBlock(parentPath)
    val libraryPath = parent.getUnelaboratedBlocks(name).asInstanceOf[wir.BlockLibrary].target
    debug(s"Elaborate block at $path: ${readableLibraryPath(libraryPath)}")
    val (refinedLibrary, unrefinedType) = refinements.instanceRefinements.get(path) match {
      case Some(refinement) => (refinement, Some(libraryPath))
      case None => refinements.classRefinements.get(libraryPath) match {
        case Some(refinement) => (refinement, Some(libraryPath))
        case None => (libraryPath, None)
      }
    }

    val blockPb = library.getBlock(refinedLibrary) match {
      case Errorable.Success(blockPb) =>
        if (!library.isSubclassOf(refinedLibrary, libraryPath)) {
          errors += CompilerError.RefinementSubclassError(path, refinedLibrary, libraryPath)
        }
        blockPb
      case Errorable.Error(err) =>
        import edgir.elem.elem
        errors += CompilerError.LibraryError(path, refinedLibrary, err)
        elem.HierarchyBlock()
    }
    val block = new wir.Block(blockPb, unrefinedType)

    // Populate class-based value refinements
    refinements.classValues.get(refinedLibrary) match {
      case Some(classValueRefinements) => for ((subpath, value) <- classValueRefinements) {
        constProp.setForcedValue(
          path.asIndirect ++ subpath, value,
          s"${refinedLibrary.getTarget.getName} class refinement")
      }
      case None =>
    }
    constProp.setValue(path.asIndirect + IndirectStep.Name, TextValue(path.toString))

    // Process block
    processBlock(path, block)

    // Link block in parent
    parent.elaborate(name, block)
  }

  protected def processLink(path: DesignPath, link: wir.Link): Unit = {
    import edg.ExprBuilder.{Ref, ValueExpr}

    // Elaborate ports, generating equivalence constraints as needed
    // TODO support port.NAME
    elaborateContainedPorts(path, link)
    processParamDeclarations(path, link)
    for ((name, port) <- link.getElaboratedPorts) {
      setPortConnectedLinkParams(path + name, port, path, link.getParams.keys.toSeq, false)
      processPortConnected(path + name, port, true)
    }

    // All inner link ports that need to be allocated, and constraints connecting to it
    // as (path to inner link port array -> constraint names)
    val innerLinkArrayConstraints = mutable.HashMap[Seq[String], mutable.ListBuffer[String]]()

    // Process constraints, as in the block case
    link.getConstraints.foreach { case (constrName, constr) => constr.expr match {
      case expr if processBlocklikeConstraint.isDefinedAt(path, constrName, constr, expr) =>
        processBlocklikeConstraint(path, constrName, constr, expr)
      case expr.ValueExpr.Expr.Exported(exported) =>
        (exported.getExteriorPort, exported.getInternalBlockPort) match {
          case (ValueExpr.Ref(extPort), ValueExpr.Ref(intPort)) =>
            elaboratePending.addNode(
              ElaborateRecord.Connect(path ++ intPort, path ++ extPort),
              Seq(ElaborateRecord.Link(path),
                ElaborateRecord.Link(path + intPort.head),
                ElaborateRecord.ConnectedLink(path ++ intPort))
            )
            // TODO: this allows exporting into exterior ports' inner ports. Is this clean?
            directConnectedPorts += (path ++ intPort)
          case (ValueExpr.MapExtract(ValueExpr.Ref(extPortArray), Ref(extPortInner)),
              ValueExpr.RefAllocate(intPortArray)) =>
            innerLinkArrayConstraints.getOrElseUpdate(intPortArray, mutable.ListBuffer()) += constrName
          case (ValueExpr.Ref(extPort), ValueExpr.RefAllocate(intPortArray)) =>
            innerLinkArrayConstraints.getOrElseUpdate(intPortArray, mutable.ListBuffer()) += constrName
          case (ValueExpr.RefAllocate(extPortArray), ValueExpr.RefAllocate(intPortArray)) =>
            throw new NotImplementedError(s"TODO: export port array <-> port array: ${constr.expr}")
          case (ValueExpr.RefAllocate(extPortArray), ValueExpr.Ref(intPort)) =>
            throw new NotImplementedError(s"TODO: export port array <-> port: ${constr.expr}")
          case _ => throw new IllegalConstraintException(s"unknown export in link $path: $constrName = $exported")
        }
      case _ => throw new IllegalConstraintException(s"unknown constraint in link $path: $constrName = $constr")
    }}

    // Expand arrays
    innerLinkArrayConstraints.foreach { case (intPortArray, constrNames) =>
      var nextIndex = 0
      val intPortArrayElts = constrNames.flatMap { constrName =>
        var thisArrayElts = mutable.ListBuffer[String]()
        link.mapMultiConstraint(constrName) { constr =>
          val extPorts = (constr.getExported.getExteriorPort, constr.getExported.getInternalBlockPort) match {
            // get individual external ports
            case (ValueExpr.MapExtract(ValueExpr.Ref(extPortArray), Ref(extPortInner)),
            ValueExpr.RefAllocate(constrIntPortArray)) =>  // vector-vector connect
              require(intPortArray == constrIntPortArray)
              constProp.getArrayElts(path ++ extPortArray).get.map { extArrayElt =>
                (extPortArray :+ extArrayElt) ++ extPortInner }
            case (ValueExpr.Ref(extPort), ValueExpr.RefAllocate(constrIntPortArray)) =>  // element-vector connect
              require(intPortArray == constrIntPortArray)
              Seq(extPort)
            case _ => throw new IllegalArgumentException(s"Unknown constraint in expanding array: $constr")
          }
          val startIndex = nextIndex
          nextIndex += extPorts.length

          extPorts.zipWithIndex.map { case (extPort, index) =>
            val arrayIndex = (index + startIndex).toString
            thisArrayElts += arrayIndex

            elaboratePending.addNode(
              ElaborateRecord.Connect(path ++ intPortArray + arrayIndex, path ++ extPort),
              Seq(ElaborateRecord.Link(path),
                ElaborateRecord.Link(path + intPortArray.head),
                ElaborateRecord.ConnectedLink(path ++ intPortArray + arrayIndex))
            )
            directConnectedPorts += (path ++ intPortArray + arrayIndex)

            val newConstrName = if (extPorts.length == 1) {
              constrName  // constraints don't expand
            } else {
              constrName + "." + index  // expands into multiple constraints, each needs a unique name
            }
            val newConstr = constr.update(
              _.exported.exteriorPort.ref.steps := extPort.map { pathElt =>
                ref.LocalStep(ref.LocalStep.Step.Name(pathElt)) },
              _.exported.internalBlockPort.ref.steps := (intPortArray :+ arrayIndex).map { pathElt =>
                ref.LocalStep(ref.LocalStep.Step.Name(pathElt)) },
            )

            newConstrName -> newConstr
          }
        }

        thisArrayElts.toSeq
      }.toSeq
      debug(s"Array defined: ${path ++ intPortArray} = $intPortArrayElts")
      constProp.setArrayElts(path ++ intPortArray, intPortArrayElts)
      constProp.setValue(path.asIndirect ++ intPortArray + IndirectStep.Length,
        IntValue(intPortArrayElts.length))
    }

    // Queue up sub-trees that need elaboration - needs to be post-generate for generators
    for (linkName <- link.getUnelaboratedLinks.keys) {
      debug(s"Push link to pending: ${path + linkName}")
      elaboratePending.addNode(ElaborateRecord.Link(path + linkName), Seq())
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
    debug(s"Elaborate link at $path: ${readableLibraryPath(libraryPath)}")

    val linkPb = library.getLink(libraryPath) match {
      case Errorable.Success(linkPb) => linkPb
      case Errorable.Error(err) =>
        import edgir.elem.elem
        errors += CompilerError.LibraryError(path, libraryPath, err)
        elem.Link()
    }
    val link = new wir.Link(linkPb)

    constProp.setValue(path.asIndirect + IndirectStep.Name, TextValue(path.toString))

    // Process block
    processLink(path, link)

    // Link block in parent
    parent.elaborate(name, link)
  }

  /** Elaborates the generator, running it and merging the result with the block.
    */
  protected def elaborateGenerator(blockPath: DesignPath, fnName: String): Unit = {
    debug(s"Elaborate generator $fnName at $blockPath")
    val block = resolveBlock(blockPath)
    val generator = block.getGenerators(fnName)
    block.removeGenerator(fnName)

    val reqParamValues = generator.required_params.map { reqParam =>
      reqParam -> constProp.getValue(blockPath.asIndirect ++ reqParam).get
    }.toMap
    val reqPortValues = generator.required_ports.flatMap { reqPort =>
      val isConnectedSuffix = PathSuffix() ++ reqPort + IndirectStep.IsConnected
      val isConnectedValue = constProp.getValue(blockPath.asIndirect ++ isConnectedSuffix).get
          .asInstanceOf[BooleanValue]
      isConnectedValue.value match {
        case true =>
          val connectedNameSuffix = PathSuffix() ++ reqPort + IndirectStep.ConnectedLink + IndirectStep.Name
          val connectedNameValue = constProp.getValue(blockPath.asIndirect ++ connectedNameSuffix).get
              .asInstanceOf[TextValue]
          Map(isConnectedSuffix.asLocalPath() -> isConnectedValue,
            connectedNameSuffix.asLocalPath() -> connectedNameValue)
        case false =>
          Map(isConnectedSuffix.asLocalPath() -> isConnectedValue)
      }
    }.toMap

    // TODO pass through IS_CONNECTED
    val generatorResult = library.runGenerator(block.getBlockClass, fnName,
      reqParamValues ++ reqPortValues
    )
    val generatedPb = generatorResult match {
      case Errorable.Success(generatedPb) =>
        require(generatedPb.getSelfClass == block.getBlockClass)
        block.dedupGeneratorPb(generatedPb)
      case Errorable.Error(err) =>
        import edgir.elem.elem
        errors += CompilerError.GeneratorError(blockPath, block.getBlockClass, fnName, err)
        elem.HierarchyBlock()
    }

    val generatedDiffBlock = new wir.Block(generatedPb, None)
    processBlock(blockPath, generatedDiffBlock)
    block.append(generatedDiffBlock)
  }

  protected def elaborateBlockPortsConnected(blockPath: DesignPath): Unit = {
    val block = resolveBlock(blockPath)
    for ((name, port) <- block.getElaboratedPorts) {
      if (!directConnectedPorts.contains(blockPath + name)) {
        // TODO this needs to not be transitive, should only fire for the topmost disconnected
        // TODO this is hacky, to add the recursive elaboration record
        setPortConnectedLinkParams(blockPath + name, port, DesignPath(), Seq(), true)
      }
      processPortConnected(blockPath + name, port, false)
    }
  }


  /** Performs full compilation and returns the resulting design. Might take a while.
    */
  def compile(): schema.Design = {
    import edg.ElemBuilder

    // Ports at top break IS_CONNECTED implies CONNECTED_LINK has valid params
    require(root.getElaboratedPorts.isEmpty, "design top may not have ports")

    while (elaboratePending.getReady.nonEmpty) {
      elaboratePending.getReady.foreach { elaborateRecord =>
        onElaborate(elaborateRecord)
        elaborateRecord match {
          case elaborateRecord@ElaborateRecord.Block(blockPath) =>
            elaborateBlock(blockPath)
            elaboratePending.setValue(elaborateRecord, None)
          case elaborateRecord@ElaborateRecord.Link(linkPath) =>
            elaborateLink(linkPath)
            elaboratePending.setValue(elaborateRecord, None)
          case elaborateRecord@ElaborateRecord.Connect(toLinkPortPath, fromLinkPortPath) =>
            elaborateConnect(toLinkPortPath, fromLinkPortPath)
            elaboratePending.setValue(elaborateRecord, None)
          case elaborateRecord@ElaborateRecord.Generator(blockPath, fnName) =>
            elaborateGenerator(blockPath, fnName)
            elaboratePending.setValue(elaborateRecord, None)
          case elaborateRecord@ElaborateRecord.BlockPortsConnected(blockPath) =>
            elaborateBlockPortsConnected(blockPath)
            elaboratePending.setValue(elaborateRecord, None)
          case elaborateRecord => throw new IllegalArgumentException(s"unknown ready elaboration target $elaborateRecord")
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

  def getConnectedLink(port: DesignPath): Option[DesignPath] = connectedLinkParams.get(port) match {
    case Some((linkPath, linkParams)) if linkPath == DesignPath() => None  // this is a hack, because disconnected ports generate a dummy entry
    case Some((linkPath, linkParams)) => Some(linkPath)
    case None => None
  }
}
