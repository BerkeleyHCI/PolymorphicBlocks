package edg.compiler

import edg.EdgirUtils.SimpleLibraryPath
import edg.wir.{DesignPath, IndirectDesignPath}
import edgir.expr.expr
import edgir.ref.ref
import edgrpc.compiler.{compiler => edgcompiler}

class ElaboratingException(msg: String, wrapped: Exception) extends Exception(f"$msg:\n$wrapped")

sealed trait CompilerError {
  def toIr: edgcompiler.ErrorRecord
}

object CompilerError {
  case class Unelaborated(record: ElaborateRecord, missing: Set[ElaborateRecord]) extends CompilerError {
    // These errors may be redundant with below, but provides dependency data
    override def toString: String = s"Unelaborated missing dependencies $record:\n" +
      s"${missing.map(x => s"- $x").mkString("\n")}"

    override def toIr: edgcompiler.ErrorRecord = {
      val missingStr = "missing " + missing.map(_.toString).mkString(", ")
      val (kind, path) = record match {
        case ElaborateRecord.ExpandBlock(path, _, _) =>
          (f"Uncompiled block, $missingStr", Some(path.asIndirect.toLocalPath))
        case ElaborateRecord.Block(path, _) => (f"Uncompiled block, $missingStr", Some(path.asIndirect.toLocalPath))
        case ElaborateRecord.Link(path) => (f"Uncompiled link, $missingStr", Some(path.asIndirect.toLocalPath))
        case ElaborateRecord.LinkArray(path) =>
          (f"Uncompiled link array, $missingStr", Some(path.asIndirect.toLocalPath))
        case ElaborateRecord.Parameter(containerPath, _, postfix, _) =>
          (f"Uncompiled parameter, $missingStr", Some((containerPath.asIndirect ++ postfix).toLocalPath))
        case _ => (f"Uncompiled internal element, $missingStr", None)
      }
      edgcompiler.ErrorRecord(
        path = path,
        kind = kind,
        name = "",
        details = ""
      )
    }
  }
  case class LibraryElement(path: DesignPath, target: ref.LibraryPath) extends CompilerError {
    override def toString: String = s"Unelaborated library element ${target.toSimpleString} @ $path"

    override def toIr: edgcompiler.ErrorRecord = {
      edgcompiler.ErrorRecord(
        path = Some(path.asIndirect.toLocalPath),
        kind = "Uncompiled library element",
        name = "",
        details = f"class ${target.toSimpleString}"
      )
    }
  }
  case class UndefinedPortArray(path: DesignPath, portType: ref.LibraryPath) extends CompilerError {
    override def toString: String = s"Undefined port array ${portType.toSimpleString} @ $path"

    override def toIr: edgcompiler.ErrorRecord = {
      edgcompiler.ErrorRecord(
        path = Some(path.asIndirect.toLocalPath),
        kind = "Undefined port array",
        name = "",
        details = f"port type ${portType.toSimpleString}"
      )
    }
  }

  // TODO partly redundant w/ LibraryElement error, which is a compiler-level error
  case class LibraryError(path: DesignPath, target: ref.LibraryPath, err: String) extends CompilerError {
    override def toString: String = s"Library error ${target.toSimpleString} @ $path: $err"

    override def toIr: edgcompiler.ErrorRecord = {
      edgcompiler.ErrorRecord(
        path = Some(path.asIndirect.toLocalPath),
        kind = "Library error",
        name = "",
        details = f"${target.toSimpleString}: err"
      )
    }
  }
  case class GeneratorError(path: DesignPath, target: ref.LibraryPath, err: String) extends CompilerError {
    override def toString: String = s"Generator error ${target.toSimpleString} @ $path: $err"

    override def toIr: edgcompiler.ErrorRecord = {
      edgcompiler.ErrorRecord(
        path = Some(path.asIndirect.toLocalPath),
        kind = "Generator error",
        name = "",
        details = f"${target.toSimpleString}: err"
      )
    }
  }
  case class RefinementSubclassError(path: DesignPath, refinedLibrary: ref.LibraryPath, designLibrary: ref.LibraryPath)
      extends CompilerError {
    override def toString: String =
      s"Invalid refinement ${refinedLibrary.toSimpleString} -> ${designLibrary.toSimpleString} @ $path"

    override def toIr: edgcompiler.ErrorRecord = {
      edgcompiler.ErrorRecord(
        path = Some(path.asIndirect.toLocalPath),
        kind = "Invalid refinement",
        name = "",
        details = f"${refinedLibrary.toSimpleString} -> ${designLibrary.toSimpleString}"
      )
    }
  }

