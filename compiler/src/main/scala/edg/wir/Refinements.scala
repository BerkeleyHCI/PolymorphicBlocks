package edg.wir

import edgir.ref.ref
import edgrpc.hdl.hdl
import edg.compiler.{ExprEvaluate, ExprValue}
import edg.util.MapUtils


case class Refinements(
  classRefinements: Map[ref.LibraryPath, ref.LibraryPath] = Map(),
  instanceRefinements: Map[DesignPath, ref.LibraryPath] = Map(),
  classValues: Map[ref.LibraryPath, Map[ref.LocalPath, ExprValue]] = Map(),  // class -> (internal path -> value)
  instanceValues: Map[DesignPath, ExprValue] = Map()
) {
  // Append another set of refinements on top of this one, erroring out in case of a conflict
  def ++(that: Refinements): Refinements = {
    val combinedClassValues = (classValues.toSeq ++ that.classValues.toSeq)  // this one is merge-able one level down
        .groupBy(_._1)
        .map { case (className, classPathValues) =>
      className -> MapUtils.mergeMapSafe(classPathValues.map(_._2):_*)
    }
    Refinements(
      classRefinements = MapUtils.mergeMapSafe(classRefinements, that.classRefinements),
      instanceRefinements = MapUtils.mergeMapSafe(instanceRefinements, that.instanceRefinements),
      classValues = combinedClassValues,
      instanceValues = MapUtils.mergeMapSafe(instanceValues, that.instanceValues),
    )
  }

  // separates the refinements into one not containing (only) the set blocks and params, and one not.
  def partitionBy(blocks: Set[DesignPath], params: Set[DesignPath]): (Refinements, Refinements) = {
    val (containsBlocks, otherBlocks) = instanceRefinements.partition { case (path, _) => blocks.contains(path) }
    val (containsParams, otherParams) = instanceValues.partition { case (path, _) => params.contains(path) }
    val containsRefinement = Refinements(Map(), containsBlocks, Map(), containsParams)
    val otherRefinement = Refinements(
      classRefinements, otherBlocks, classValues, otherParams
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
            replacement = Some(target))
        }.toSeq ++ instanceRefinements.map { case (path, target) =>
          hdl.Refinements.Subclass(
            source = hdl.Refinements.Subclass.Source.Path(path.asIndirect.toLocalPath),
            replacement = Some(target))
        },
      values =
        classValues.flatMap { case (source, subpathValue) =>
          subpathValue.map { case (subpath, value) =>
            hdl.Refinements.Value(
              source = hdl.Refinements.Value.Source.ClsParam(
                hdl.Refinements.Value.ClassParamPath(cls = Some(source), paramPath = Some(subpath))
              ),
              value = Some(value.toLit))
          }
        }.toSeq ++ instanceValues.map { case (path, value) =>
          hdl.Refinements.Value(
            source = hdl.Refinements.Value.Source.Path(path.asIndirect.toLocalPath),
            value = Some(value.toLit))
        }
    )
  }
}


object Refinements {
  def apply(pb: hdl.Refinements): Refinements = {
    val classRefinements = pb.subclasses.collect { refinement => refinement.source match {
      case hdl.Refinements.Subclass.Source.Cls(cls) =>
        cls -> refinement.getReplacement
    } }.toMap
    val instanceRefinements = pb.subclasses.collect { refinement => refinement.source match {
      case hdl.Refinements.Subclass.Source.Path(path) =>
        DesignPath() ++ path -> refinement.getReplacement
    } }.toMap
    val classValues = pb.values.collect { value => value.source match {
      case hdl.Refinements.Value.Source.ClsParam(clsParam) =>
        clsParam.getCls -> (clsParam.getParamPath -> ExprEvaluate.evalLiteral(value.getValue))
    } }.groupBy(_._1).view.mapValues(_.map(_._2).toMap).toMap

    val instanceValues = pb.values.collect { value => value.source match {
      case hdl.Refinements.Value.Source.Path(path) =>
        DesignPath() ++ path -> ExprEvaluate.evalLiteral(value.getValue)
    } }.toMap

    Refinements(classRefinements, instanceRefinements, classValues, instanceValues)
  }
}
