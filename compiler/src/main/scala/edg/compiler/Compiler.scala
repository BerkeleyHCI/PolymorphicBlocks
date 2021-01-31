package edg.compiler

import edg.compiler.hdl.HdlInterfaceGrpc.HdlInterface

import scala.collection.mutable
import edg.schema.schema
import edg.expr.expr
import edg.ref.ref
import edg.wir.{DesignPath, IndirectDesignPath, IndirectStep}
import edg.wir
import edg.util.DependencyGraph


class IllegalConstraintException(msg: String) extends Exception(msg)


sealed trait ElaborateRecord
object ElaborateRecord {
  case class Block(blockPath: DesignPath) extends ElaborateRecord
  case class Link(linkPath: DesignPath) extends ElaborateRecord
  case class Param(paramPath: IndirectDesignPath) extends ElaborateRecord
  case class Generator(blockPath: DesignPath, fnName: String) extends ElaborateRecord

  // dependency source, when the port's CONNECTED_LINK equivalences have been elaborated,
  // and inserted into the link params data structure
  case class ConnectedLink(portPath: DesignPath) extends ElaborateRecord
  case class ParamValue(paramPath: IndirectDesignPath) extends ElaborateRecord

  // These are dependency targets only, to expand CONNECTED_LINK and parameter equivalences when ready
  case class Connect(toLinkPortPath: DesignPath, fromLinkPortPath: DesignPath) extends ElaborateRecord
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
class Compiler(inputDesignPb: schema.Design, library: edg.wir.Library) {
  // TODO better debug toggle
//  protected def debug(msg: => String): Unit = println(msg)
  protected def debug(msg: => String): Unit = { }

  def readableLibraryPath(path: ref.LibraryPath): String = {  // TODO refactor to shared utils?
    path.getTarget.getName
  }


  private val elaboratePending = DependencyGraph[ElaborateRecord, None.type]()

  private val constProp = new ConstProp() {
    override def onParamSolved(param: IndirectDesignPath, value: ExprValue): Unit = {
      elaboratePending.setValue(ElaborateRecord.ParamValue(param), null)
    }
  }
  private val assertions = mutable.Buffer[(DesignPath, String, expr.ValueExpr, SourceLocator)]()  // containing block, name, expr

  // Supplemental elaboration data structures
  // port -> (connected link path, list of params of the connected link)
  private val connectedLinkParams = mutable.HashMap[DesignPath, (DesignPath, Seq[String])]()
  // set of all connected ports, built from root inwards
  private val connectedPorts = mutable.Set[DesignPath]()  // transitive (lack of connects propagates through exports)
  private val directConnectedPorts = mutable.Set[DesignPath]()  // direct (indicates whether the port is involved in a connect in enclosing)

  // TODO clean up this API?
  private[edg] def getValue(path: IndirectDesignPath): Option[ExprValue] = constProp.getValue(path)


  // Seed compilation with the root
  //
  private val root = new wir.Block(inputDesignPb.getContents, inputDesignPb.getContents.superclasses)
  def resolve(path: DesignPath): wir.Pathable = root.resolve(path.steps)
  def resolveBlock(path: DesignPath): wir.Block = root.resolve(path.steps).asInstanceOf[wir.Block]
  def resolveLink(path: DesignPath): wir.Link = root.resolve(path.steps).asInstanceOf[wir.Link]
  def resolvePort(path: DesignPath): wir.PortLike = root.resolve(path.steps).asInstanceOf[wir.PortLike]

  processBlock(DesignPath.root, root)
  elaboratePending.setValue(ElaborateRecord.Block(DesignPath.root), None)

