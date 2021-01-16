package edg


/** Convenience functions for building edg ir element trees with less proto boilerplate
  */
object ElemBuilder {
  import edg.init.init
  import edg.elem.elem
  import edg.expr.expr
  import edg.ref.ref
  import ExprBuilder.ValueExpr

  // For constructing ValueExpr constraints typically used in top-level constraints
  // For other ValueExprs, see ExprBuilder
  object Constraint {
    def Connected(block: ref.LocalPath, link: ref.LocalPath): expr.ValueExpr = expr.ValueExpr(
      expr=expr.ValueExpr.Expr.Connected(expr.ConnectedExpr(
        blockPort=Some(ValueExpr.Ref(block)), linkPort=Some(ValueExpr.Ref(link))))
    )
    def Exported(external: ref.LocalPath, internal: ref.LocalPath): expr.ValueExpr = expr.ValueExpr(
      expr=expr.ValueExpr.Expr.Exported(expr.ExportedExpr(
        exteriorPort=Some(ValueExpr.Ref(external)), internalBlockPort=Some(ValueExpr.Ref(internal))))
    )
    def Assign(dst: ref.LocalPath, assignExpr: expr.ValueExpr): expr.ValueExpr = expr.ValueExpr(
      expr=expr.ValueExpr.Expr.Assign(expr.AssignExpr(
        dst=Some(dst), src=Some(assignExpr)))
    )
  }

  object Block {
    def Library(path: ref.LibraryPath): elem.BlockLike = elem.BlockLike(`type`=elem.BlockLike.Type.LibElem(
      value=path
    ))
    def Library(name: String): elem.BlockLike = elem.BlockLike(`type`=elem.BlockLike.Type.LibElem(
      value=LibraryPath(name)
    ))

    def Block(params: Map[String, init.ValInit],
              ports: Map[String, elem.PortLike],
              blocks: Map[String, elem.BlockLike],
              links: Map[String, elem.LinkLike],
              constraints: Map[String, expr.ValueExpr] = Map(),
              superclasses: Seq[String] = Seq()
             ): elem.BlockLike = elem.BlockLike(`type`=elem.BlockLike.Type.Hierarchy(elem.HierarchyBlock(
      params=params,
      ports=ports, blocks=blocks, links=links,
      constraints=constraints,
      superclasses=superclasses.map { LibraryPath(_) }
    )))
  }

  def LibraryPath(name: String): ref.LibraryPath = ref.LibraryPath(target=Some(
    ref.LocalStep(step=ref.LocalStep.Step.Name(name))
  ))
}