  case class OverAssign(target: IndirectDesignPath, causes: Seq[OverAssignCause]) extends CompilerError {
    override def toString: String = s"Overassign to $target:\n" +
      s"${causes.map(x => s"- $x").mkString("\n")}"

    override def toIr: edgcompiler.ErrorRecord = {
      edgcompiler.ErrorRecord(
        path = Some(target.toLocalPath),
        kind = "Overassign",
        name = "",
        details = causes.map(_.toString).mkString(", ")
      )
    }
  }

  case class BadRef(path: DesignPath, ref: IndirectDesignPath) extends CompilerError {
    override def toIr: edgcompiler.ErrorRecord = {
      edgcompiler.ErrorRecord(
        path = Some(path.asIndirect.toLocalPath),
        kind = "Bad reference",
        name = "",
        details = ref.toLocalPath.toString
      )
    }
  }

  case class AbstractBlock(path: DesignPath, blockType: ref.LibraryPath) extends CompilerError {
    override def toString: String = s"Abstract block: $path (of type ${blockType.toSimpleString})"

    override def toIr: edgcompiler.ErrorRecord = {
      edgcompiler.ErrorRecord(
        path = Some(path.asIndirect.toLocalPath),
        kind = "Abstract block",
        name = "",
        details = f"block type ${blockType.toSimpleString}"
      )
    }
  }

  sealed trait AssertionError extends CompilerError
  case class FailedAssertion(
      root: DesignPath,
      constrName: String,
      value: expr.ValueExpr,
      result: ExprValue,
      compiler: Compiler
  ) extends AssertionError {
    override def toString: String =
      s"Failed assertion: $root.$constrName, ${ExprToString.apply(value)} => $result"

    override def toIr: edgcompiler.ErrorRecord = {
      edgcompiler.ErrorRecord(
        path = Some(root.asIndirect.toLocalPath),
        kind = "Failed assertion",
        name = constrName,
        details = s"${ExprToString.apply(value)} => $result"
      )
    }
  }
  case class MissingAssertion(
      root: DesignPath,
      constrName: String,
      value: expr.ValueExpr,
      missing: Set[IndirectDesignPath]
  ) extends AssertionError {
    override def toString: String =
      s"Unevaluated assertion: $root.$constrName: missing ${missing.mkString(", ")} in ${ExprToString.apply(value)}"

    override def toIr: edgcompiler.ErrorRecord = {
      edgcompiler.ErrorRecord(
        path = Some(root.asIndirect.toLocalPath),
        kind = "Unevaluated assertion",
        name = constrName,
        details = s"Missing ${missing.mkString(", ")} in ${ExprToString.apply(value)}"
      )
    }
  }

  case class InconsistentLinkArrayElements(
      root: DesignPath,
      linkPath: IndirectDesignPath,
      linkElements: ArrayValue[TextValue],
      blockPortPath: IndirectDesignPath,
      blockPortElements: ArrayValue[TextValue]
  ) extends CompilerError {
    override def toString: String =
      s"Inconsistent link array elements: $linkPath ($linkElements), $blockPortPath ($blockPortElements)"

    override def toIr: edgcompiler.ErrorRecord = {
      edgcompiler.ErrorRecord(
        path = Some(linkPath.toLocalPath),
        kind = "Inconsistent link array elements",
        name = "",
        details = s"$linkElements (link-side), $blockPortElements (block-side)"
      )
    }
  }

  sealed trait OverAssignCause
  object OverAssignCause {
    case class Assign(target: IndirectDesignPath, root: DesignPath, constrName: String, value: expr.ValueExpr)
        extends OverAssignCause {
      override def toString = s"Assign $target <- ${ExprToString(value)} @ $root.$constrName"
    }
    case class Equal(target: IndirectDesignPath, source: IndirectDesignPath) // TODO constraint info once we track that?
        extends OverAssignCause {
      override def toString = s"Equals $target = $source"
    }
  }
}
