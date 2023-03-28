package edg.compiler

import edg.EdgirUtils._
import edg.util.{DependencyGraph, Errorable, SingleWriteHashMap}
import edg.wir.ProtoUtil._
import edg.wir._
import edg.{ExprBuilder, wir}
import edgir.expr.expr
import edgir.ref.ref
import edgir.init.init
import edgir.schema.schema

import scala.collection.{SeqMap, mutable}


sealed trait ElaborateRecord
object ElaborateRecord {
  sealed trait ElaborateTask extends ElaborateRecord  // an elaboration task that can be run
  sealed trait ElaborateDependency extends ElaborateRecord  // an elaboration dependency source

  // step 1/2 for blocks: replaces library reference blocks with the concrete block from the library
  case class ExpandBlock(blockPath: DesignPath, blockClass: ref.LibraryPath) extends ElaborateTask
  // step 2/2 for blocks, when generators are ready: processes the subtree (including connects and assigns)
  case class Block(blockPath: DesignPath) extends ElaborateTask
  case class Link(linkPath: DesignPath) extends ElaborateTask
  case class LinkArray(linkPath: DesignPath) extends ElaborateTask

  // Defines the type of a parameter, may be held back by partial compilation rules
  case class Parameter(containerPath: DesignPath, blockClass: Option[ref.LibraryPath], postfix: ref.LocalPath,
                       param: init.ValInit) extends ElaborateTask

  // Connection to be elaborated, to set port parameter, IS_CONNECTED, and CONNECTED_LINK equivalences.
  // Only elaborates the direct connect, and for bundles, creates sub-Connect tasks since it needs
  // connectedLink and linkParams.
  case class Connect(toLinkPortPath: DesignPath, toBlockPortPath: DesignPath, root: DesignPath)
      extends ElaborateTask

  // Elaborates the contents of a port array, based on the port array's ELEMENTS parameter.
  // For recursive arrays, (eg, in link arrays), this is set when recursively elaborated.
  // Only called for port arrays without defined elements (so excluding blocks that define their ports, including
  // generator-defined port arrays which are structurally similar).
  // Created but never run for abstract blocks with abstract port array.
  case class ElaboratePortArray(path: DesignPath) extends ElaborateTask

  case class Port(path: DesignPath) extends ElaborateDependency  // when expanded

  case class ParamValue(paramPath: IndirectDesignPath) extends ElaborateDependency  // when solved

  // The next tasks are a series for array connection

  // This assigns a link's elements from the first ELEMENTS defined, then asserts subsequent ELEMENTS are equal.
  // Requires: source param is defined.
  case class AssignLinkElements(target: IndirectDesignPath, source: IndirectDesignPath, containerPath: DesignPath)
      extends ElaborateTask

  // Expands ArrayConnect and ArrayExport connections to individual Connect and Export operations.
  // ALLOCATEs are preserved as-is, meaning those will be allocated on an individual (instead of array) basis.
  // Requires: port's ELEMENTS defined.
  case class ExpandArrayConnections(parent: DesignPath, constraintName: String)
      extends ElaborateTask with ElaborateDependency

  // Once lowered to single connects, rewrites constraints to replace the ALLOCATE with a concrete port name,
  // allocated from the port's ELEMENTS.
  // Requires: array-connections expanded, port's ELEMENTS defined.
  case class RewriteConnectAllocate(parent: DesignPath, portPath: Seq[String], constraintNames: Seq[String],
                                    arrayConstraintNames: Seq[String], portIsLink: Boolean)
      extends ElaborateTask with ElaborateDependency

  // Sets a PortArray's IS_CONNECTED based off all the connected constraints.
  // Requires: array-connections expanded, ALLOCATE replaced with concrete indices
  case class ResolveArrayIsConnected(parent: DesignPath, portPath: Seq[String], constraintNames: Seq[String],
                                     arrayConstraintNames: Seq[String], portIsLink: Boolean)
      extends ElaborateTask
}


/** Configuration for partial compilation, where the compiler intentionally leaves some design subtree
  * unelaboated, eg as a template for design space exploration.
  */
case class PartialCompile(
  blocks: Seq[DesignPath] = Seq(),  // do not elaborate these blocks
  params: Seq[DesignPath] = Seq(),  // do not propagate values into these params (assignments are discarded)
  classes: Seq[ref.LibraryPath] = Seq(),  // do not elaborate blocks of these classes
  classParams: Seq[(ref.LibraryPath, ref.LocalPath)] = Seq()  // do not propagate values into params of these classes
) {
  def ++(that: PartialCompile): PartialCompile = {  // concatenates two partial compilation rules
    PartialCompile(blocks ++ that.blocks, params ++ that.params,
      classes ++ that.classes, classParams ++ that.classParams)
  }

  def isEmpty = blocks.isEmpty && params.isEmpty && classes.isEmpty && classParams.isEmpty
}


// Utility class that provides a namespace for suggestedName, including a shared default naming pool for where
// suggestedName is not haven.
class AssignNamer() {
  val freeIndices = LazyList.from(0).iterator

  def name(suggestedName: Option[String]): String = suggestedName match {
    case Some(suggestedName) => suggestedName
    case None => freeIndices.next().toString
  }
}


/** Compiler for a particular design, with an associated library to elaborate references from.
  *
  * During the compilation process, internal data structures are mutated.
  *
  * Port parameters are propagated by expanding connect and export statements between connected ports
  * into equalities between all contained parameters.
  * This expansion triggers when the link-side port is fully elaborated, as its parameters are used.
  * CONNECTED_LINK is a symlink that is resolved by ConstProp.
  */