  // Actual compilation methods
  //
  protected def elaborateConnect(toLinkPortPath: DesignPath, fromLinkPortPath: DesignPath): Unit = {
    debug(s"Generate connect equalities for $toLinkPortPath <-> $fromLinkPortPath")

    // Generate port-port parameter propagation
    // All connected ports should have params
    val toLinkPort = resolvePort(toLinkPortPath)
    val fromLinkPort = resolvePort(fromLinkPortPath)
    val toLinkPortParams = toLinkPort.asInstanceOf[wir.HasParams].getParams.keys
    val fromLinkPortParams = fromLinkPort.asInstanceOf[wir.HasParams].getParams.keys
    require(toLinkPortParams == fromLinkPortParams,
      s"connected ports at $toLinkPortPath, $fromLinkPortPath with different params")
    for (paramName <- toLinkPortParams) {
      constProp.addEquality(
        IndirectDesignPath.fromDesignPath(toLinkPortPath) + paramName,
        IndirectDesignPath.fromDesignPath(fromLinkPortPath) + paramName
      )
    }

    // Generate the CONNECTED_LINK equalities
    val (linkPath, linkParams) = connectedLinkParams(toLinkPortPath)
    connectedLinkParams.put(fromLinkPortPath, (linkPath, linkParams))  // propagate CONNECTED_LINK params
    for (linkParam <- linkParams) {
      constProp.addEquality(
        IndirectDesignPath.fromDesignPath(toLinkPortPath) + IndirectStep.ConnectedLink + linkParam,
        IndirectDesignPath.fromDesignPath(fromLinkPortPath) + IndirectStep.ConnectedLink + linkParam
      )
    }

    // Add sub-ports to the elaboration dependency graph, as appropriate
    (toLinkPort, fromLinkPort) match {
      case (toLinkPort: wir.Bundle, fromLinkPort: wir.Bundle) =>
        require(toLinkPort.getElaboratedPorts.keys == fromLinkPort.getElaboratedPorts.keys,
          s"connected bundles at $toLinkPortPath, $fromLinkPortPath with different ports")
        for (portName <- toLinkPort.getElaboratedPorts.keys) {
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

  protected def processParams(path: DesignPath, hasParams: wir.HasParams): Unit = {
    for ((paramName, param) <- hasParams.getParams) {
      constProp.addDeclaration(path + paramName, param)
    }
  }

  protected def generateConnectedEquivalence(container1: IndirectDesignPath, container2: IndirectDesignPath,
                                   hasParams: wir.HasParams): Unit = {
    for (paramName <- hasParams.getParams.keys) {
      constProp.addEquality(container1 + paramName, container2 + paramName)
    }
  }

  protected def processPort(path: DesignPath, port: wir.PortLike): Unit = port match {
    // TODO better semantics and consistency between this and processBlock/processLink
    // Unlike those, this is called with the final port object (after LibraryElements replaced).
    // Main issue is that PortArray doesn't have a meaningful elaborate(), instead using bulk setPorts
    case port: wir.Port =>
      processParams(path, port)
    case port: wir.Bundle =>
      processParams(path, port)
      elaborateContainedPorts(path, port)  // discard directContainingLink when recursing inside
    case port: wir.PortArray =>
      val libraryPath = port.getType
      debug(s"Elaborate PortArray at $path: ${readableLibraryPath(libraryPath)}")
      // TODO can / should this share the LibraryElement instantiation logic w/ elaborate BlocklikePorts?
      // TODO .getOrElse is needed for ports that don't get connected, but may want something stricter
      // especially when block side arrays become a thing
      val newPorts = constProp.getArrayElts(path).getOrElse(Seq()).map { index =>
        index -> wir.PortLike.fromIrPort(library.getPort(libraryPath), libraryPath)
      }.toMap
      port.setPorts(newPorts)  // the PortArray is elaborated in-place instead of needing a new object
      newPorts.foreach { case (index, subport) =>
        processPort(path + index, subport)
      }
    case port => throw new NotImplementedError(s"unknown unelaborated port $port")
  }

  protected def elaborateContainedPorts(path: DesignPath, hasPorts: wir.HasMutablePorts): Unit = {
    for ((portName, port) <- hasPorts.getUnelaboratedPorts) { port match {
      case port: wir.LibraryElement =>
        val libraryPath = port.target
        debug(s"Elaborate Port at ${path + portName}: ${readableLibraryPath(libraryPath)}")
        val newPort = wir.PortLike.fromIrPort(library.getPort(libraryPath), libraryPath)
        hasPorts.elaborate(portName, newPort)
        processPort(path + portName, newPort)
      case port: wir.PortArray =>
        processPort(path + portName, port)
      case port => throw new NotImplementedError(s"unknown unelaborated port $port")
    }}
  }

  protected def processPortConnected(portPath: DesignPath, port: wir.PortLike): Unit = port match {
    case port @ (_: wir.Port | _: wir.Bundle) =>
      constProp.setValue(IndirectDesignPath.fromDesignPath(portPath) + IndirectStep.IsConnected,
        BooleanValue(connectedPorts.contains(portPath)))
    case port: wir.PortArray => port.getElaboratedPorts.foreach { case (name, subport) =>
      processPortConnected(portPath + name, subport)
    }
    case port => throw new NotImplementedError(s"unknown unelaborated port $port")
  }

  protected def setPortConnectedLinkParams(portPath: DesignPath, port: wir.PortLike,
                                           linkPath: DesignPath, params: Seq[String],
                                           recursive: Boolean): Unit = {
    port match {
      case port @ (_: wir.Port | _: wir.Bundle) =>
        connectedLinkParams.put(portPath, (linkPath, params))
        params.foreach { paramName =>
          constProp.addEquality(
            IndirectDesignPath.fromDesignPath(portPath) + IndirectStep.ConnectedLink + paramName,
            IndirectDesignPath.fromDesignPath(linkPath) + paramName
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
        IndirectDesignPath.fromDesignPath(path) ++ assign.dst.get,
        path, assign.src.get,
        SourceLocator.empty)  // TODO add sourcelocators
    case (path, constrName, constr, expr.ValueExpr.Expr.Binary(_) | expr.ValueExpr.Expr.Reduce(_)) =>
      assertions += ((path, constrName, constr, SourceLocator.empty))  // TODO add source locators
    case (path, constrName, constr, expr.ValueExpr.Expr.Ref(target))
      if target.steps.last.step.isReservedParam
          && target.steps.last.getReservedParam == ref.Reserved.IS_CONNECTED =>
      assertions += ((path, constrName, constr, SourceLocator.empty))  // TODO add source locators
  }

  protected def processBlock(path: DesignPath, block: wir.Block): Unit = {
    import edg.ExprBuilder.{Ref, ValueExpr}
    import edg.ref.ref

    // Elaborate ports, generating equivalence constraints as needed
    elaborateContainedPorts(path, block)
    processParams(path, block)
    for ((name, port) <- block.getElaboratedPorts) {
      if (!directConnectedPorts.contains(path + name)) {
        // TODO this needs to not be transitive, should only fire for the topmost disconnected
        setPortConnectedLinkParams(path + name, port, DesignPath.root, Seq(), true)
      }
      processPortConnected(path + name, port)
    }

    // Process constraints:
    // - for connected constraints, add into the connectivity map
    // - for assignment constraints, add into const prop
    // - for other constraints, add into asserts list
    // TODO ensure constraint processing order?
    // All ports that need to be allocated, with the list of connected ports,
    // as (port array path -> list(constraint name, block port))
    val linkPortAllocates = mutable.HashMap[Seq[String], mutable.ListBuffer[(String, Seq[String])]]()
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
            connectedPorts += (path ++ blockPort)
            directConnectedPorts += (path ++ blockPort)
            connectedPorts += (path ++ linkPort)
            directConnectedPorts += (path ++ linkPort)
          case (ValueExpr.Ref(blockPort), ValueExpr.RefAllocate(linkPortArray)) =>
            linkPortAllocates.getOrElseUpdate(linkPortArray, mutable.ListBuffer()) += ((constrName, blockPort))
          case (ValueExpr.RefAllocate(blockPortArray), ValueExpr.RefAllocate(linkPortArray)) =>
            throw new NotImplementedError("TODO: block port array <-> link port array")
          case (ValueExpr.RefAllocate(blockPortArray), ValueExpr.Ref(linkPort)) =>
            throw new NotImplementedError("TODO: block port array <-> link port")
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
            if (connectedPorts.contains(path + extPort.head)) {
              connectedPorts += (path ++ intPort)
            }
            directConnectedPorts += (path ++ intPort)
          case (ValueExpr.RefAllocate(extPortArray), ValueExpr.RefAllocate(intPortArray)) =>
            throw new NotImplementedError("TODO: export port array <-> port array")
          case (ValueExpr.RefAllocate(extPortArray), ValueExpr.Ref(intPort)) =>
            throw new NotImplementedError("TODO: export port array <-> port")
          case (ValueExpr.Ref(extPort), ValueExpr.RefAllocate(intPortArray)) =>
            throw new NotImplementedError("TODO: export port <-> port array")
          case _ => throw new IllegalConstraintException(s"unknown export in block $path: $constrName = $exported")
        }
      case _ => throw new IllegalConstraintException(s"unknown constraint in block $path: $constrName = $constr")
    }}

    // For fully resolved arrays, allocate port numbers and set array elements
    linkPortAllocates.foreach { case (linkPortArray, blockConstrPorts) =>
      val linkPortArrayElts = blockConstrPorts.zipWithIndex.map { case ((constrName, blockPort), index) =>
        elaboratePending.addNode(
          ElaborateRecord.Connect(path ++ linkPortArray + index.toString, path ++ blockPort),
          Seq(ElaborateRecord.Block(path + blockPort.head),
            ElaborateRecord.Link(path + linkPortArray.head),
            ElaborateRecord.ConnectedLink(path ++ linkPortArray + index.toString))
        )
        connectedPorts += (path ++ blockPort)
        directConnectedPorts += (path ++ blockPort)
        connectedPorts += (path ++ linkPortArray + index.toString)
        directConnectedPorts += (path ++ linkPortArray + index.toString)

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
    }

    // Queue up generators as needed
    for ((generatorFnName, generator) <- block.getGenerators) {
      elaboratePending.addNode(ElaborateRecord.Generator(path, generatorFnName),
        generator.dependencies.map { depPath =>
          ElaborateRecord.ParamValue(IndirectDesignPath.fromDesignPath(path) ++ depPath)
        }
      )
    }

    // Queue up sub-trees that need elaboration - needs to be post-generate for generators
    for (blockName <- block.getUnelaboratedBlocks.keys) {
      debug(s"Push block to pending: ${path + blockName}")
      elaboratePending.addNode(ElaborateRecord.Block(path + blockName), Seq())
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
    val libraryPath = parent.getUnelaboratedBlocks(name).asInstanceOf[wir.LibraryElement].target
    debug(s"Elaborate block at $path: ${readableLibraryPath(libraryPath)}")
    val block = new wir.Block(library.getBlock(libraryPath), Seq(libraryPath))

    // Process block
    processBlock(path, block)

    // Link block in parent
    parent.elaborate(name, block)
  }

  protected def processLink(path: DesignPath, link: wir.Link): Unit = {
    import edg.ExprBuilder.{Ref, ValueExpr}
    import edg.ElemBuilder.Constraint
    import collection.SeqMap
    // Elaborate ports, generating equivalence constraints as needed
    elaborateContainedPorts(path, link)
    processParams(path, link)
    for ((name, port) <- link.getElaboratedPorts) {
      setPortConnectedLinkParams(path + name, port, path, link.getParams.keys.toSeq, false)
      processPortConnected(path + name, port)
    }

    // All inner link ports that need to be allocated, with the list of connected ports,
    // as (port array path -> constraint name
    val linkPortAllocates = mutable.HashMap[Seq[String], String]()
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
            if (connectedPorts.contains(path + extPort.head)) {
              connectedPorts += (path ++ intPort)
            }
            directConnectedPorts += (path ++ intPort)
          case (ValueExpr.MapExtract(ValueExpr.Ref(extPortArray), Ref(extPortInner)),
              ValueExpr.RefAllocate(intPortArray)) =>
            require(!linkPortAllocates.contains(intPortArray), s"redefinition of link port array $intPortArray")
            linkPortAllocates.put(intPortArray, constrName)
          case (ValueExpr.RefAllocate(extPortArray), ValueExpr.RefAllocate(intPortArray)) =>
            throw new NotImplementedError("TODO: export port array <-> port array")
          case (ValueExpr.RefAllocate(extPortArray), ValueExpr.Ref(intPort)) =>
            throw new NotImplementedError("TODO: export port array <-> port")
          case (ValueExpr.Ref(extPort), ValueExpr.RefAllocate(intPortArray)) =>
            throw new NotImplementedError("TODO: export port <-> port array")
          case _ => throw new IllegalConstraintException(s"unknown export in link $path: $constrName = $exported")
        }
      case _ => throw new IllegalConstraintException(s"unknown constraint in link $path: $constrName = $constr")
    }}

    // Expand arrays
    linkPortAllocates.foreach { case (linkPortArray, exportConstrName) =>
      link.mapMultiConstraint(exportConstrName) { exportConstr =>
        val ValueExpr.MapExtract(ValueExpr.Ref(extPortArray), Ref(extPortInner)) = exportConstr.getExported.getExteriorPort
        val ValueExpr.RefAllocate(intPortArray) = exportConstr.getExported.getInternalBlockPort

        val arrayElts = constProp.getArrayElts(path ++ extPortArray).get
        constProp.setArrayElts(path ++ intPortArray, arrayElts)

        val expandedExports = arrayElts.map { arrayElt =>
          elaboratePending.addNode(
            ElaborateRecord.Connect(path ++ intPortArray + arrayElt, path ++ extPortArray + arrayElt ++ extPortInner),
            Seq(ElaborateRecord.Link(path),
              ElaborateRecord.Link(path + intPortArray.head),
              ElaborateRecord.ConnectedLink(path ++ intPortArray + arrayElt))
          )
          if (connectedPorts.contains(path + extPortArray.head)) {
            connectedPorts += (path ++ intPortArray)
          }
          directConnectedPorts += (path ++ intPortArray)

          exportConstrName + "." + arrayElt ->
              Constraint.Exported(Ref((extPortArray :+ arrayElt :++ extPortInner): _*),
                Ref((intPortArray :+ arrayElt): _*)
              )
        }
        debug(s"Array defined: ${path ++ intPortArray} = $arrayElts")
        expandedExports
      }
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
    val libraryPath = parent.getUnelaboratedLinks(name).asInstanceOf[wir.LibraryElement].target
    debug(s"Elaborate link at $path: ${readableLibraryPath(libraryPath)}")
    val link = new wir.Link(library.getLink(libraryPath), Seq(libraryPath))

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
    val generatedPb = library.runGenerator(block.getBlockClass, fnName,
      generator.dependencies.map { depPath =>
        depPath -> constProp.getValue(IndirectDesignPath.fromDesignPath(blockPath) ++ depPath).get
      }.toMap
    )
    val generatedDiff = block.dedupGeneratorPb(generatedPb)
    val generatedDiffBlock = new wir.Block(generatedDiff, Seq(block.getBlockClass))
    processBlock(blockPath, generatedDiffBlock)
    block.append(generatedDiffBlock)
  }

  /** Performs full compilation and returns the resulting design. Might take a while.
    */
  def compile(): schema.Design = {
    import edg.ElemBuilder

    // Ports at top break IS_CONNECTED implies CONNECTED_LINK has valid params
    require(root.getElaboratedPorts.isEmpty, "design top may not have ports")

    while (elaboratePending.getReady.nonEmpty) {
      elaboratePending.getReady.foreach {
        case elaborateRecord @ ElaborateRecord.Block(blockPath) =>
          elaborateBlock(blockPath)
          elaboratePending.setValue(elaborateRecord, None)
        case elaborateRecord @ ElaborateRecord.Link(linkPath) =>
          elaborateLink(linkPath)
          elaboratePending.setValue(elaborateRecord, None)
        case elaborateRecord @ ElaborateRecord.Connect(toLinkPortPath, fromLinkPortPath) =>
          elaborateConnect(toLinkPortPath, fromLinkPortPath)
          elaboratePending.setValue(elaborateRecord, None)
        case elaborateRecord @ ElaborateRecord.Generator(blockPath, fnName) =>
          elaborateGenerator(blockPath, fnName)
          elaboratePending.setValue(elaborateRecord, None)
        case elaborateRecord => throw new IllegalArgumentException(s"unknown ready elaboration target $elaborateRecord")
      }
    }

    require(elaboratePending.getMissingBlocking.isEmpty,
      s"failed to elaborate: ${elaboratePending.getMissingBlocking}")
    require(constProp.getUnsolved.isEmpty,
      s"const prop failed to solve: ${constProp.getUnsolved}")

    ElemBuilder.Design(root.toPb)
  }

  def getAllSolved: Map[IndirectDesignPath, ExprValue] = constProp.getAllSolved
}
