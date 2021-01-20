package edg.compiler

import scala.collection.mutable
import edg.schema.schema
import edg.expr.expr
import edg.wir.{DesignPath, IndirectDesignPath, IndirectStep}
import edg.wir
import edg.util.DependencyGraph


class IllegalConstraintException(msg: String) extends Exception(msg)


trait ConnectPropRecord
object ConnectPropRecord {
  case class Block(path: DesignPath) extends ConnectPropRecord  // set once block elaborated
  case class Link(path: DesignPath) extends ConnectPropRecord  // set once link elaborated
  case class Connect(blockPortPath: DesignPath, linkPortPath: DesignPath,
                     linkPath: DesignPath) extends ConnectPropRecord  // as dependency target, set once elaborated
  case class Export(extPortPath: DesignPath, intPortPath: DesignPath) extends ConnectPropRecord  // as dependency target, set once elaborated
}

trait ElaborateRecord
object ElaborateRecord {
  case class Block(blockPath: DesignPath) extends ElaborateRecord
  case class Link(linkPath: DesignPath) extends ElaborateRecord
  case class Param(paramPath: IndirectDesignPath) extends ElaborateRecord
}


/** Compiler for a particular design, with an associated library to elaborate references from.
  * TODO also needs a Python interface for generators, somewhere.
  *
  * During the compilation process, internal data structures are mutated.
  */
class Compiler(inputDesignPb: schema.Design, library: edg.wir.Library) {
  // TODO better debug toggle
//  protected def debug(msg: => String): Unit = println(msg)
  protected def debug(msg: => String): Unit = { }

  private val elaboratePending = DependencyGraph[ElaborateRecord, None.type]()

  private val constProp = new ConstProp()
  private val assertions = mutable.Buffer[(DesignPath, String, expr.ValueExpr, SourceLocator)]()  // containing block, name, expr

  // TODO clean up this API?
  private[edg] def getValue(path: IndirectDesignPath): Option[ExprValue] = constProp.getValue(path)

  // Dependency graph for generating the equivalence constraints between parameters, as well as CONNECTED_LINK.
  // This triggers once both the block and links (or exterior block and interior block, for exports)
  // have been elaborated, as a simultaneous traversal on the ports on both sides.
  private val connectPropDependencies = DependencyGraph[ConnectPropRecord, None.type]()

  protected def generateConnected(port1Path: DesignPath, port1: wir.PortLike,
                                  port2Path: DesignPath, port2: wir.PortLike): Unit = {
    (port1, port2) match {
      case (port1: wir.Port, port2: wir.Port) =>
        require(port1.getParams.keys == port2.getParams.keys,
          s"connected ports at $port1Path, $port2Path with different params")
        for (paramName <- port1.getParams.keys) {
          constProp.addEquality(
            IndirectDesignPath.fromDesignPath(port1Path) + paramName,
            IndirectDesignPath.fromDesignPath(port2Path) + paramName
          )
        }
      case (port1, port2) => throw new IllegalArgumentException(s"can't connect ports $port1, $port2")
    }
  }

  protected def updateConnectPropDependencies(): Unit = {
    connectPropDependencies.getReady.foreach {
      case connectRecord @ ConnectPropRecord.Connect(blockPortPath, linkPortPath, linkPath) =>
        debug(s"Generate connect equalities for $blockPortPath, $linkPortPath")
        // Generate CONNECTED_LINK equalities
        val link = resolveLink(linkPath)
        for (paramName <- link.getParams.keys) {
          constProp.addEquality(
            IndirectDesignPath.fromDesignPath(linkPath) + paramName,
            IndirectDesignPath.fromDesignPath(blockPortPath) + IndirectStep.ConnectedLink() + paramName
          )
        }
        // Generated port parameter equalities
        val blockPort = resolvePort(blockPortPath)
        val linkPort = resolvePort(linkPortPath)
        generateConnected(blockPortPath, blockPort, linkPortPath, linkPort)
        // Mark as completed
        connectPropDependencies.setValue(connectRecord, None)
      case connectRecord @ ConnectPropRecord.Export(extPortPath, intPortPath) =>
        debug(s"Generate export equalities for $extPortPath, $intPortPath")
        val extPort = resolvePort(extPortPath)
        val intPort = resolvePort(intPortPath)
        generateConnected(extPortPath, extPort, intPortPath, intPort)
        // Mark as completed
        connectPropDependencies.setValue(connectRecord, None)
    }
    require(connectPropDependencies.getReady.isEmpty)
  }

