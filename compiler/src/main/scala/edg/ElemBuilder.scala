package edg


/** Convenience functions for building edg ir element trees with less proto boilerplate
  */
object ElemBuilder {
  import edg.init.init
  import edg.elem.elem
  import edg.expr.expr
  import edg.ref.ref
  import edg.schema.schema
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

    def Block(params: Map[String, init.ValInit] = Map(),
              ports: Map[String, elem.PortLike] = Map(),
              blocks: Map[String, elem.BlockLike] = Map(),
              links: Map[String, elem.LinkLike] = Map(),
              constraints: Map[String, expr.ValueExpr] = Map(),
              superclass: String = "",
             ): elem.BlockLike = elem.BlockLike(`type`=elem.BlockLike.Type.Hierarchy(elem.HierarchyBlock(
      params=params, ports=ports, blocks=blocks, links=links,
      constraints=constraints,
      superclasses=superclass match {
        case "" => Seq()
        case superclass => Seq(LibraryPath(superclass))
      }
    )))
  }

  object Link {
    def Library(path: ref.LibraryPath): elem.LinkLike = elem.LinkLike(`type`=elem.LinkLike.Type.LibElem(
      value=path
    ))
    def Library(name: String): elem.LinkLike = elem.LinkLike(`type`=elem.LinkLike.Type.LibElem(
      value=LibraryPath(name)
    ))

    def Link(params: Map[String, init.ValInit] = Map(),
             ports: Map[String, elem.PortLike] = Map(),
             links: Map[String, elem.LinkLike] = Map(),
             constraints: Map[String, expr.ValueExpr] = Map(),
             superclass: String = "",
            ): elem.LinkLike = elem.LinkLike(`type`=elem.LinkLike.Type.Link(elem.Link(
      params=params, ports=ports, links=links,
      constraints=constraints,
      superclasses=superclass match {
        case "" => Seq()
        case superclass => Seq(LibraryPath(superclass))
      }
    )))
  }

  object Port {
    def Library(path: ref.LibraryPath): elem.PortLike = elem.PortLike(`is`=elem.PortLike.Is.LibElem(
      value=path
    ))
    def Library(name: String): elem.PortLike = elem.PortLike(`is`=elem.PortLike.Is.LibElem(
      value=LibraryPath(name)
    ))

    def Port(params: Map[String, init.ValInit] = Map(),
             constraints: Map[String, expr.ValueExpr] = Map(),
             superclass: String = ""
            ): elem.PortLike = elem.PortLike(`is`=elem.PortLike.Is.Port(elem.Port(
      params=params,
      constraints=constraints,
      superclasses=superclass match {
        case "" => Seq()
        case superclass => Seq(LibraryPath(superclass))
      }
    )))

    def Bundle(params: Map[String, init.ValInit] = Map(),
               ports: Map[String, elem.PortLike] = Map(),
               constraints: Map[String, expr.ValueExpr] = Map(),
               superclass: String = ""
              ): elem.PortLike = elem.PortLike(`is`=elem.PortLike.Is.Bundle(elem.Bundle(
      params=params, ports=ports,
      constraints=constraints,
      superclasses=superclass match {
        case "" => Seq()
        case superclass => Seq(LibraryPath(superclass))
      }
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

  def Library(blocks: Map[String, elem.BlockLike] = Map(),
              links: Map[String, elem.LinkLike] = Map(),
              ports: Map[String, elem.PortLike] = Map()): schema.Library = {
    schema.Library(root=Some(schema.Library.NS(members=
      blocks.mapValues { _.`type` match {
        case elem.BlockLike.Type.Hierarchy(block) =>
          schema.Library.NS.Val(`type` = schema.Library.NS.Val.Type.HierarchyBlock(block))
        case block => throw new NotImplementedError(s"Unknown BlockLike in library $block")
      }}.toMap ++
      links.mapValues { _.`type` match {
        case elem.LinkLike.Type.Link(link) =>
          schema.Library.NS.Val (`type` = schema.Library.NS.Val.Type.Link (link) )
        case link => throw new NotImplementedError(s"Unknown LinkLike in library $link")
      }}.toMap ++
      ports.mapValues { _.`is` match {
        case elem.PortLike.Is.Port(port) =>
          schema.Library.NS.Val(`type` = schema.Library.NS.Val.Type.Port(port))
        case port => throw new NotImplementedError(s"Unknown PortLike in library $port")
      }}.toMap
    )))
  }

  def Design(block: elem.BlockLike): schema.Design = {
    Design(block.`type`.asInstanceOf[elem.BlockLike.Type.Hierarchy].value)
  }
  def Design(block: elem.HierarchyBlock): schema.Design = {
    schema.Design(contents=Some(block))
  }
}