class Compiler private (inputDesignPb: schema.Design, val library: edg.wir.Library,
                        val refinements: Refinements, val partial: PartialCompile,
                        initialize: Boolean) {
  // public constructor that does not expose init, which is internal only
  def this(inputDesignPb: schema.Design, library: edg.wir.Library,
           refinements: Refinements = Refinements(), partial: PartialCompile = PartialCompile()) = {
    this(inputDesignPb, library, refinements, partial, true)
  }

  // Working design tree data structure
  private var root = new wir.Block(inputDesignPb.getContents, None)  // TODO refactor to unify root / non-root cases
  require(root.getPorts.isEmpty, "design top may not have ports")  // also don't need to elaborate top ports

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

  if (initialize) {  // seed only on the initial object creation (and not forks, which would duplicate work)
    for ((path, value) <- refinements.instanceValues) { // seed const prop with path assertions
      constProp.addAssignValue(path.asIndirect, value, DesignPath(), "path refinement", forced=true)
    }
    for ((path, source) <- refinements.instanceAssigns) {
      constProp.addAssignEqual(path.asIndirect, source.asIndirect, DesignPath(), "path refinement", forced=true)
    }

    elaboratePending.addNode(ElaborateRecord.Block(DesignPath()), Seq()) // seed with root

    // this is done inside expandBlock which isn't called for the root
    constProp.addAssignValue(IndirectDesignPath() + IndirectStep.Name, TextValue(""),
      DesignPath(), "name")
    processParamDeclarations(DesignPath(), Some(root.getBlockClass), root)
  }

  // Some pre-processed data structures to make refinement processing more efficient
  private val refinementClassValuesByClass = refinements.classValues.groupBy(_._1._1)
  private val refinementInstanceValuePaths = (refinements.instanceValues.keys ++ refinements.instanceAssigns.keys).toSet

  def filterRefinementClassValues(blockClass: ref.LibraryPath,
                                  classValuesByClass: Map[ref.LibraryPath, Map[(ref.LibraryPath, ref.LocalPath), ExprValue]],
                                 ): Seq[((ref.LibraryPath, ref.LocalPath), ExprValue)] = {
    classValuesByClass.collect {
      case (refinementClass, refinementClassValues) if library.blockIsSubclassOf(blockClass, refinementClass) =>
        refinementClassValues
    }.flatten.toSeq
  }

  // Supplemental elaboration data structures
  private val expandedArrayConnectConstraints = SingleWriteHashMap[DesignPath, Seq[String]]()  // constraint path -> new constraint names

  // TODO this should get moved into the design tree
  private val errors = mutable.ListBuffer[CompilerError]()

  // Creates a new copy of this compiler including all the work done already.
  // Useful for design space exploration, where the non-search portions of the design have been compiled.
  def fork(additionalRefinements: Refinements = Refinements(), partial: PartialCompile = PartialCompile()): Compiler = {
    val cloned = new Compiler(inputDesignPb, library, refinements ++ additionalRefinements, partial, initialize=false)
    cloned.root = root.cloned
    cloned.elaboratePending.initFrom(elaboratePending)
    cloned.constProp.initFrom(constProp)
    additionalRefinements.instanceValues.foreach { case (path, value) =>
      cloned.constProp.addAssignValue(path.asIndirect, value, DesignPath(), "path refinement", forced=true)
    }
    val additionalRefinementClassValuesByClass = additionalRefinements.classValues.groupBy(_._1._1)
    def processBlockAdditionalRefinements(path: DesignPath, block: Block): Unit = {
      additionalRefinements.classRefinements.foreach { case (refinementClass, _) =>
        require(!block.unrefinedType.contains(refinementClass), f"added class refinement changes class at $path")
      }

      filterRefinementClassValues(block.getBlockClass, additionalRefinementClassValuesByClass).foreach {
        case ((refinementClass, postfix), value) =>
          val paramPath = path ++ postfix
          if (!cloned.refinementInstanceValuePaths.contains(paramPath)) { // instance values supersede class values
            cloned.constProp.addAssignValue(path.asIndirect ++ postfix, value, DesignPath(),
              s"${refinementClass.toSimpleString} class refinement", forced=true)
          }
      }

      block.getBlocks foreach {  // recurse
        case (subblockName, subblock: Block) => processBlockAdditionalRefinements(path + subblockName, subblock)
        case (subblockName, subblock: BlockLibrary) =>  // ignored
      }
    }
    processBlockAdditionalRefinements(DesignPath(), cloned.root)
    require(cloned.expandedArrayConnectConstraints.isEmpty)
    cloned.expandedArrayConnectConstraints.addAll(expandedArrayConnectConstraints)
    require(cloned.errors.isEmpty)
    cloned.errors.addAll(errors)
    cloned
  }

  // Add solved values, where the param must not have had a value
  def addAssignValues(values: Map[DesignPath, ExprValue], name: String): Unit = {
    values.foreach { case (path, value) =>
      constProp.addAssignValue(path.asIndirect, value, DesignPath(), name)
    }
  }

  // Returns all errors, by scanning the design tree for errors and adding errors accumulated through the compile
  // process
  def getErrors(): Seq[CompilerError] = {
    val pendingErrors = elaboratePending.getMissingValue.map { missingNode =>
      CompilerError.Unelaborated(missingNode, elaboratePending.nodeMissing(missingNode))
    }.toSeq

    errors.toSeq ++ constProp.getErrors ++ pendingErrors
  }

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
    val connectedParam = toLinkPort.getParams.keys.map(IndirectStep.Element(_))
    for (connectedStep <- connectedParam) { // note: can't happen for top level connect!
      constProp.addAssignEqual(
        connect.toLinkPortPath.asIndirect + connectedStep,
        connect.toBlockPortPath.asIndirect + connectedStep,
        connect.root, "connect"
      )
    }

    // Add sub-ports to the elaboration dependency graph, as appropriate
    toLinkPort match {
      case toLinkPort: wir.Bundle =>
        for (portName <- toLinkPort.getPorts.keys) {
          elaboratePending.addNode(
            ElaborateRecord.Connect(connect.toLinkPortPath + portName, connect.toBlockPortPath + portName,
              connect.root),
            Seq()
          )
          constProp.setConnection(connect.toLinkPortPath + portName, connect.toBlockPortPath + portName)
        }
      case toLinkPort => // everything else ignored
    }
  }

  protected def resolvePortConnectivity(containerPath: DesignPath, portPostfix: Seq[String],
                                        constraint: Option[(String, expr.ValueExpr)]): Unit = {
    val container = resolve(containerPath).asInstanceOf[wir.HasMutableConstraints]  // block or link
    val constraintExpr = constraint.map { case (constrName, constr) => (constrName, constr.expr) }

    // Returns the topmost port for some port path that may be an inner port of a bundle.
    // Returns array components (but never the array itself), but does not return bundle components.
    // This should only be used for exports, on the outer port, which must have been fully elaborated.
    def exteriorTopPort(blockPath: DesignPath, portPostfix: Seq[String]): DesignPath = {
      // Returns the deepest applicable postfix, starting from a port
      def resolveRecursive(portPath: DesignPath, port: wir.PortLike, postfix: Seq[String]): Seq[String] = {
        port match {
          case _: wir.Port | _: wir.Bundle | _: wir.PortLibrary =>  // don't recurse into these
            // note that libraries in arrays may not yet have been elaborated
            Seq()
          case port: wir.PortArray =>
            Seq(postfix.head) ++ resolveRecursive(portPath + postfix.head, port.getPorts(postfix.head), postfix.tail)
        }
      }
      val blockLike = resolve(blockPath).asInstanceOf[wir.HasMutablePorts]
      containerPath + portPostfix.head ++ resolveRecursive(blockPath + portPostfix.head, blockLike.getPorts(portPostfix.head), portPostfix.tail)
    }

    constraintExpr match {
      case Some((constrName, expr.ValueExpr.Expr.Connected(connected))) =>
        require(container.isInstanceOf[wir.Block])
        constProp.addAssignValue(containerPath.asIndirect ++ portPostfix + IndirectStep.IsConnected,
          BooleanValue(true), containerPath, s"$containerPath.$constrName")
      case Some((constrName, expr.ValueExpr.Expr.Exported(exported))) =>
        val exportedToTop = exteriorTopPort(containerPath, exported.getExteriorPort.getRef.steps.map(_.getName))
        constProp.addAssignEqual(
          containerPath.asIndirect ++ portPostfix + IndirectStep.IsConnected,
          exportedToTop.asIndirect + IndirectStep.IsConnected,
          containerPath, s"$containerPath.$constrName")
      case Some((constrName, expr.ValueExpr.Expr.ExportedTunnel(exported))) =>  // same as exported case
        // Since the exterior port refers to a child block of the current container,
        // it would not have been elaborated yet so we cannot inspect into it.
        // This relies on tunnel exports being simple (port to port, not port to inner port).
        constProp.addAssignEqual(
          containerPath.asIndirect ++ portPostfix + IndirectStep.IsConnected,
          containerPath.asIndirect ++ exported.getExteriorPort.getRef + IndirectStep.IsConnected,
          containerPath, s"$containerPath.$constrName")
      case None =>
        constProp.addAssignValue(containerPath.asIndirect ++ portPostfix + IndirectStep.IsConnected,
          BooleanValue(false), containerPath, s"${containerPath ++ portPostfix}.(not connected)")

      case Some((_, _)) => throw new IllegalArgumentException
    }
  }

  protected def paramMatchesPartial(containerPath: DesignPath, blockClass: Option[ref.LibraryPath],
                                    postfix: ref.LocalPath): Boolean = {
    if (partial.params.contains(containerPath ++ postfix)) {
      return true
    }
    blockClass match {
      case Some(blockClass) =>
        partial.classParams.exists { case (partialClass, partialPostfix) =>
          library.blockIsSubclassOf(blockClass, partialClass) && partialPostfix == postfix
        }
      case None => false
    }
  }

  // Called for each param declaration, currently just registers the declaration and type signature.
  protected def processParamDeclarations(root: DesignPath, blockClass: Option[ref.LibraryPath], hasParams: wir.HasParams): Unit = {
    for ((paramName, param) <- hasParams.getParams) {
      val postfix = ExprBuilder.Ref(paramName)
      if (paramMatchesPartial(root, blockClass, postfix)) {
        elaboratePending.addNode(ElaborateRecord.Parameter(root, blockClass, postfix, param), Seq())
      } else {
        // uniformly using ElaborateRecord craters performance, so this fast path is added here
        constProp.addDeclaration(root ++ postfix, param)
      }
    }
  }

  // Elaborates the port, mutating it in-place. Recursive.
  protected def elaboratePort(path: DesignPath, containerPath: DesignPath,
                              container: wir.HasMutablePorts, port: wir.PortLike): Unit = {
    // Instantiate as needed
    val instantiated = port match {
      case port: wir.PortLibrary =>
        val libraryPath = port.target

        val portPb = library.getPort(libraryPath) match {
          case Errorable.Success(portPb) => portPb
          case Errorable.Error(err) =>
            import edg.IrPort
            import edgir.elem.elem
            errors += CompilerError.LibraryError(path, libraryPath, err)
            IrPort.Port(elem.Port())
        }
        val newPort = wir.PortLike.fromIrPort(portPb)
        container.elaborate(path.lastString, newPort)
        newPort
      case port: wir.PortArray => port  // no instantiation needed
      case port => throw new NotImplementedError(s"unknown unelaborated port $port")
    }
    elaboratePending.setValue(ElaborateRecord.Port(path), None)

    // Process and recurse as needed
    instantiated match {
      case port: wir.Port =>
        constProp.addAssignValue(path.asIndirect + IndirectStep.Name, TextValue(path.toString),
          containerPath, "name")
        processParamDeclarations(path, None, port)
      case port: wir.Bundle =>
        constProp.addAssignValue(path.asIndirect + IndirectStep.Name, TextValue(path.toString),
          containerPath, "name")
        processParamDeclarations(path, None, port)
        for ((childPortName, childPort) <- port.getPorts) {
          elaboratePort(path + childPortName, containerPath, port, childPort)
        }
      case port: wir.PortArray =>
        if (port.portsSet) {  // set ELEMENTS if ports is defined by array, otherwise ports are dependent on ELEMENTS
          constProp.addAssignValue(path.asIndirect + IndirectStep.Elements,
            ArrayValue(port.getPorts.keys.toSeq.map(TextValue(_))),
            containerPath, "block-defined elements")
        }
        elaboratePending.addNode(ElaborateRecord.ElaboratePortArray(path), Seq(  // does recursive elaboration + LENGTH
          ElaborateRecord.ParamValue(path.asIndirect + IndirectStep.Elements)
        ))
      case port => throw new NotImplementedError(s"unknown instantiated port $port")
    }
  }

  // Attempts to process a parameter constraint, returning true if it is a matching constraint
  def processAssignConstraint(blockPath: DesignPath, constrName: String, constr: expr.ValueExpr,
                              constrValue: expr.ValueExpr): Boolean = constrValue.expr match {
    case expr.ValueExpr.Expr.Assign(assign) =>
      constProp.addAssignExpr(
        blockPath.asIndirect ++ assign.dst.get,
        assign.src.get, blockPath, constrName)
      true
    case expr.ValueExpr.Expr.AssignTunnel(assign) =>
      // same as normal assign case, but would not enforce locality of references
      constProp.addAssignExpr(
        blockPath.asIndirect ++ assign.dst.get,
        assign.src.get, blockPath, constrName)
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
            ElaborateRecord.Connect(blockPath ++ linkPort, blockPath ++ blockPort, blockPath),
            Seq(ElaborateRecord.Port(blockPath ++ linkPort))
          )
          constProp.setConnection(blockPath ++ linkPort, blockPath ++ blockPort)
          true
        case _ => false  // anything with allocates is not processed
      }
      case expr.ValueExpr.Expr.Exported(exported) => (exported.getExteriorPort, exported.getInternalBlockPort) match {
        case (ValueExpr.Ref(extPort), ValueExpr.Ref(intPort)) =>
          if (!isInLink) {
            elaboratePending.addNode(
              ElaborateRecord.Connect(blockPath ++ extPort, blockPath ++ intPort, blockPath),
              Seq(ElaborateRecord.Port(blockPath ++ extPort))
            )
            constProp.setConnection(blockPath ++ extPort, blockPath ++ intPort)
          } else {  // for links, the internal port is towards the inner link, so the args are flipped
            elaboratePending.addNode(
              ElaborateRecord.Connect(blockPath ++ intPort, blockPath ++ extPort, blockPath),
              Seq(ElaborateRecord.Port(blockPath ++ intPort))
            )
            constProp.setConnection(blockPath ++ intPort, blockPath ++ extPort)
          }
          true
        case _ => false  // anything with allocates is not processed
      }
      case expr.ValueExpr.Expr.ExportedTunnel(exported) => (exported.getExteriorPort, exported.getInternalBlockPort) match {
        case (ValueExpr.Ref(extPort), ValueExpr.Ref(intPort)) =>
          require(!isInLink)
          elaboratePending.addNode(
            ElaborateRecord.Connect(blockPath ++ extPort, blockPath ++ intPort, blockPath),
            Seq(ElaborateRecord.Port(blockPath ++ extPort))
          )
          constProp.setConnection(blockPath ++ extPort, blockPath ++ intPort)
          true
        case _ => false  // anything with allocates is not processed
      }
      case _ => false  // not defined
    }
  }

  // Given a block library at some path, expand it and link it in the parent.
  // Does not elaborate the internals (including connections / assertions / assignments), which is
  // a separate phase that (for generators) may be gated on additional parameters.
  // Handles class type refinements and adds default parameters and class-based value refinements
  // For the generator, this will be a skeleton block.
  protected def expandBlock(path: DesignPath): Unit = {
    import edgir.elem.elem

    val block = resolveBlock(path).asInstanceOf[wir.BlockLibrary]
    val libraryPath = block.target
    val libraryBlockPb = library.getBlock(libraryPath) match {
      case Errorable.Success(blockPb) => blockPb
      case Errorable.Error(err) =>
        errors += CompilerError.LibraryError(path, libraryPath, err)
        elem.HierarchyBlock()
    }

    val refinementLibraryPath = refinements.instanceRefinements.get(path).orElse(
      refinements.classRefinements.get(libraryPath).orElse(
        libraryBlockPb.defaultRefinement
      )
    )
    val unrefinedType = if (refinementLibraryPath.isDefined) Some(libraryPath) else None
    val blockLibraryPath = refinementLibraryPath.getOrElse(libraryPath)

    val blockPb = library.getBlock(blockLibraryPath) match {
      case Errorable.Success(blockPb) =>
        blockPb
      case Errorable.Error(err) =>
        errors += CompilerError.LibraryError(path, blockLibraryPath, err)
        elem.HierarchyBlock()
    }

    // add class-based refinements - must be set before refinement params
    // note that this operates on the post-refinement class
    filterRefinementClassValues(blockLibraryPath, refinementClassValuesByClass).foreach {
      case ((refinementClass, postfix), value) =>
        val paramPath = path ++ postfix
        if (!refinementInstanceValuePaths.contains(paramPath)) { // instance values supersede class values
          constProp.addAssignValue(path.asIndirect ++ postfix, value, DesignPath(),
            s"${refinementClass.toSimpleString} class refinement", forced=true)
        }
    }

    // additional processing needed for the refinement case
    if (unrefinedType.isDefined) {
      if (!library.blockIsSubclassOf(blockLibraryPath, libraryPath)) {  // check refinement validity
        errors += CompilerError.RefinementSubclassError(path, blockLibraryPath, libraryPath)
      }

      val unrefinedPb = library.getBlock(libraryPath) match {  // add subclass (refinement) default params
        case Errorable.Success(unrefinedPb) =>
          unrefinedPb
        case Errorable.Error(err) =>  // this doesn't stop elaboration, but does raise an error
          import edgir.elem.elem
          errors += CompilerError.LibraryError(path, libraryPath, err)
          elem.HierarchyBlock()
      }
      val refinedNewParams = blockPb.params.toSeqMap.keys.toSet -- unrefinedPb.params.toSeqMap.keys
      refinedNewParams.foreach { refinedNewParam =>
        blockPb.paramDefaults.get(refinedNewParam).foreach { refinedDefault =>
          constProp.addAssignExpr(path.asIndirect + refinedNewParam, refinedDefault,
            path, s"(default)${blockLibraryPath.toSimpleString}.$refinedNewParam")
        }
      }
    }

    val newBlock = if (blockPb.generator.isEmpty) {
      new wir.Block(blockPb, unrefinedType)
    } else {
      new wir.Generator(blockPb, unrefinedType)
    }

    val (parentPath, blockName) = path.split
    val parent = resolveBlock(parentPath).asInstanceOf[wir.Block]
    parent.elaborate(blockName, newBlock)

    constProp.addAssignValue(path.asIndirect + IndirectStep.Name, TextValue(path.toString),
      path, "name")
    processParamDeclarations(path, Some(newBlock.getBlockClass), newBlock)

    newBlock.getPorts.foreach { case (portName, port) =>
      elaboratePort(path + portName, path, newBlock, port)
    }

    // TODO instead of directly elaborating, add it as a separate step dependent on generators
    // This is currently needed while connect algo refactoring is in progress to only break one thing at a time.
    val deps = newBlock match {
      case newBlock: wir.Generator =>
        newBlock.getDependencies.map { depPath =>
          ElaborateRecord.ParamValue(path.asIndirect ++ depPath)
        }
      case _ => Seq()
    }
    elaboratePending.addNode(ElaborateRecord.Block(path), deps)
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
    constProp.addAssignValue(path.asIndirect + IndirectStep.Name, TextValue(path.toString),
      path, "name")
    processParamDeclarations(path, None, newLink)

    newLink.getPorts.foreach { case (portName, port) =>
      elaboratePort(path + portName, path, newLink, port)
    }

    // For link-side port arrays: set ALLOCATED -> ELEMENTS and allow it to expand later
    newLink.getPorts.collect { case (portName, port: wir.PortArray) =>
      require(!port.portsSet) // links can't have fixed array elts
      constProp.addAssignEqual(
        path.asIndirect + portName + IndirectStep.Elements, path.asIndirect + portName + IndirectStep.Allocated,
          path, s"$portName (link array-from-connects)")
    }

    // Links can only elaborate when their port arrays are ready
    val arrayDeps = newLink.getPorts.collect {
      case (portName, arr: wir.PortArray) => ElaborateRecord.ElaboratePortArray(path + portName)
    }.toSeq
    elaboratePending.addNode(ElaborateRecord.Link(path), arrayDeps)

    newLink
  }

  // Expand an link array in-place.
  protected def expandLinkArray(path: DesignPath, array: wir.LinkArray): Unit = {
    val libraryPath = array.getModelLibrary

    val modelPb = library.getLink(libraryPath) match {
      case Errorable.Success(linkPb) =>
        linkPb
      case Errorable.Error(err) =>
        import edgir.elem.elem
        errors += CompilerError.LibraryError(path, libraryPath, err)
        elem.Link()
    }
    val model = new wir.Link(modelPb)
    array.createFrom(model)

    // For all arrays, size ELEMENTS directly from ALLOCATED
    model.getPorts.collect { case (portName, port: wir.PortArray) =>
      constProp.addAssignEqual(
        path.asIndirect + portName + IndirectStep.Elements, path.asIndirect + portName + IndirectStep.Allocated,
        path, s"$portName (link-array array-from-connects)")
    }

    val arrayPortDeps = model.getPorts.collect { case (portName, port: wir.PortArray) =>
      ElaborateRecord.ParamValue(path.asIndirect + portName + IndirectStep.Elements)
    }.toSeq
    val elementDep = ElaborateRecord.ParamValue(path.asIndirect + IndirectStep.Elements)

    elaboratePending.addNode(ElaborateRecord.LinkArray(path), arrayPortDeps :+ elementDep)
  }

  protected def runGenerator(path: DesignPath, generator: wir.Generator): Unit = {
    val reqParamValues = generator.getDependencies.map { reqParam =>
      reqParam -> constProp.getValue(path.asIndirect ++ reqParam).getOrElse(
        throw new IllegalArgumentException(f"missing param ${path.asIndirect ++ reqParam}"))
    }

    // Run generator and plug in
    library.runGenerator(generator.getBlockClass, reqParamValues.toMap) match {
      case Errorable.Success(generatedPb) =>
        val generatedPorts = generator.applyGenerated(generatedPb)
        generatedPorts.foreach { portName =>
          val portArray = generator.getPorts(portName).asInstanceOf[wir.PortArray]
          constProp.addAssignValue(path.asIndirect + portName + IndirectStep.Elements,
            ArrayValue(portArray.getPorts.keys.toSeq.map(TextValue(_))),
            path, "generator-defined elements")
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
    block.getBlocks.foreach { case (innerBlockName, innerBlock) =>
      elaboratePending.addNode(
        ElaborateRecord.ExpandBlock(path + innerBlockName, innerBlock.asInstanceOf[BlockLibrary].target),
        Seq())
    }

    block.getLinks.foreach {
      case (innerLinkName, innerLink: wir.LinkLibrary) =>
        block.elaborate(innerLinkName, expandLink(path + innerLinkName, innerLink))
      case (innerLinkName, innerLink: wir.LinkArray) =>
        expandLinkArray(path + innerLinkName, innerLink)
      case _ => throw new NotImplementedError()
    }

    val connectedConstraints = new ConnectedConstraintManager(block)
    // Set IsConnected and generate constraint expansion records
    import edg.ExprBuilder.ValueExpr
    block.getBlocks.foreach { case (innerBlockName, innerBlock) =>
      val innerBlockLibrary = innerBlock.asInstanceOf[wir.BlockLibrary]
      val innerBlockTemplate = library.getBlock(innerBlockLibrary.target)

      innerBlockTemplate.map { innerBlockTemplate => innerBlockTemplate.ports.asPairs.foreach { case (portName, port) =>
        import edgir.elem.elem
        val portPostfix = Seq(innerBlockName, portName)
        port.is match {
          case _: elem.PortLike.Is.Array =>  // array case: connectivity delayed to lowering
            connectedConstraints.connectionsByBlockPort(portPostfix) match {
              case PortConnections.ArrayConnect(constrName, constr) => constr.expr match {
                case expr.ValueExpr.Expr.ConnectedArray(connected) =>
                  val linkPortPostfix = connected.getLinkPort match {
                    case ValueExpr.Ref(linkPortPostfix) => linkPortPostfix
                    case ValueExpr.RefAllocate(linkPortPostfix, _) => linkPortPostfix
                    case _ => throw new IllegalArgumentException
                  }
                  val linkElements = path.asIndirect + linkPortPostfix.head + IndirectStep.Elements
                  val blockPortElements = path.asIndirect ++ portPostfix + IndirectStep.Elements
                  elaboratePending.addNode(ElaborateRecord.AssignLinkElements(
                    linkElements, blockPortElements, path),
                    Seq(ElaborateRecord.ParamValue(blockPortElements)))
                  constProp.addAssignEqual(path.asIndirect ++ portPostfix + IndirectStep.Allocated,
                    linkElements,
                    path, "array connect ALLOCATED from link ELEMENTS")

                  val expandArrayTask = ElaborateRecord.ExpandArrayConnections(path, constrName)
                  // Note: actual expansion task set on the link side
                  val resolveConnectedTask = ElaborateRecord.ResolveArrayIsConnected(path, portPostfix, Seq(), Seq(constrName), false)
                  elaboratePending.addNode(resolveConnectedTask, Seq(
                    ElaborateRecord.ElaboratePortArray(path ++ portPostfix),
                    expandArrayTask
                  ))

                case expr.ValueExpr.Expr.ExportedArray(exported) =>  // note internal port is portPostfix
                  val ValueExpr.Ref(extPostfix) = exported.getExteriorPort
                  constProp.addAssignEqual(path.asIndirect ++ extPostfix + IndirectStep.Elements,
                    path.asIndirect ++ portPostfix + IndirectStep.Elements,
                    path, constrName)
                  constProp.addAssignEqual(path.asIndirect ++ portPostfix + IndirectStep.Allocated,
                    path.asIndirect ++ extPostfix + IndirectStep.Allocated,
                    path, constrName)
                  val expandArrayTask = ElaborateRecord.ExpandArrayConnections(path, constrName)
                  elaboratePending.addNode(expandArrayTask,
                    Seq(
                      ElaborateRecord.ParamValue(path.asIndirect ++ portPostfix + IndirectStep.Elements),
                      // allocated must run first, it depends on constraints not being lowered
                      ElaborateRecord.ParamValue(path.asIndirect ++ portPostfix + IndirectStep.Allocated)
                  ))
                  val resolveConnectedTask = ElaborateRecord.ResolveArrayIsConnected(path, portPostfix, Seq(), Seq(constrName), false)
                  elaboratePending.addNode(resolveConnectedTask, Seq(
                    ElaborateRecord.ElaboratePortArray(path ++ portPostfix),
                    expandArrayTask))

                case _ => throw new IllegalArgumentException(s"invalid array connect to array $constr")
              }

              case PortConnections.AllocatedConnect(singleConnects, arrayConnects) =>
                val namer = new AssignNamer()
                val connectNames = singleConnects.map { case (suggestedName, _, _) => namer.name(suggestedName) }
                val connectTerms = ExprBuilder.ValueExpr.LiteralArrayText(connectNames)
                val arrayConnectTermss = arrayConnects.map { case (suggestedName, _, constr) =>
                  val allocatedVals = constr.expr match {
                    case expr.ValueExpr.Expr.ConnectedArray(connected) => connected.getLinkPort match {
                      case ValueExpr.RefAllocate(linkPath, _) =>
                        ValueExpr.Ref(ref.LocalPath(steps = Seq(
                          ref.LocalStep(step = ref.LocalStep.Step.Name(linkPath.head)),
                          ref.LocalStep(step = ref.LocalStep.Step.ReservedParam(value = ref.Reserved.ELEMENTS))
                        )))
                      case ValueExpr.Ref(linkPath) =>  // exactly the same as the RefAllocate case
                        ValueExpr.Ref(ref.LocalPath(steps = Seq(
                          ref.LocalStep(step = ref.LocalStep.Step.Name(linkPath.head)),
                          ref.LocalStep(step = ref.LocalStep.Step.ReservedParam(value = ref.Reserved.ELEMENTS))
                        )))
                      case _ => throw new IllegalArgumentException
                    }
                    case expr.ValueExpr.Expr.ExportedArray(_) =>
                      // Can't array-export from an allocated array, since it's unclear what the actual internal
                      // ELEMENTS are since there isn't a specified correlation from ALLOCATED (available here) to
                      // (potentially post-generate) ELEMENTS.
                      // Possible semantics here might be to just use the ALLOCATED available here, but that is
                      // subtly different from ELEMENTS in edge cases, so for now the user must explicitly unroll
                      // the array.
                      throw new IllegalArgumentException("unsupported array export to allocate")
                    case _ => throw new IllegalArgumentException
                  }
                  val allocatedName = ValueExpr.Literal(namer.name(suggestedName) + "_")
                  ValueExpr.BinSetOp(expr.BinarySetExpr.Op.CONCAT, allocatedName, allocatedVals)
                }
                constProp.addAssignExpr(path.asIndirect ++ portPostfix + IndirectStep.Allocated,
                  ValueExpr.UnarySetOp(expr.UnarySetExpr.Op.FLATTEN,
                    ValueExpr.Array(Seq(connectTerms) ++ arrayConnectTermss)),
                  path, ""
                )

                val expandArrayConnectTasks = arrayConnects.map { case (allocated, constrName, constr) =>
                  ElaborateRecord.ExpandArrayConnections(path, constrName)
                }
                val resolveAllocateTask = ElaborateRecord.RewriteConnectAllocate(path, portPostfix, singleConnects.map(_._2), arrayConnects.map(_._2), false)
                elaboratePending.addNode(resolveAllocateTask,
                  Seq(ElaborateRecord.ElaboratePortArray(path ++ portPostfix)) ++ expandArrayConnectTasks)
                val resolveConnectedTask = ElaborateRecord.ResolveArrayIsConnected(path, portPostfix, singleConnects.map(_._2), arrayConnects.map(_._2), false)
                elaboratePending.addNode(resolveConnectedTask, Seq(resolveAllocateTask))

              case PortConnections.AllocatedTunnelExport(connects) =>
                // similar to AllocatedConnect case, except only with single-element connects
                val namer = new AssignNamer()
                val connectNames = connects.map { case (suggestedName, _, _) => namer.name(suggestedName) }
                constProp.addAssignExpr(path.asIndirect ++ portPostfix + IndirectStep.Allocated,
                  ExprBuilder.ValueExpr.LiteralArrayText(connectNames),
                  path, ""
                )
                val resolveAllocateTask = ElaborateRecord.RewriteConnectAllocate(path, portPostfix, connects.map(_._2), Seq(), false)
                elaboratePending.addNode(resolveAllocateTask,
                  Seq(ElaborateRecord.ElaboratePortArray(path ++ portPostfix)))
                val resolveConnectedTask = ElaborateRecord.ResolveArrayIsConnected(path, portPostfix, connects.map(_._2), Seq(), false)
                elaboratePending.addNode(resolveConnectedTask, Seq(resolveAllocateTask))

              case PortConnections.NotConnected =>
                constProp.addAssignValue(path.asIndirect ++ portPostfix + IndirectStep.Allocated, ArrayValue(Seq()),
                  path, "not connected")
                val resolveConnectedTask = ElaborateRecord.ResolveArrayIsConnected(path, portPostfix, Seq(), Seq(), false)
                elaboratePending.addNode(resolveConnectedTask, Seq(
                  ElaborateRecord.ElaboratePortArray(path ++ portPostfix)))

              case connects => throw new IllegalArgumentException(s"invalid connections to array $connects")
            }

          case _ =>  // leaf only, no array support
            connectedConstraints.connectionsByBlockPort(portPostfix) match {
              case PortConnections.SingleConnect(constrName, constr) =>
                resolvePortConnectivity(path, portPostfix, Some(constrName, constr))
              case PortConnections.TunnelExport(constrName, constr) =>
                resolvePortConnectivity(path, portPostfix, Some(constrName, constr))
              case PortConnections.NotConnected =>
                resolvePortConnectivity(path, portPostfix, None)
              case connects => throw new IllegalArgumentException(s"invalid connections to element $connects")
            }
        }
      }
    }}

    block.getLinks.foreach {
      case (innerLinkName, innerLink: wir.Link) => innerLink.getPorts.foreach { case (portName, port) =>
        val portPostfix = Seq(innerLinkName, portName)
        port match {
          case _: wir.PortArray =>  // array case: connectivity delayed to lowering
            connectedConstraints.connectionsByLinkPort(portPostfix, false) match {
              case PortConnections.ArrayConnect(constrName, constr) =>
                throw new NotImplementedError()

              case PortConnections.AllocatedConnect(singleConnects, arrayConnects) =>
                require(arrayConnects.isEmpty)  // flattening (array-array w/o LinkArray) connections currently not used
                val namer = new AssignNamer()
                val connectNames = singleConnects.map { case (suggestedName, constrName, _) =>
                  val allocatedName = namer.name(suggestedName)
                  // because link ports elements are always defined by incoming connects, no waiting for elements
                  // is needed and the allocate can be rewritten here
                  block.mapConstraint(constrName) { constr =>
                    constr.connectUpdateRef { case ValueExpr.RefAllocate(`portPostfix`, `suggestedName`) =>
                      ValueExpr.Ref((portPostfix :+ allocatedName): _*)
                    }
                  }
                  allocatedName
                }
                constProp.addAssignExpr(path.asIndirect ++ portPostfix + IndirectStep.Allocated,
                  ExprBuilder.ValueExpr.LiteralArrayText(connectNames),
                  path, ""
                )
                elaboratePending.addNode(
                  ElaborateRecord.ResolveArrayIsConnected(path, portPostfix, singleConnects.map(_._2), Seq(), false),
                  Seq(ElaborateRecord.ElaboratePortArray(path ++ portPostfix)))

              case PortConnections.NotConnected =>
                constProp.addAssignValue(path.asIndirect ++ portPostfix + IndirectStep.Allocated, ArrayValue(Seq()),
                  path, "not connected")
                val resolveConnectedTask = ElaborateRecord.ResolveArrayIsConnected(path, portPostfix, Seq(), Seq(), false)
                elaboratePending.addNode(resolveConnectedTask, Seq(
                  ElaborateRecord.ElaboratePortArray(path ++ portPostfix)))

              case connects => throw new IllegalArgumentException(s"invalid connections to array $connects")
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
      case (innerLinkName, innerLink: wir.LinkArray) => innerLink.getModelPorts.foreach { case (portName, port) =>
        val portPostfix = Seq(innerLinkName, portName)
        port match {
          case _: wir.PortArray => // array case: connectivity delayed to lowering
            connectedConstraints.connectionsByLinkPort(portPostfix, false) match {
              case PortConnections.AllocatedConnect(singleConnects, arrayConnects) =>
                require(singleConnects.isEmpty)  // link arrays cannot have single connects on ports
                // array ports on link arrays are nested two deep, first (outer, resolved here) by connects
                // then (inner, resolved separately) by the link's ELEMENTS
                val namer = new AssignNamer()
                val suggestedNames = arrayConnects.map { case (suggestedName, constrName, _) =>
                  val allocatedName = namer.name(suggestedName)
                  block.mapConstraint(constrName) { constr =>
                    // similarly, to the regular link case, allocates can be rewritten here
                    constr.arrayUpdateRef { case ValueExpr.RefAllocate(`portPostfix`, None) =>
                      ValueExpr.Ref((portPostfix :+ allocatedName): _*)
                    }
                  }
                  allocatedName
                }
                constProp.addAssignExpr(path.asIndirect ++ portPostfix + IndirectStep.Allocated,
                  ExprBuilder.ValueExpr.LiteralArrayText(suggestedNames),
                  path, ""
                )
                val expandArrayTasks = arrayConnects.map { case (allocated, constrName, constr) =>
                  val expandArrayTask = ElaborateRecord.ExpandArrayConnections(path, constrName)
                  elaboratePending.addNode(expandArrayTask,
                    Seq(ElaborateRecord.ParamValue(path.asIndirect + portPostfix.head + IndirectStep.Elements)))
                  expandArrayTask
                }
                val resolveConnectedTask = ElaborateRecord.ResolveArrayIsConnected(path, portPostfix, Seq(), arrayConnects.map(_._2), false)
                elaboratePending.addNode(resolveConnectedTask,
                  Seq(ElaborateRecord.ElaboratePortArray(path ++ portPostfix)) ++
                  expandArrayTasks)

              case PortConnections.NotConnected =>  // TODO what are NC semantics for link array?
                constProp.addAssignValue(path.asIndirect ++ portPostfix + IndirectStep.Allocated, ArrayValue(Seq()),
                  path, "not connected")
                val resolveConnectedTask = ElaborateRecord.ResolveArrayIsConnected(path, portPostfix, Seq(), Seq(), false)
                elaboratePending.addNode(resolveConnectedTask, Seq(
                  ElaborateRecord.ElaboratePortArray(path ++ portPostfix)))

              case connects => throw new IllegalArgumentException(s"invalid connections to array $connects")
            }
          case _ =>  // non-array, eg Port or Bundle
            connectedConstraints.connectionsByLinkPort(portPostfix, false) match {
              case PortConnections.ArrayConnect(constrName, constr) => constr.expr match {
                case expr.ValueExpr.Expr.ConnectedArray(connected) =>
                  val expandArrayTask = ElaborateRecord.ExpandArrayConnections(path, constrName)
                  elaboratePending.addNode(expandArrayTask, Seq(
                    ElaborateRecord.ParamValue(path.asIndirect + portPostfix.head + IndirectStep.Elements)
                  ))
                  // Note: actual expansion task set on the link side
                  val resolveConnectedTask = ElaborateRecord.ResolveArrayIsConnected(path, portPostfix, Seq(), Seq(constrName), false)
                  elaboratePending.addNode(resolveConnectedTask, Seq(
                    ElaborateRecord.ElaboratePortArray(path ++ portPostfix),
                    expandArrayTask))

                case connects => throw new IllegalArgumentException(s"invalid connections to array $connects")
              }

              case PortConnections.NotConnected =>
                val resolveConnectedTask = ElaborateRecord.ResolveArrayIsConnected(path, portPostfix, Seq(), Seq(), false)
                elaboratePending.addNode(resolveConnectedTask, Seq(
                  ElaborateRecord.ElaboratePortArray(path ++ portPostfix)))

              case connects => throw new IllegalArgumentException(s"invalid connections to element $connects")
            }
        }
      }
      case _ => throw new IllegalArgumentException
    }

    // Process all the process-able constraints: parameter constraints and non-allocate connected
    block.getConstraints.foreach { case (constrName, constr) =>
      processAssignConstraint(path, constrName, constr, constr)
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

    // TODO refactor this out, ConnectedLink needs to be centralized
    def setConnectedLink(portPath: DesignPath, port: PortLike): Unit = (port: @unchecked) match {
      case _: wir.Port | _: wir.Bundle =>
        constProp.setConnectedLink(path, portPath)
      case port: wir.PortArray =>
        port.getPorts.foreach { case (subPortName, subPort) =>
          setConnectedLink(portPath + subPortName, subPort)
        }
    }
    for ((portName, port) <- link.getPorts) {
      setConnectedLink(path + portName, port)
    }

    // Queue up sub-trees that need elaboration
    link.getLinks.foreach { case (innerLinkName, innerLink) =>
      val innerLinkElaborated = expandLink(path + innerLinkName, innerLink.asInstanceOf[wir.LinkLibrary])
      link.elaborate(innerLinkName, innerLinkElaborated)
    }

    // Aggregate by inner link ports
    val connectedConstraints = new ConnectedConstraintManager(link)

    link.getLinks.foreach { case (innerLinkName, innerLink) =>
      innerLink.asInstanceOf[wir.Link].getPorts.foreach { case (portName, port) =>
        val portPostfix = Seq(innerLinkName, portName)
        port match {
          case _: wir.PortArray => // array case: ignored, handled in lowering
            connectedConstraints.connectionsByLinkPort(portPostfix, true) match {
              case PortConnections.AllocatedConnect(singleConnects, arrayConnects) =>
                val namer = new AssignNamer()
                val connectNames = singleConnects.map { case (suggestedName, _, _) => namer.name(suggestedName) }
                val connectTerms = ExprBuilder.ValueExpr.LiteralArrayText(connectNames)
                val arrayConnectTermss = arrayConnects.map { case (suggestedName, _, constr) =>
                  val ValueExpr.MapExtract(ValueExpr.Ref(extPostfix), Ref(_)) = constr.getExportedArray.getExteriorPort
                  val allocatedVals = ValueExpr.Ref(ref.LocalPath(steps=
                    extPostfix.map(step => ref.LocalStep(step=ref.LocalStep.Step.Name(step))) :+
                        ref.LocalStep(step=ref.LocalStep.Step.ReservedParam(value=ref.Reserved.ALLOCATED))
                  ))
                  val allocatedName = ValueExpr.Literal(namer.name(suggestedName) + "_")
                  ValueExpr.BinSetOp(expr.BinarySetExpr.Op.CONCAT, allocatedName, allocatedVals)
                }
                constProp.addAssignExpr(path.asIndirect ++ portPostfix + IndirectStep.Allocated,
                  ValueExpr.UnarySetOp(expr.UnarySetExpr.Op.FLATTEN,
                    ValueExpr.Array(Seq(connectTerms) ++ arrayConnectTermss)),
                  path, ""
                )

                arrayConnects.foreach { case (allocated, constrName, constr) =>
                  val extPostfix = constr.getExportedArray.getExteriorPort match {
                    case ValueExpr.MapExtract(ValueExpr.Ref(extPostfix), Ref(_)) => extPostfix
                    case extPort => throw new IllegalArgumentException(s"unknown exported exterior $extPort")
                  }
                  val ValueExpr.RefAllocate(intPostfix, _) = constr.getExportedArray.getInternalBlockPort
                  elaboratePending.addNode(ElaborateRecord.ExpandArrayConnections(path, constrName), Seq(
                    ElaborateRecord.ParamValue(path.asIndirect ++ extPostfix + IndirectStep.Elements),
                    // allocated must run first, it depends on constraints not being lowered
                    ElaborateRecord.ParamValue(path.asIndirect ++ intPostfix + IndirectStep.Allocated)
                  ))
                }

                val resolveAllocateTask = ElaborateRecord.RewriteConnectAllocate(path, portPostfix, singleConnects.map(_._2), arrayConnects.map(_._2), true)
                elaboratePending.addNode(resolveAllocateTask, Seq(ElaborateRecord.ElaboratePortArray(path ++ portPostfix)))

                val resolveConnectedTask = ElaborateRecord.ResolveArrayIsConnected(path, portPostfix, singleConnects.map(_._2), arrayConnects.map(_._2), false)
                elaboratePending.addNode(resolveConnectedTask, Seq(
                  resolveAllocateTask))

              case PortConnections.NotConnected =>
                constProp.addAssignValue(path.asIndirect ++ portPostfix + IndirectStep.Allocated, ArrayValue(Seq()),
                  path, "not connected")
                val resolveConnectedTask = ElaborateRecord.ResolveArrayIsConnected(path, portPostfix, Seq(), Seq(), false)
                elaboratePending.addNode(resolveConnectedTask, Seq(
                  ElaborateRecord.ElaboratePortArray(path ++ portPostfix)))

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
      processAssignConstraint(path, constrName, constr, constr)
      processConnectedConstraint(path, constrName, constr, true)
    }
  }

  protected def elaborateLinkArray(path: DesignPath): Unit = {
    val link = resolve(path).asInstanceOf[wir.LinkArray]

    val linkElements = ArrayValue.ExtractText(
      constProp.getValue(path.asIndirect + IndirectStep.Elements).get)
    val linkPortArrayElements = link.getModelPorts.collect {
      case (portName, port: wir.PortArray) =>
        val portElements = ArrayValue.ExtractText(
          constProp.getValue(path.asIndirect + portName + IndirectStep.Elements).get)
        constProp.addAssignValue(path.asIndirect + portName + IndirectStep.Length, IntValue(portElements.size),
          path, "elements-defined count")
        elaboratePending.setValue(ElaborateRecord.ElaboratePortArray(path + portName), None) // resolved in initPortsFromModel
        portName -> portElements
    }

    // Propagate link-wide ELEMENTS to port ELEMENTS and inner-link ALLOCATED
    link.getModelPorts.foreach {
      case (portName, port: wir.PortArray) =>
        linkPortArrayElements(portName).foreach { index =>
          constProp.addAssignEqual(
            path.asIndirect + portName + index + IndirectStep.Elements,
            path.asIndirect + IndirectStep.Elements,
            path, s"$portName.$index (link-array ports-from-elts)")
        }
        linkElements.foreach { elementIndex =>
          constProp.addAssignEqual(
            path.asIndirect + elementIndex + portName + IndirectStep.Allocated,
            path.asIndirect + portName + IndirectStep.Elements,
            path, s"$elementIndex.$portName (link-array inner-port-array from outer-elts)")
        }
      case (portName, port) =>
        constProp.addAssignEqual(
          path.asIndirect + portName + IndirectStep.Elements,
          path.asIndirect + IndirectStep.Elements,
          path, s"$portName (link-array ports-from-elts)")
    }
    // Then expand the port-arrays
    link.initPortsFromModel(linkPortArrayElements).foreach { case (createdPortPostfix, createdPort) =>
      elaboratePortArray(path ++ createdPortPostfix)
      elaboratePending.setValue(ElaborateRecord.ElaboratePortArray(path ++ createdPortPostfix), None)
    }

    // Create internal links
    link.initLinks(linkElements).foreach { case (createdLinkName, createdLink) =>
      val innerLinkElaborated = expandLink(path + createdLinkName, createdLink)
      link.elaborate(createdLinkName, innerLinkElaborated)
    }

    // Create internal connects
    link.initConstraints(linkElements, linkPortArrayElements)

    // Resolve connections
    import edg.ExprBuilder.ValueExpr
    link.getConstraints.foreach { case (constrName, constr) =>
      processConnectedConstraint(path, constrName, constr, true)
    }

    // Resolve is-connected - need to sort by inner link's outermost port
    link.getConstraints.toSeq.map { case (constrName, constr) =>
      val ValueExpr.Ref(portPostfix) = constr.getExported.getInternalBlockPort
      link.getModelPorts(portPostfix(1)) match {
        case _: wir.PortArray =>
          (portPostfix.init, (constrName, constr)) // drop the array index
        case _ => // non-array like Port and Bundle
          (portPostfix, (constrName, constr))
      }
    }.groupBy(_._1).foreach { case (portPostfix, elts) =>  // actually resolve (delayed if array)
      val constrNamesConstrs = elts.map { _._2 }
      link.getModelPorts(portPostfix(1)) match {
        case _: wir.PortArray =>
          val constrNames = constrNamesConstrs.map { case (constrName, constr) => constrName }
          val resolveConnectedTask = ElaborateRecord.ResolveArrayIsConnected(path, portPostfix, constrNames, Seq(), false)
          elaboratePending.addNode(resolveConnectedTask, Seq(
            ElaborateRecord.ElaboratePortArray(path ++ portPostfix)))
        case _ => // non-array like Port and Bundle
          val Seq((constrName, constr)) = constrNamesConstrs  // can only be one element
          resolvePortConnectivity(path, portPostfix, Some(constrName, constr))
      }
    }
  }

  def elaboratePortArray(path: DesignPath): Unit = {
    val port = resolvePort(path).asInstanceOf[wir.PortArray]
    if (!port.portsSet) {
      val childPortNames = ArrayValue.ExtractText(constProp.getValue(path.asIndirect + IndirectStep.Elements).get)
      val childPortLibraries = childPortNames.map { childPortName =>
        childPortName -> wir.PortLibrary.apply(port.getType)
      }.to(SeqMap)
      port.setPorts(childPortLibraries)
    }
    for ((childPortName, childPort) <- port.getPorts) {
      elaboratePort(path + childPortName, path, port, childPort)
    }
    // since this only adds child ports to arrays (instead of creating the array in the parent),
    // we don't set the ElaborateRecord.Port(...) here
    constProp.addAssignValue(path.asIndirect + IndirectStep.Length, IntValue(port.getPorts.size),
      path, "elements-defined count")
  }

  // Sets the link's ELEMENTS from the first block-side port (source) ELEMENTS available,
  // and checks that block-side port ELEMENTS are consistent.
  protected def assignLinkElements(record: ElaborateRecord.AssignLinkElements): Unit = {
    if (constProp.getValue(record.target).isEmpty) {
      constProp.addAssignEqual(record.target, record.source,
        record.containerPath, "array connect link ELEMENTS from block-side ELEMENTS")
    }
    val linkElements = constProp.getValue(record.target).get.asInstanceOf[ArrayValue[TextValue]]
    val blockPortElements = constProp.getValue(record.source).get.asInstanceOf[ArrayValue[TextValue]]
    if (linkElements.values.toSet != blockPortElements.values.toSet) {
      errors.append(CompilerError.InconsistentLinkArrayElements(record.containerPath,
        record.target, linkElements,
        record.source, blockPortElements))
    }
  }

  // Once all array-connects have defined lengths, this lowers the array-connect statements by replacing them
  // with single leaf-level connections.
  protected def expandArrayConnections(record: ElaborateRecord.ExpandArrayConnections): Unit = {
    val parentBlock = resolve(record.parent).asInstanceOf[wir.HasMutableConstraints]  // can be block or link

    import edg.ExprBuilder.{Ref, ValueExpr}
    val newConstrNames = parentBlock.getConstraints(record.constraintName).expr match {
      case expr.ValueExpr.Expr.ExportedArray(exported) => (exported.getExteriorPort, exported.getInternalBlockPort) match {
        case (ValueExpr.Ref(extPortArray), ValueExpr.Ref(intPortArray)) =>
          val intPortArrayElts = ArrayValue.ExtractText(  // propagates inner to outer
            constProp.getValue(record.parent.asIndirect ++ intPortArray + IndirectStep.Elements).get)
          parentBlock.mapMultiConstraint(record.constraintName) { constr =>
            intPortArrayElts.map { index =>
              val newConstr = constr.asSingleConnection.connectUpdateRef { // tack an index on both sides
                case ValueExpr.Ref(ref) if ref == extPortArray => ValueExpr.Ref((ref :+ index): _*)
              }.connectUpdateRef {
                case ValueExpr.Ref(ref) if ref == intPortArray => ValueExpr.Ref((ref :+ index): _*)
              }
              s"${record.constraintName}.$index" -> newConstr
            }
          }.keys

        case (ValueExpr.MapExtract(ValueExpr.Ref(extPortArray), _), ValueExpr.RefAllocate(_, _)) =>
          val extPortArrayElts = ArrayValue.ExtractText(  // propagates outer to inner
            constProp.getValue(record.parent.asIndirect ++ extPortArray + IndirectStep.Elements).get)
          parentBlock.mapMultiConstraint(record.constraintName) { constr =>
            extPortArrayElts.map { index =>
              val newConstr = constr.asSingleConnection.connectUpdateRef {
                case ValueExpr.MapExtract(ValueExpr.Ref(extPortArray), Ref(extPortInner)) =>
                  ValueExpr.Ref((extPortArray ++ Seq(index) ++ extPortInner): _*)
                // inner side remains an allocate
              }
              s"${record.constraintName}.$index" -> newConstr
            }
          }.keys

        case _ => throw new IllegalArgumentException("unsupported array export")
      }
      case expr.ValueExpr.Expr.ConnectedArray(connected) =>
        // in all cases, the expansion is by link's elements, and any link-side allocations must be resolved
        val linkArrayPostfix = Seq(connected.getLinkPort.getRef.steps.head.getName)
        val linkArrayElts = ArrayValue.ExtractText( // propagates inner to outer
          constProp.getValue(record.parent.asIndirect ++ linkArrayPostfix + IndirectStep.Elements).get)
        parentBlock.mapMultiConstraint(record.constraintName) { constr =>
          linkArrayElts.map { index =>
            val newConstr = constr.asSingleConnection.connectUpdateRef { // tack an index on both sides
              case ValueExpr.Ref(ref) if !ref.startsWith(linkArrayPostfix) => ValueExpr.Ref((ref :+ index): _*)
              case ValueExpr.RefAllocate(ref, None) if !ref.startsWith(linkArrayPostfix) =>
                ValueExpr.RefAllocate(ref, None)  // allocate stays intact
              case ValueExpr.RefAllocate(ref, Some(suggestedName)) if !ref.startsWith(linkArrayPostfix) =>
                ValueExpr.RefAllocate(ref, Some(s"${suggestedName}_$index"))  // index tacked onto suggested name
            }.connectUpdateRef {
              case ValueExpr.Ref(ref) if ref.startsWith(linkArrayPostfix) => ValueExpr.Ref((ref :+ index): _*)
            }
            s"${record.constraintName}.$index" -> newConstr
          }
        }.keys

      case _ => throw new IllegalArgumentException
    }

    expandedArrayConnectConstraints.put(record.parent + record.constraintName, newConstrNames.toSeq)
    newConstrNames foreach { constrName =>
      // note no guarantee these are fully lowered, since the other side may have un-lowered allocates
      processConnectedConstraint(record.parent, constrName, parentBlock.getConstraints(constrName),
        parentBlock.isInstanceOf[wir.Link])
    }
  }

  // Once a block-side port array has all its element widths available, this lowers the connect statements
  // by replacing ALLOCATEs with concrete indices.
  // This must also handle internal-side export statements.
  protected def rewriteConnectAllocate(record: ElaborateRecord.RewriteConnectAllocate): Unit = {
    val parentBlock = resolve(record.parent).asInstanceOf[wir.HasMutableConstraints]  // can be block or link
    val portElements = ArrayValue.ExtractText(
      constProp.getValue(record.parent.asIndirect ++ record.portPath + IndirectStep.Elements).get)
    // Update constraint names given expanded array constraints
    val combinedConstrNames = record.constraintNames ++
        record.arrayConstraintNames.flatMap(constrName => expandedArrayConnectConstraints(record.parent + constrName))

    import edg.ExprBuilder.ValueExpr
    val suggestedNames = combinedConstrNames.flatMap { constrName =>
      parentBlock.getConstraints(constrName).connectMapRef {
        case ValueExpr.RefAllocate(record.portPath, index) => index
      }
    }.toSet

    val freeNames = portElements.filter(!suggestedNames.contains(_)).iterator
    combinedConstrNames foreach { constrName =>
      parentBlock.mapConstraint(constrName) { constr => constr.connectUpdateRef {
        case ValueExpr.RefAllocate(record.portPath, Some(suggestedName)) =>
          if (portElements.contains(suggestedName)) {
            ValueExpr.Ref((record.portPath :+ suggestedName):_*)
          } else {
            ValueExpr.RefAllocate(record.portPath, Some(f"not in array: $suggestedName"))
          }
        case ValueExpr.RefAllocate(record.portPath, None) =>
          if (freeNames.hasNext) {
            ValueExpr.Ref((record.portPath :+ freeNames.next()): _*)
          } else {
            ValueExpr.RefAllocate(record.portPath, Some(f"no free ports"))
          }
      } }
    }

    combinedConstrNames foreach { constrName =>
      // note no guarantee these are fully lowered, since the other side may have un-lowered allocates
      processConnectedConstraint(record.parent, constrName, parentBlock.getConstraints(constrName), record.portIsLink)
    }
  }

  protected def resolveArrayIsConnected(record: ElaborateRecord.ResolveArrayIsConnected): Unit = {
    val parentBlock = resolve(record.parent).asInstanceOf[wir.HasMutableConstraints]  // can be block or link
    val combinedConstrNames = record.constraintNames ++
        record.arrayConstraintNames.flatMap(constrName => expandedArrayConnectConstraints(record.parent + constrName))

    import edg.ExprBuilder.ValueExpr
    val allocatedIndexToConstraint = combinedConstrNames.flatMap { constrName =>
      parentBlock.getConstraints(constrName).connectMapRef {
        case ValueExpr.Ref(record.portPath :+ index) => Some((Seq(index), constrName))
        case ValueExpr.Ref(record.portPath :+ index :+ interior) => Some((Seq(index, interior), constrName))  // for link arrays
        case ValueExpr.RefAllocate(record.portPath, _) => None  // allocate should be resolved by here, except for bad designs
      }
    }.toMap

    val portArray = resolve(record.parent ++ record.portPath).asInstanceOf[wir.PortArray]
    portArray.getPorts.foreach {
      case (index, innerPort: wir.PortArray) =>  // for link arrays
        require(innerPort.isElaborated)
        innerPort.getPorts.foreach { case (subIndex, subPort) =>
          val constraintOption = allocatedIndexToConstraint.get(Seq(index, subIndex)).map { constrName =>
            (constrName, parentBlock.getConstraints(constrName))
          }
          resolvePortConnectivity(record.parent, record.portPath :+ index :+ subIndex, constraintOption)
        }
      case (index, innerPort) =>
        val constraintOption = allocatedIndexToConstraint.get(Seq(index)).map { constrName =>
          (constrName, parentBlock.getConstraints(constrName))
        }
        resolvePortConnectivity(record.parent, record.portPath :+ index, constraintOption)
    }
  }

  /** Performs full compilation and returns the resulting design. Might take a while.
    */
  def compile(): schema.Design = {
    import edg.ElemBuilder

    // to handle partial compilation, as records are processed they are checked against a match to partial
    // if there is a match, they are added here to be ignored on subsequent passes
    // this is rebuilt dynamically on each compile() invocation
    val partialCompileIgnoredRecords = mutable.Set[ElaborateRecord]()

    // repeat as long as there is work ready, and all the ready work isn't marked to be ignored
    var readyList = Set[ElaborateRecord]()
    do {
      readyList = elaboratePending.getReady -- partialCompileIgnoredRecords
      readyList.foreach { elaborateRecord =>
        try {
          elaborateRecord match {
            case elaborateRecord@ElaborateRecord.ExpandBlock(blockPath, blockClass) =>
              if (partial.blocks.contains(blockPath) || partial.classes.contains(blockClass)) {
                partialCompileIgnoredRecords.add(elaborateRecord)
              } else {
                expandBlock(blockPath)
                elaboratePending.setValue(elaborateRecord, None)
              }
            case elaborateRecord@ElaborateRecord.Block(blockPath) =>
              elaborateBlock(blockPath)
              elaboratePending.setValue(elaborateRecord, None)
            case elaborateRecord@ElaborateRecord.Link(linkPath) =>
              elaborateLink(linkPath)
              elaboratePending.setValue(elaborateRecord, None)
            case elaborateRecord@ElaborateRecord.LinkArray(linkPath) =>
              elaborateLinkArray(linkPath)
              elaboratePending.setValue(elaborateRecord, None)
            case elaborateRecord@ElaborateRecord.Parameter(root, blockClass, postfix, param) =>
              if (paramMatchesPartial(root, blockClass, postfix)) {
                partialCompileIgnoredRecords.add(elaborateRecord)
              } else {
                constProp.addDeclaration(root ++ postfix, param)
                elaboratePending.setValue(elaborateRecord, None)
              }
            case connect: ElaborateRecord.Connect =>
              elaborateConnect(connect)
              elaboratePending.setValue(elaborateRecord, None)

            case elaborateRecord: ElaborateRecord.ElaboratePortArray =>
              elaboratePortArray(elaborateRecord.path)
              elaboratePending.setValue(elaborateRecord, None)

            case elaborateRecord: ElaborateRecord.AssignLinkElements =>
              assignLinkElements(elaborateRecord)
              elaboratePending.setValue(elaborateRecord, None)
            case elaborateRecord: ElaborateRecord.ExpandArrayConnections =>
              expandArrayConnections(elaborateRecord)
              elaboratePending.setValue(elaborateRecord, None)
            case elaborateRecord: ElaborateRecord.RewriteConnectAllocate =>
              rewriteConnectAllocate(elaborateRecord)
              elaboratePending.setValue(elaborateRecord, None)
            case elaborateRecord: ElaborateRecord.ResolveArrayIsConnected =>
              resolveArrayIsConnected(elaborateRecord)
              elaboratePending.setValue(elaborateRecord, None)

            case _: ElaborateRecord.ElaborateDependency =>
              throw new IllegalArgumentException(s"can't elaborate dependency-only record $elaborateRecord")
          }
        } catch {
          case e: Exception =>
            val wrappedException = new ElaboratingException(s"while elaborating $elaborateRecord", e)
            wrappedException.setStackTrace(e.getStackTrace)
            throw wrappedException
        }
      }
    } while (readyList.nonEmpty)

    ElemBuilder.Design(root.toPb)
  }

  def evaluateExpr(root: DesignPath, value: expr.ValueExpr): ExprResult = {
    new ExprEvaluatePartial(constProp, root).map(value)
  }


  // Primarily used for unit tests, TODO clean up this API?
  private[edg] def getValue(path: IndirectDesignPath): Option[ExprValue] = constProp.getValue(path)

  def getParamType(param: IndirectDesignPath): Option[Class[_ <: ExprValue]] = constProp.getType(param)
  def getParamValue(param: IndirectDesignPath): Option[ExprValue] = constProp.getValue(param)
  def getAllSolved: Map[IndirectDesignPath, ExprValue] = constProp.getAllSolved
  def getConnectedLink(port: DesignPath): Option[DesignPath] = constProp.getConnectedLink(port)
}
