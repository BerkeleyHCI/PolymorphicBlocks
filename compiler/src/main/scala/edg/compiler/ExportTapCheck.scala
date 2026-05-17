package edg.compiler

import edg.ExprBuilder.ValueExpr
import edg.wir.{DesignPath, IndirectStep}
import edg.wir.ProtoUtil.{ConstraintProtoToSeqMap, ParamProtoToSeqMap}
import edgir.elem.elem
import edgir.expr.expr
import edgir.ref.ref

import scala.collection.SeqMap
import scala.collection.mutable

/** Checks export tap validity, that inner-side parameters are undefined and elements are consistent.
  */
class ExportTapCheck(compiler: Compiler)
    extends DesignMap[Unit, Seq[CompilerError], Unit] {
  val portParams = mutable.HashMap[DesignPath, Seq[String]]()

  def mapExported(
      containingPath: DesignPath,
      exportName: String,
      exported: expr.ExportedExpr
  ): Seq[CompilerError] = {
    val (ValueExpr.Ref(extPort), ValueExpr.Ref(intPort)) = (exported.getExteriorPort, exported.getInternalBlockPort)
    portParams(containingPath ++ extPort).flatMap { paramName =>
      val paramPath = containingPath.asIndirect ++ intPort + paramName
      val exportedErrors = compiler.getValue(paramPath) match {
        case Some(_) => Seq(CompilerError.ExprError(
            paramPath,
            "export tap internal port parameter must be undefined"
          ))
        case None => Seq()
      }
      exportedErrors ++ exported.expanded.flatMap(expr =>
        mapExported(containingPath, exportName, expr)
      )
    }
  }

  def mapConstraint(
      containingPath: DesignPath,
      constrName: String,
      constr: expr.ValueExpr
  ): Seq[CompilerError] = {
    constr.expr match {
      case expr.ValueExpr.Expr.Exported(exported) if exported.tap =>
        mapExported(containingPath, constrName, exported)
      case expr.ValueExpr.Expr.ExportedArray(exported) if exported.tap =>
        val (ValueExpr.Ref(extPort), ValueExpr.Ref(intPort)) = (exported.getExteriorPort, exported.getInternalBlockPort)
        val exportedArrayContainerErrors =
          if (
            compiler.getValue(containingPath.asIndirect ++ extPort + IndirectStep.Elements) == compiler.getValue(
              containingPath.asIndirect ++ intPort + IndirectStep.Elements
            )
          ) {
            Seq()
          } else {
            Seq(CompilerError.ExprError(
              containingPath.asIndirect + constrName,
              "inconsistent export tap array port elements"
            ))
          }
        exportedArrayContainerErrors ++ mapExported(containingPath, constrName, exported)
      case _ => Seq() // other constructs ignored
    }
  }

  override def mapPort(path: DesignPath, port: elem.Port, ports: SeqMap[String, Unit]): Unit = {
    portParams.put(path, port.params.asPairs.map { case (name, _) => name }.toSeq)
  }
  override def mapPortArray(path: DesignPath, port: elem.PortArray, ports: SeqMap[String, Unit]): Unit = {
    portParams.put(path, Seq())
  }
  override def mapPortLibrary(path: DesignPath, port: ref.LibraryPath): Unit = {}

  override def mapBlock(
      path: DesignPath,
      block: elem.HierarchyBlock,
      ports: SeqMap[String, Unit],
      blocks: SeqMap[String, Seq[CompilerError]],
      links: SeqMap[String, Unit]
  ): Seq[CompilerError] = {
    block.constraints.asPairs.flatMap {
      case (name, constr) => mapConstraint(path, name, constr)
    }.toSeq ++ blocks.values.flatten
  }
  override def mapBlockLibrary(path: DesignPath, block: ref.LibraryPath): Seq[CompilerError] = {
    Seq() // block library errors should be checked elsewhere
  }

  override def mapLink(
      path: DesignPath,
      link: elem.Link,
      ports: SeqMap[String, Unit],
      links: SeqMap[String, Unit]
  ): Unit = {} // export tap not valid in links

  override def mapLinkArray(
      path: DesignPath,
      link: elem.LinkArray,
      ports: SeqMap[String, Unit],
      links: SeqMap[String, Unit]
  ): Unit = {} // export tap not valid in links

  override def mapLinkLibrary(
      path: DesignPath,
      link: ref.LibraryPath
  ): Unit = {} // link library errors should be checked elsewhere
}
