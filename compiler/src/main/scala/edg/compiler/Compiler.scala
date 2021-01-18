package edg.compiler

import scala.collection.mutable
import edg.schema.schema
import edg.expr.expr
import edg.wir.{DesignPath, IndirectDesignPath}
import edg.wir
import edg.util.MutableBiMap


class IllegalConstraintException(msg: String) extends Exception(msg)


/** Compiler for a particular design, with an associated library to elaborate references from.
  * TODO also needs a Python interface for generators, somewhere.
  *
  * During the compilation process, internal data structures are mutated.
  */
class Compiler(inputDesignPb: schema.Design, library: edg.wir.Library) {
  // TODO better debug toggle
//  protected def debug(msg: => String): Unit = println(msg)
  protected def debug(msg: => String): Unit = { }

  private val pendingBlocks = mutable.Set[DesignPath]()  // block-likes pending elaboration
  private val pendingLinks = mutable.Set[DesignPath]()  // block-likes pending elaboration

  private val constProp = new ConstProp()
  private val assertions = mutable.Buffer[(DesignPath, String, expr.ValueExpr, SourceLocator)]()  // containing block, name, expr

  // TODO clean up this API?
  private[edg] def getValue(path: IndirectDesignPath): Option[ExprValue] = constProp.getValue(path)

  // Connect statements which have been read but the equivalence constraints have not been generated,
  // in the format (block port -> link port) for connects, or (exterior port -> interior port) for exports.
  // Array ports must be resolved to the element level.
  private val unresolvedConnects = MutableBiMap[DesignPath]()
  // For array points involved in connects, returns all the sub-elements
  private val arrayElements = mutable.HashMap[DesignPath, Seq[String]]()
  // PortArrays (either link side or block side) pending a length, as (port name -> (constraint containing block,
  // constraint name))
  private val pendingLength = mutable.HashMap[DesignPath, (DesignPath, String)]()

  // Seed compilation with the root
  //
  private val root = new wir.Block(inputDesignPb.contents.get, inputDesignPb.contents.get.superclasses)
  def resolveBlock(path: DesignPath): wir.Block = root.resolve(path.steps).asInstanceOf[wir.Block]
  def resolveLink(path: DesignPath): wir.Link = root.resolve(path.steps).asInstanceOf[wir.Link]

  processBlock(DesignPath.root, root)

  protected def processParams(path: DesignPath, hasParams: wir.HasParams): Unit = {
    for ((paramName, param) <- hasParams.getParams) {
      constProp.addDeclaration(path + paramName, param)
    }
  }

  protected def generateConnectedEquivalence(container1: IndirectDesignPath, container2: IndirectDesignPath,
                                   hasParams: wir.HasParams): Unit = {
    for ((paramName, param) <- hasParams.getParams) {
      constProp.addEquality(container1 + paramName, container2 + paramName)
    }
  }

  protected def processPort(path: DesignPath, port: wir.PortLike): Unit = port match {
    // TODO better semantics and consistency between this and processBlock/processLink
    // Unlike those, this is called with the final port object (after LibraryElements replaced).
    // Main issue is that PortArray doesn't have a meaningful elaborate(), instead using bulk setPorts
    case port: wir.Port =>
      processParams(path, port)
      unresolvedConnects.get(path) match {
        case Some(connectedPath) =>
          generateConnectedEquivalence(IndirectDesignPath.fromDesignPath(path),
            IndirectDesignPath.fromDesignPath(connectedPath),
            port)
          unresolvedConnects.remove(path).get
        case None =>  // ignored
      }
    case port: wir.PortArray =>
      val libraryPath = port.getType
      debug(s"Elaborate PortArray at ${path}: $libraryPath")
      // TODO can / should this share the LibraryElement instantiation logic w/ elaborateBlocklikePorts?
      val newPorts = arrayElements(path).map { index =>
        index -> wir.PortLike.fromIrPort(library.getPort(libraryPath), libraryPath)
      }.toMap
      port.setPorts(newPorts)  // the PortArray is elaborated in-place instead of needing a new object
      newPorts.foreach { case (index, subport) =>
        processPort(path + index, subport)
      }
    case port => throw new NotImplementedError(s"unknown unelaborated port $port")
  }

