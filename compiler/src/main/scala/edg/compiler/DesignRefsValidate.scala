package edg.compiler

import edg.wir.{DesignPath, IndirectDesignPath}
import edgir.elem.elem
import edgir.expr.expr
import edgir.lit.lit
import edgir.ref.ref
import edgir.schema.schema

import scala.collection.{SeqMap, mutable}


// Given an input ValueExpr, returns all the Refs as LocalPaths.
// This includes both port-valued Refs (eg, in connects) and parameter-valued Refs.
// May be indirect, eg .CONNECTE_LINK.
object CollectExprRefs extends ValueExprMap[Seq[ref.LocalPath]] {
  override def mapLiteral(literal: lit.ValueLit): Seq[ref.LocalPath] = {
    Seq()
  }
  override def mapBinary(binary: expr.BinaryExpr, lhs: Seq[ref.LocalPath],
                         rhs: Seq[ref.LocalPath]): Seq[ref.LocalPath] = {
    lhs ++ rhs
  }
  override def mapBinarySet(binarySet: expr.BinarySetExpr, lhsset: Seq[ref.LocalPath],
                            rhs: Seq[ref.LocalPath]): Seq[ref.LocalPath] = {
    lhsset ++ rhs
  }
  override def mapUnary(unary: expr.UnaryExpr, `val`: Seq[ref.LocalPath]): Seq[ref.LocalPath] = {
    `val`
  }
  override def mapUnarySet(unarySet: expr.UnarySetExpr, vals: Seq[ref.LocalPath]): Seq[ref.LocalPath] = {
    vals
  }
  override def mapStruct(struct: expr.StructExpr,
                         vals: Map[String, Seq[ref.LocalPath]]): Seq[ref.LocalPath] = {
    vals.values.foldLeft(Seq[ref.LocalPath]()) { _ ++ _ }
  }
  override def mapRange(range: expr.RangeExpr, minimum: Seq[ref.LocalPath],
                        maximum: Seq[ref.LocalPath]): Seq[ref.LocalPath] = {
    minimum ++ maximum
  }
  override def mapIfThenElse(ite: expr.IfThenElseExpr, cond: Seq[ref.LocalPath], tru: Seq[ref.LocalPath],
                             fal: Seq[ref.LocalPath]): Seq[ref.LocalPath] = {
    cond ++ tru ++ fal
  }
  override def mapExtract(extract: expr.ExtractExpr, container: Seq[ref.LocalPath],
                          index: Seq[ref.LocalPath]): Seq[ref.LocalPath] = {
    container ++ index
  }
  override def mapMapExtract(mapExtract: expr.MapExtractExpr): Seq[ref.LocalPath] = {
    Seq()  // TODO depends on knowledge of array sizes
  }
  override def mapConnected(connected: expr.ConnectedExpr, blockPort: Seq[ref.LocalPath],
                            linkPort: Seq[ref.LocalPath]): Seq[ref.LocalPath] = {
    blockPort ++ linkPort
  }
  override def mapExported(exported: expr.ExportedExpr, exteriorPort: Seq[ref.LocalPath],
                           internalBlockPort: Seq[ref.LocalPath]): Seq[ref.LocalPath] = {
    exteriorPort ++ internalBlockPort
  }
  override def mapConnectedArray(connected: expr.ConnectedExpr, blockPort: Seq[ref.LocalPath],
                                 linkPort: Seq[ref.LocalPath]): Seq[ref.LocalPath] = {
    blockPort ++ linkPort
  }
  override def mapExportedArray(exported: expr.ExportedExpr, exteriorPort: Seq[ref.LocalPath],
                                internalBlockPort: Seq[ref.LocalPath]): Seq[ref.LocalPath] = {
    exteriorPort ++ internalBlockPort
  }
  override def mapAssign(assign: expr.AssignExpr, src: Seq[ref.LocalPath]): Seq[ref.LocalPath] = {
    assign.dst.toSeq ++ src
  }
  override def mapRef(path: ref.LocalPath): Seq[ref.LocalPath] =
    Seq(path)
}


/** Checks that refs in the design are valid.
  * TODO: check parameter references - but these needs CONNECTED_LINK values
  * TODO: also needs to handle MapExtract properly, which needs array sizes
  */
class DesignRefsValidate extends DesignMap[Unit, Unit, Unit] {
  // as list of (constr path, ref)
  protected val connectRefs = mutable.ListBuffer[(DesignPath, IndirectDesignPath)]()
  protected val paramRefs = mutable.ListBuffer[(DesignPath, IndirectDesignPath)]()

  protected val portDefs = mutable.Set[DesignPath]()
  protected val paramDefs = mutable.Set[DesignPath]()

  def mapConstraint(containingPath: DesignPath, constrName: String, constr: expr.ValueExpr): Unit = {
    val refs = CollectExprRefs.map(constr).map { ref =>
      (containingPath + constrName, containingPath.asIndirect ++ ref)
    }
    (constr.expr: @unchecked) match {
      case _: expr.ValueExpr.Expr.Connected => connectRefs.appendAll(refs)
      case _ => paramRefs.appendAll(refs)  // assume everything else is a ref, TODO clarify with top-level Statements
    }
  }

  override def mapPort(path: DesignPath, port: elem.Port): Unit = {
    port.params.foreach { case (name, _) => paramDefs.add(path + name) }
    portDefs.add(path)
  }
  override def mapPortArray(path: DesignPath, port: elem.PortArray,
                   ports: SeqMap[String, Unit]): Unit = {
    // do nothing
  }
  override def mapBundle(path: DesignPath, port: elem.Bundle,
                ports: SeqMap[String, Unit]): Unit = {
    port.params.foreach { case (name, _) => paramDefs.add(path + name) }
    portDefs.add(path)
  }
  override def mapPortLibrary(path: DesignPath, port: ref.LibraryPath): Unit = {
    Seq(CompilerError.LibraryElement(path, port))
  }

  override def mapBlock(path: DesignPath, block: elem.HierarchyBlock,
               ports: SeqMap[String, Unit], blocks: SeqMap[String, Unit],
               links: SeqMap[String, Unit]): Unit = {
    block.params.foreach { case (name, _) => paramDefs.add(path + name) }
    block.constraints.foreach { case (name, constr) => mapConstraint(path, name, constr) }
  }
  override def mapBlockLibrary(path: DesignPath, block: ref.LibraryPath): Unit = {
    // do nothing
  }

  override def mapLink(path: DesignPath, link: elem.Link,
                       ports: SeqMap[String, Unit], links: SeqMap[String, Unit]): Unit = {
    link.params.foreach { case (name, _) => paramDefs.add(path + name) }
    link.constraints.foreach { case (name, constr) => mapConstraint(path, name, constr) }
  }
  override def mapLinkArray(path: DesignPath, link: elem.LinkArray,
                            ports: SeqMap[String, Unit], links: SeqMap[String, Unit]): Unit = {
    link.constraints.foreach { case (name, constr) => mapConstraint(path, name, constr) }
  }
  override def mapLinkLibrary(path: DesignPath, link: ref.LibraryPath): Unit = {
    // do nothing
  }

  def validate(design: schema.Design): Seq[CompilerError] = {
    map(design)
    connectRefs.collect {
      case (constrPath, portRef) =>
        DesignPath.fromIndirectOption(portRef) match {
          case Some(portRef) if portDefs.contains(portRef) => None
          case _ => Some(CompilerError.BadRef(constrPath, portRef))
        }
      case _ => None
    }.toSeq.flatten
  }
}
