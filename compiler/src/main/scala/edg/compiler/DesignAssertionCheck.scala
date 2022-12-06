package edg.compiler

import edg.wir.DesignPath
import edg.wir.ProtoUtil.ConstraintProtoToSeqMap
import edgir.elem.elem
import edgir.expr.expr
import edgir.ref.ref

import scala.collection.SeqMap


/** Evaluates all assertions and returns those that aren't valid or are missing parameters
  */
class DesignAssertionCheck(compiler: Compiler) extends
    DesignMap[Unit, Seq[CompilerError.AssertionError], Seq[CompilerError.AssertionError]] {
  def mapConstraint(containingPath: DesignPath, constrName: String, constr: expr.ValueExpr):
      Option[CompilerError.AssertionError] = {
    constr.expr match {
      case expr.ValueExpr.Expr.Binary(_) | expr.ValueExpr.Expr.BinarySet(_) |
           expr.ValueExpr.Expr.Unary(_) | expr.ValueExpr.Expr.UnarySet(_) |
           expr.ValueExpr.Expr.IfThenElse(_) | expr.ValueExpr.Expr.Ref(_) |
           expr.ValueExpr.Expr.Literal(_) =>
        compiler.evaluateExpr(containingPath, constr) match {
          case ExprResult.Result(BooleanValue(true)) => None
          case ExprResult.Result(result) =>
            Some(CompilerError.FailedAssertion(containingPath, constrName, constr, result))
          case ExprResult.Missing(missing) =>
            Some(CompilerError.MissingAssertion(containingPath, constrName, constr, missing))
        }
      case _ => None  // non-assertions ignored
    }
  }

  override def mapPort(path: DesignPath, port: elem.Port): Unit = { }
  override def mapPortArray(path: DesignPath, port: elem.PortArray,
                   ports: SeqMap[String, Unit]): Unit = { }
  override def mapBundle(path: DesignPath, port: elem.Bundle,
                ports: SeqMap[String, Unit]): Unit = { }
  override def mapPortLibrary(path: DesignPath, port: ref.LibraryPath): Unit = { }

  override def mapBlock(path: DesignPath, block: elem.HierarchyBlock, ports: SeqMap[String, Unit],
                        blocks: SeqMap[String, Seq[CompilerError.AssertionError]],
                        links: SeqMap[String, Seq[CompilerError.AssertionError]]): Seq[CompilerError.AssertionError] = {
    block.constraints.asPairs.flatMap {
      case (name, constr) => mapConstraint(path, name, constr)
    }.toSeq ++ blocks.values.flatten ++ links.values.flatten
  }
  override def mapBlockLibrary(path: DesignPath, block: ref.LibraryPath): Seq[CompilerError.AssertionError] = {
    Seq()  // block library errors should be checked elsewhere
  }

  override def mapLink(path: DesignPath, link: elem.Link, ports: SeqMap[String, Unit],
                       links: SeqMap[String, Seq[CompilerError.AssertionError]]): Seq[CompilerError.AssertionError] = {
    link.constraints.asPairs.flatMap {
      case (name, constr) => mapConstraint(path, name, constr)
    }.toSeq ++ links.values.flatten
  }
  override def mapLinkArray(path: DesignPath, link: elem.LinkArray, ports: SeqMap[String, Unit],
                            links: SeqMap[String, Seq[CompilerError.AssertionError]]): Seq[CompilerError.AssertionError] = {
    link.constraints.asPairs.flatMap {
      case (name, constr) => mapConstraint(path, name, constr)
    }.toSeq ++ links.values.flatten
  }
  override def mapLinkLibrary(path: DesignPath, link: ref.LibraryPath): Seq[CompilerError.AssertionError] = {
    Seq()  // link library errors should be checked elsewhere
  }
}