  // Seed compilation with the root
  //
  private val root = new wir.Block(inputDesignPb.contents.get, inputDesignPb.contents.get.superclasses)
  def resolveBlock(path: DesignPath): wir.Block = root.resolve(path.steps).asInstanceOf[wir.Block]
  def resolveLink(path: DesignPath): wir.Link = root.resolve(path.steps).asInstanceOf[wir.Link]
  def resolvePort(path: DesignPath): wir.PortLike = root.resolve(path.steps).asInstanceOf[wir.PortLike]

  processBlock(DesignPath.root, root)

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
      elaborateContainedPorts(path, port)
    case port: wir.PortArray =>
      val libraryPath = port.getType
      debug(s"Elaborate PortArray at $path: $libraryPath")
      // TODO can / should this share the LibraryElement instantiation logic w/ elaborate BlocklikePorts?
      val newPorts = constProp.getArrayElts(path).get.map { index =>
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
        debug(s"Elaborate Port at ${path + portName}: $libraryPath")
        val newPort = wir.PortLike.fromIrPort(library.getPort(libraryPath), libraryPath)
        hasPorts.elaborate(portName, newPort)
        processPort(path + portName, newPort)
      case port: wir.PortArray =>
        processPort(path + portName, port)
      case port => throw new NotImplementedError(s"unknown unelaborated port $port")
    }}
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
  }

  protected def processBlock(path: DesignPath, block: wir.Block): Unit = {
    import edg.ExprBuilder.Ref
    import edg.ref.ref

    // Elaborate ports, generating equivalence constraints as needed
    elaborateContainedPorts(path, block)
    processParams(path, block)

    // Process constraints:
    // - for connected constraints, add into the connectivity map
    // - for assignment constraints, add into const prop
    // - for other constraints, add into asserts list
    // TODO ensure constraint processing order?
    // All ports that need to be allocated, with the list of connected ports,
    // as (port array path -> list(constraint name, block port))
    val linkPortAllocates = mutable.HashMap[ref.LocalPath, mutable.ListBuffer[(String, ref.LocalPath)]]()
    block.getConstraints.foreach { case (constrName, constr) => constr.expr match {
      case expr if processBlocklikeConstraint.isDefinedAt(path, constrName, constr, expr) =>
        processBlocklikeConstraint(path, constrName, constr, expr)
      case expr.ValueExpr.Expr.Connected(connected) =>
        (connected.blockPort.get.expr.ref.get, connected.linkPort.get.expr.ref.get) match {
          case (Ref.Allocate(blockPortArray), Ref.Allocate(linkPortArray)) =>
            throw new NotImplementedError("TODO: block port array <-> link port array")
          case (Ref.Allocate(blockPortArray), linkPort) =>
            throw new NotImplementedError("TODO: block port array <-> link port")
          case (blockPort, Ref.Allocate(linkPortArray)) =>
            linkPortAllocates.getOrElseUpdate(linkPortArray, mutable.ListBuffer()) += ((constrName, blockPort))
          case (blockPort, linkPort) =>
            connectPropDependencies.addNode(
              ConnectPropRecord.Connect(path ++ blockPort, path ++ linkPort,
                path + linkPort.steps.head.step.name.get),
              Seq(ConnectPropRecord.Block(path + blockPort.steps.head.step.name.get),
                ConnectPropRecord.Link(path + linkPort.steps.head.step.name.get))
            )
        }
      case expr.ValueExpr.Expr.Exported(exported) =>
        (exported.exteriorPort.get.expr.ref.get, exported.internalBlockPort.get.expr.ref.get) match {
          case (Ref.Allocate(extPortArray), Ref.Allocate(intPortArray)) =>
            throw new NotImplementedError("TODO: export port array <-> port array")
          case (Ref.Allocate(extPortArray), intPort) =>
            throw new NotImplementedError("TODO: export port array <-> port")
          case (extPort, Ref.Allocate(intPortArray)) =>
            throw new NotImplementedError("TODO: export port <-> port array")
          case (extPort, intPort) =>
            connectPropDependencies.addNode(
              ConnectPropRecord.Export(path ++ extPort, path ++ intPort),
              Seq(ConnectPropRecord.Block(path),
                ConnectPropRecord.Block(path + intPort.steps.head.step.name.get))
            )
        }
      case _ => throw new IllegalConstraintException(s"unknown constraint in block $path: $constrName = $constr")
    }}

    // For fully resolved arrays, allocate port numbers and set array elements
    linkPortAllocates.foreach { case (linkPortArray, blockConstrPorts) =>
      val linkPortArrayElts = blockConstrPorts.zipWithIndex.map { case ((constrName, blockPort), index) =>
        connectPropDependencies.addNode(
          ConnectPropRecord.Connect(path ++ blockPort, path ++ linkPortArray + index.toString,
            path + linkPortArray.steps.head.step.name.get),
          Seq(ConnectPropRecord.Block(path + blockPort.steps.head.step.name.get),
            ConnectPropRecord.Link(path + linkPortArray.steps.head.step.name.get))
        )
        block.mapConstraint(constrName) { constr =>
          val steps = constr.expr.connected.get.linkPort.get.expr.ref.get.steps
          require(steps.last == Ref.AllocateStep)
          val indexStep = ref.LocalStep(step=ref.LocalStep.Step.Name(index.toString))
          constr.update(
            _.connected.linkPort.ref.steps := steps.slice(0, steps.length - 1) :+ indexStep
          )
        }
        index.toString
      }.toSeq
      constProp.setArrayElts(path ++ linkPortArray, linkPortArrayElts)
    }

    // Process assignment constraints

    // Queue up generators as needed

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
    debug(s"Elaborate block at $path: $libraryPath")
    val block = new wir.Block(library.getBlock(libraryPath), Seq(libraryPath))

    // Process block
    processBlock(path, block)

    // Link block in parent
    parent.elaborate(name, block)

    // Mark this as ready for dependent actions
    connectPropDependencies.setValue(ConnectPropRecord.Block(path), None)
    updateConnectPropDependencies()
  }

  protected def processLink(path: DesignPath, link: wir.Link): Unit = {
    import edg.ExprBuilder.Ref
    // Elaborate ports, generating equivalence constraints as needed
    elaborateContainedPorts(path, link)
    processParams(path, link)

    // Process constraints, as in the block case
    link.getConstraints.foreach { case (constrName, constr) => constr.expr match {
      case expr if processBlocklikeConstraint.isDefinedAt(path, constrName, constr, expr) =>
        processBlocklikeConstraint(path, constrName, constr, expr)
      case expr.ValueExpr.Expr.Exported(exported) =>
        (exported.exteriorPort.get.expr.ref.get, exported.internalBlockPort.get.expr.ref.get) match {
          case (Ref.Allocate(extPortArray), Ref.Allocate(intPortArray)) =>
            throw new NotImplementedError("TODO: export port array <-> port array")
          case (Ref.Allocate(extPortArray), intPort) =>
            throw new NotImplementedError("TODO: export port array <-> port")
          case (extPort, Ref.Allocate(intPortArray)) =>
            throw new NotImplementedError("TODO: export port <-> port array")
          case (extPort, intPort) =>
            connectPropDependencies.addNode(
              ConnectPropRecord.Export(path ++ extPort, path ++ intPort),
              Seq(ConnectPropRecord.Link(path),
                ConnectPropRecord.Link(path + intPort.steps.head.step.name.get))
            )
        }
      case _ => throw new IllegalConstraintException(s"unknown constraint in link $path: $constrName = $constr")
    }}

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
    val parent = resolveBlock(parentPath)  // TODO what if this is a link?
    val libraryPath = parent.getUnelaboratedLinks(name).asInstanceOf[wir.LibraryElement].target
    debug(s"Elaborate link at $path: $libraryPath")
    val link = new wir.Link(library.getLink(libraryPath), Seq(libraryPath))

    // Process block
    processLink(path, link)

    // Link block in parent
    parent.elaborate(name, link)

    // Mark this as ready for dependent actions
    connectPropDependencies.setValue(ConnectPropRecord.Link(path), None)
    updateConnectPropDependencies()
  }

  /** Performs full compilation and returns the resulting design. Might take a while.
    */
  def compile(): schema.Design = {
    import edg.ElemBuilder
    while (elaboratePending.getReady.nonEmpty) {
      elaboratePending.getReady.foreach {
        case elaborateRecord @ ElaborateRecord.Block(blockPath) => elaborateBlock(blockPath)
          elaboratePending.setValue(elaborateRecord, None)
        case elaborateRecord @ ElaborateRecord.Link(linkPath) => elaborateLink(linkPath)
          elaboratePending.setValue(elaborateRecord, None)
      }
    }

    require(elaboratePending.getMissing.isEmpty,
      s"failed to elaborate: ${elaboratePending.getMissing}")
    require(connectPropDependencies.getMissing.isEmpty,
      s"connects failed to generate: ${connectPropDependencies.getMissing}")
    require(constProp.getUnsolved.isEmpty,
      s"const prop failed to solve: ${constProp.getUnsolved}")

    ElemBuilder.Design(root.toPb)
  }
}
