package edg.wir

import edg.compiler.ExprValue
import edg.ref.ref
import edg.compiler.hdl


case class Refinements(
  classRefinements: Map[ref.LibraryPath, ref.LibraryPath] = Map(),
  instanceRefinements: Map[DesignPath, ref.LibraryPath] = Map(),
  classValues: Map[ref.LibraryPath, Seq[(ref.LocalPath, ExprValue)]] = Map(),  // class -> (internal path, value)
  instanceValues: Map[DesignPath, ExprValue] = Map()
)


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
        clsParam.getCls -> (clsParam.getParamPath -> ExprValue.fromLit(value.getValue))
    } }.groupBy(_._1).mapValues(_.map(_._2)).toMap

    val instanceValues = pb.values.collect { value => value.source match {
      case hdl.Refinements.Value.Source.Path(path) =>
        DesignPath() ++ path -> ExprValue.fromLit(value.getValue)
    } }.toMap

    Refinements(classRefinements, instanceRefinements, classValues, instanceValues)
  }
}
