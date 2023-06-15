package edg.wir

import edg.EdgirUtils.SimpleLibraryPath
import edgir.ref.ref
import edgrpc.hdl.hdl
import edg.compiler.{ExprEvaluate, ExprToString, ExprValue}
import edg.util.MapUtils

case class Refinements(
    classRefinements: Map[ref.LibraryPath, ref.LibraryPath] = Map(),
    instanceRefinements: Map[DesignPath, ref.LibraryPath] = Map(),
    classValues: Map[(ref.LibraryPath, ref.LocalPath), ExprValue] = Map(), // (class, internal path -> value)
    instanceValues: Map[DesignPath, ExprValue] = Map(),
    instanceAssigns: Map[DesignPath, DesignPath] = Map()
) {
  override def toString: String = {
    val allStrs = Seq(
      if (classRefinements.nonEmpty) {
        val elts = classRefinements.map { case (dstCls, cls) =>
          s"${dstCls.toSimpleString}<-${cls.toSimpleString}"
        }.mkString(", ")
        Some(s"classRefinements($elts)")
      } else {
        None
      },
      if (instanceRefinements.nonEmpty) {
        val elts = instanceRefinements.map { case (dst, cls) =>
          s"${dst}<-${cls.toSimpleString}"
        }.mkString(", ")
        Some(s"instanceRefinements($elts)")
      } else {
        None
      },
      if (classValues.nonEmpty) {
        val elts = classValues.map { case ((target, subpath), expr) =>
          s"${target.toSimpleString}:${ExprToString(subpath)}<-${expr.toStringValue}"
        }.mkString(", ")
        Some(s"classValues($elts)")
      } else {
        None
      },
      if (instanceValues.nonEmpty) {
        val elts = instanceValues.map { case (target, expr) =>
          s"$target<-${expr.toStringValue}"
        }.mkString(", ")
        Some(s"instanceValues($elts)")
      } else {
        None
      },
      if (instanceValues.nonEmpty) {
        val elts = instanceAssigns.map { case (target, source) =>
          s"$target<-$source"
        }.mkString(", ")
        Some(s"instanceAssigns($elts)")
      } else {
        None
      }
    )

    s"Refinements(${allStrs.mkString(", ")}"
  }

  // Append another set of refinements on top of this one, erroring out in case of a conflict
  def ++(that: Refinements): Refinements = {
    Refinements(
      classRefinements = MapUtils.mergeMapSafe(classRefinements, that.classRefinements),
      instanceRefinements = MapUtils.mergeMapSafe(instanceRefinements, that.instanceRefinements),
      classValues = MapUtils.mergeMapSafe(classValues, that.classValues),
      instanceValues = MapUtils.mergeMapSafe(instanceValues, that.instanceValues),
      instanceAssigns = MapUtils.mergeMapSafe(instanceAssigns, that.instanceAssigns),
    )
  }

  // separates the refinements into one not containing (only) the set blocks and params, and one not.
  def partitionBy(
      blocks: Set[DesignPath],
      params: Set[DesignPath],
      classParams: Set[(ref.LibraryPath, ref.LocalPath)]
  ): (Refinements, Refinements) = {
    val (containsBlocks, otherBlocks) = instanceRefinements.partition { case (path, _) => blocks.contains(path) }
    val (containsParams, otherParams) = instanceValues.partition { case (path, _) => params.contains(path) }
    val (containsParamAssigns, otherParamAssigns) = instanceAssigns.partition { case (path, _) =>
      params.contains(path)
    }
    val (containsClassParams, otherClassParams) = classValues.partition { case (classPath, _) =>
      classParams.contains(classPath)
    }
    val containsRefinement = Refinements(
      Map(),
      containsBlocks,
      containsClassParams,
      containsParams,
      containsParamAssigns
    )
    val otherRefinement = Refinements(
      classRefinements,
      otherBlocks,
      otherClassParams,
      otherParams,
      otherParamAssigns
    )

    (containsRefinement, otherRefinement)
  }

  def isEmpty: Boolean = {
    classRefinements.isEmpty && instanceRefinements.isEmpty && classValues.isEmpty && instanceValues.isEmpty
  }

  def toPb: hdl.Refinements = {
    hdl.Refinements(
      subclasses =
        classRefinements.map { case (source, target) =>
          hdl.Refinements.Subclass(
            source = hdl.Refinements.Subclass.Source.Cls(source),
            replacement = Some(target)
          )
        }.toSeq ++ instanceRefinements.map { case (path, target) =>
          hdl.Refinements.Subclass(
            source = hdl.Refinements.Subclass.Source.Path(path.asIndirect.toLocalPath),
            replacement = Some(target)
          )
        },
      values =
        classValues.map { case ((source, subpath), value) =>
          hdl.Refinements.Value(
            source = hdl.Refinements.Value.Source.ClsParam(
              hdl.Refinements.Value.ClassParamPath(cls = Some(source), paramPath = Some(subpath))
            ),
            value = hdl.Refinements.Value.Value.Expr(value.toLit)
          )
        }.toSeq ++ instanceValues.map { case (path, value) =>
          hdl.Refinements.Value(
            source = hdl.Refinements.Value.Source.Path(path.asIndirect.toLocalPath),
            value = hdl.Refinements.Value.Value.Expr(value.toLit)
          )
        } ++ instanceAssigns.map { case (path, source) =>
          hdl.Refinements.Value(
            source = hdl.Refinements.Value.Source.Path(path.asIndirect.toLocalPath),
            value = hdl.Refinements.Value.Value.Param(source.asIndirect.toLocalPath)
          )
        }
    )
  }
}

object Refinements {
  def apply(pb: hdl.Refinements): Refinements = {
    val classRefinements = pb.subclasses.collect { refinement =>
      refinement.source match {
        case hdl.Refinements.Subclass.Source.Cls(cls) =>
          cls -> refinement.getReplacement
      }
    }.toMap
    val instanceRefinements = pb.subclasses.collect { refinement =>
      refinement.source match {
        case hdl.Refinements.Subclass.Source.Path(path) =>
          DesignPath() ++ path -> refinement.getReplacement
      }
    }.toMap
    val classValues = pb.values.collect { value =>
      (value.source, value.value) match {
        case (hdl.Refinements.Value.Source.ClsParam(clsParam), hdl.Refinements.Value.Value.Expr(value)) =>
          (clsParam.getCls, clsParam.getParamPath) -> ExprEvaluate.evalLiteral(value)
        case (hdl.Refinements.Value.Source.ClsParam(_), _) =>
          throw new IllegalArgumentException("class-based value from parameter refinements not supported")
      }
    }.toMap
    val instanceValues = pb.values.collect { value =>
      (value.source, value.value) match {
        case (hdl.Refinements.Value.Source.Path(path), hdl.Refinements.Value.Value.Expr(value)) =>
          DesignPath() ++ path -> ExprEvaluate.evalLiteral(value)
      }
    }.toMap
    val instanceAssigns = pb.values.collect { value =>
      (value.source, value.value) match {
        case (hdl.Refinements.Value.Source.Path(path), hdl.Refinements.Value.Value.Param(paramPath)) =>
          DesignPath() ++ path -> (DesignPath() ++ paramPath)
      }
    }.toMap

    Refinements(classRefinements, instanceRefinements, classValues, instanceValues, instanceAssigns)
  }
}
