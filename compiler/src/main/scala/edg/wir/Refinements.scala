package edg.wir

import edg.compiler.ExprValue
import edg.ref.ref
import edg.compiler.{compiler => edgcompiler}


case class Refinements(
  classRefinements: Map[ref.LibraryPath, ref.LibraryPath] = Map(),
  instanceRefinements: Map[DesignPath, ref.LibraryPath] = Map(),
  classValues: Map[ref.LibraryPath, Seq[(ref.LocalPath, ExprValue)]] = Map(),  // class -> (internal path, value)
  instanceValues: Map[DesignPath, ExprValue] = Map()
)


object Refinements {
  def fromCompilerRequest(request: edgcompiler.CompilerRequest): Refinements = {
    val classRefinements = request.refinements.collect { refinement => refinement.source match {
      case edgcompiler.CompilerRequest.Refinement.Source.Cls(cls) =>
        cls -> refinement.getReplacement
    } }.toMap
    val instanceRefinements = request.refinements.collect { refinement => refinement.source match {
      case edgcompiler.CompilerRequest.Refinement.Source.Path(path) =>
        DesignPath.root ++ path -> refinement.getReplacement
    } }.toMap
    val classValues = request.values.collect { value => value.source match {
      case edgcompiler.CompilerRequest.Value.Source.ClsParam(clsParam) =>
        clsParam.getCls -> (clsParam.getParamPath -> ExprValue.fromLit(value.getValue))
    } }.groupBy(_._1).mapValues(_.map(_._2)).toMap

    val instanceValues = request.values.collect { value => value.source match {
      case edgcompiler.CompilerRequest.Value.Source.Path(path) =>
        DesignPath.root ++ path -> ExprValue.fromLit(value.getValue)
    } }.toMap

    Refinements(classRefinements, instanceRefinements, classValues, instanceValues)
  }
}
