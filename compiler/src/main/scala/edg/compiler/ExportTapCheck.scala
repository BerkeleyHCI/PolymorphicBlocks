package edg.compiler

import edg.ExprBuilder.ValueExpr
import edg.wir.{DesignPath, IndirectStep}
import edg.wir.ProtoUtil.ConstraintProtoToSeqMap
import edgir.elem.elem
import edgir.expr.expr
import edgir.ref.ref

import scala.collection.SeqMap

/** Checks export tap validity, that inner-side parameters are undefined and elements are consistent.
  */
class ExportTapCheck(compiler: Compiler)
    extends DesignMap[Unit, Seq[CompilerError], Seq[CompilerError]] {
  def mapConstraint(
      containingPath: DesignPath,
      constrName: String,
      constr: expr.ValueExpr
  ): Option[CompilerError] = {
    constr.expr match {
      case expr.ValueExpr.Expr.Exported(exported) if exported.tap => None
      case expr.ValueExpr.Expr.ExportedArray(exported) if exported.tap =>
        (exported.getExteriorPort, exported.getInternalBlockPort) match {
          case (ValueExpr.Ref(extPort), ValueExpr.Ref(intPort)) =>
            if (
              compiler.getValue(containingPath.asIndirect ++ extPort + IndirectStep.Elements) == compiler.getValue(
                containingPath.asIndirect ++ intPort + IndirectStep.Elements
              )
            ) {
              None
            } else {
              Some(CompilerError.ExprError(
                containingPath.asIndirect + constrName,
                "inconsistent export tap array port elements"
              ))
            }
          case _ => Some(CompilerError.BadRef(containingPath, containingPath.asIndirect + constrName))
        }
      case _ => None // non-assertions ignored
    }
  }

  override def mapPort(path: DesignPath, port: elem.Port, ports: SeqMap[String, Unit]): Unit = {}
  override def mapPortArray(path: DesignPath, port: elem.PortArray, ports: SeqMap[String, Unit]): Unit = {}
  override def mapPortLibrary(path: DesignPath, port: ref.LibraryPath): Unit = {}

  override def mapBlock(
      path: DesignPath,
      block: elem.HierarchyBlock,
      ports: SeqMap[String, Unit],
      blocks: SeqMap[String, Seq[CompilerError]],
      links: SeqMap[String, Seq[CompilerError]]
  ): Seq[CompilerError] = {
    block.constraints.asPairs.flatMap {
      case (name, constr) => mapConstraint(path, name, constr)
    }.toSeq ++ blocks.values.flatten ++ links.values.flatten
  }
  override def mapBlockLibrary(path: DesignPath, block: ref.LibraryPath): Seq[CompilerError] = {
    Seq() // block library errors should be checked elsewhere
  }

  override def mapLink(
      path: DesignPath,
      link: elem.Link,
      ports: SeqMap[String, Unit],
      links: SeqMap[String, Seq[CompilerError]]
  ): Seq[CompilerError] = {
    Seq() // export tap not valid in links
  }
  override def mapLinkArray(
      path: DesignPath,
      link: elem.LinkArray,
      ports: SeqMap[String, Unit],
      links: SeqMap[String, Seq[CompilerError]]
  ): Seq[CompilerError] = {
    Seq() // export tap not valid in links
  }
  override def mapLinkLibrary(path: DesignPath, link: ref.LibraryPath): Seq[CompilerError] = {
    Seq() // link library errors should be checked elsewhere
  }
}