  protected def elaborateBlocklikePorts(path: DesignPath, hasPorts: wir.HasMutablePorts): Unit = {
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
    elaborateBlocklikePorts(path, block)
    processParams(path, block)

    // Process constraints:
    // - for connected constraints, add into the connectivity map
    // - for assignment constraints, add into const prop
    // - for other constraints, add into asserts list
    // TODO ensure constraint processing order?
    // All ports that need to be allocated, with the list of connected ports,
    // as (port array path -> list(constraint name, block port))
    val linkPortAllocates = mutable.HashMap[DesignPath, mutable.ListBuffer[(String, DesignPath)]]()
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
            linkPortAllocates.getOrElseUpdate(path ++ linkPortArray, mutable.ListBuffer()) += ((constrName, path ++ blockPort))
          case (blockPort, linkPort) =>
            unresolvedConnects.put(path ++ blockPort, path ++ linkPort)
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
            unresolvedConnects.put(path ++ extPort, path ++ intPort)
        }
      case _ => throw new IllegalConstraintException(s"unknown constraint in block $path: $constrName = $constr")
    }}

    // For fully resolved arrays, allocate port numbers and set array elements
    linkPortAllocates.foreach { case (linkPortArray, blockConstrPorts) =>
      val linkPortArrayElts = blockConstrPorts.zipWithIndex.map { case ((constrName, blockPort), index) =>
        unresolvedConnects.put(blockPort, linkPortArray + index.toString)
        block.mapConstraint(constrName) { constr =>
          val steps = constr.expr.connected.get.linkPort.get.expr.ref.get.steps
          require(steps.last == Ref.AllocateStep)
          val indexStep = ref.LocalStep(step=ref.LocalStep.Step.Name(index.toString))
          constr.update(
            _.connected.linkPort.ref.steps := steps.slice(0, steps.length - 1) :+ indexStep
          )
        }
        index.toString
      }
      require(!arrayElements.isDefinedAt(linkPortArray), s"redefinition of link array elements at $linkPortArray")
      arrayElements.put(linkPortArray, linkPortArrayElts.toSeq)
    }

    // Process assignment constraints

    // Queue up generators as needed

    // Queue up sub-trees that need elaboration - needs to be post-generate for generators
    for (blockName <- block.getUnelaboratedBlocks.keys) {
      debug(s"Push block to pending: ${path + blockName}")
      pendingBlocks += path + blockName
    }
    for (linkName <- block.getUnelaboratedLinks.keys) {
      debug(s"Push link to pending: ${path + linkName}")
      pendingLinks += path + linkName
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
  }

  protected def processLink(path: DesignPath, link: wir.Link): Unit = {
    import edg.ExprBuilder.Ref
    // Elaborate ports, generating equivalence constraints as needed
    elaborateBlocklikePorts(path, link)
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
            unresolvedConnects.put(path ++ extPort, path ++ intPort)
        }
      case _ => throw new IllegalConstraintException(s"unknown constraint in link $path: $constrName = $constr")
    }}

    // Queue up sub-trees that need elaboration - needs to be post-generate for generators
    for (linkName <- link.getUnelaboratedLinks.keys) {
      debug(s"Push link to pending: ${path + linkName}")
      pendingLinks += path + linkName
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
  }

  /** Performs full compilation and returns the resulting design. Might take a while.
    */
  def compile(): schema.Design = {
    import edg.ElemBuilder
    while (pendingBlocks.nonEmpty || pendingLinks.nonEmpty) {
      if (pendingBlocks.nonEmpty) {
        val nextPath = pendingBlocks.head
        pendingBlocks.subtractOne(nextPath)
        debug(s"Pick block to elaborate: $nextPath")
        elaborateBlock(nextPath)
      } else if (pendingLinks.nonEmpty) {
        val nextPath = pendingLinks.head
        pendingLinks.subtractOne(nextPath)
        debug(s"Pick link to elaborate: $nextPath")
        elaborateLink(nextPath)
      }
    }
    ElemBuilder.Design(root.toPb)
  }
}
