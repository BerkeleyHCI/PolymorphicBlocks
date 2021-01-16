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
      params=params, ports=ports, blocks=blocks, links=links,
      constraints=constraints,
      superclasses=superclasses.map { LibraryPath(_) }
    )))
  }

  object Link {
    def Library(path: ref.LibraryPath): elem.LinkLike = elem.LinkLike(`type`=elem.LinkLike.Type.LibElem(
      value=path
    ))
    def Library(name: String): elem.LinkLike = elem.LinkLike(`type`=elem.LinkLike.Type.LibElem(
      value=LibraryPath(name)
    ))

    def Link(params: Map[String, init.ValInit],
             ports: Map[String, elem.PortLike],
             links: Map[String, elem.LinkLike],
             constraints: Map[String, expr.ValueExpr] = Map(),
             superclasses: Seq[String] = Seq()
            ): elem.LinkLike = elem.LinkLike(`type`=elem.LinkLike.Type.Link(elem.Link(
      params=params, ports=ports, links=links,
      constraints=constraints,
      superclasses=superclasses.map { LibraryPath(_) }
    )))
  }

  object Port {
    def Library(path: ref.LibraryPath): elem.PortLike = elem.PortLike(`is`=elem.PortLike.Is.LibElem(
      value=path
    ))
    def Library(name: String): elem.PortLike = elem.PortLike(`is`=elem.PortLike.Is.LibElem(
      value=LibraryPath(name)
    ))

    def Port(params: Map[String, init.ValInit],
             constraints: Map[String, expr.ValueExpr] = Map(),
             superclasses: Seq[String] = Seq()
            ): elem.PortLike = elem.PortLike(`is`=elem.PortLike.Is.Port(elem.Port(
      params=params,
      constraints=constraints,
      superclasses=superclasses.map { LibraryPath(_) }
    )))

    def Bundle(params: Map[String, init.ValInit],
               ports: Map[String, elem.PortLike],
               constraints: Map[String, expr.ValueExpr] = Map(),
               superclasses: Seq[String] = Seq()
              ): elem.PortLike = elem.PortLike(`is`=elem.PortLike.Is.Bundle(elem.Bundle(
      params=params, ports=ports,
      constraints=constraints,
      superclasses=superclasses.map { LibraryPath(_) }
    )))

    // Unelaborated (unknown length) PortArray, containing just a superclass reference
    def Array(superclass: String): elem.PortLike = elem.PortLike(`is`=elem.PortLike.Is.Array(elem.PortArray(
      superclasses=Seq(LibraryPath(superclass))
    )))

    // Fully elaborated (known length) PortArray
    def Array(superclass: String, count: Int, port: elem.PortLike): elem.PortLike =
      elem.PortLike(`is`=elem.PortLike.Is.Array(elem.PortArray(
        superclasses=Seq(LibraryPath(superclass)),
        ports=(0 until count).map { i =>
          i.toString -> port
        }.toMap
      )))
  }

  def LibraryPath(name: String): ref.LibraryPath = ref.LibraryPath(target=Some(
    ref.LocalStep(step=ref.LocalStep.Step.Name(name))
  ))
}
