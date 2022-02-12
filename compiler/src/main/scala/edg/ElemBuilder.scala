package edg

import com.google.protobuf.ByteString
import edg.EdgirUtils.SimpleLibraryPath


/** Convenience functions for building edg ir element trees with less proto boilerplate
  */
object ElemBuilder {
  import edgir.common.common
  import edgir.init.init
  import edgir.elem.elem
  import edgir.expr.expr
  import edgir.ref.ref
  import edgir.schema.schema
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
    // variation for map_extract
    def Exported(external: expr.ValueExpr, internal: ref.LocalPath): expr.ValueExpr = expr.ValueExpr(
      expr=expr.ValueExpr.Expr.Exported(expr.ExportedExpr(
        exteriorPort=Some(external), internalBlockPort=Some(ValueExpr.Ref(internal))))
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

    def Block(selfClass: String,
              superclasses: Seq[String] = Seq(),
              params: Map[String, init.ValInit] = Map(),
              paramDefaults: Map[String, expr.ValueExpr] = Map(),
              ports: Map[String, elem.PortLike] = Map(),
              blocks: Map[String, elem.BlockLike] = Map(),
              links: Map[String, elem.LinkLike] = Map(),
              constraints: Map[String, expr.ValueExpr] = Map(),
              prerefine: String = "",
             ): elem.BlockLike = elem.BlockLike(`type`=elem.BlockLike.Type.Hierarchy(elem.HierarchyBlock(
      params=params, paramDefaults=paramDefaults,
      ports=ports, blocks=blocks, links=links,
      constraints=constraints,
      selfClass=Some(LibraryPath(selfClass)),
      superclasses=superclasses map {
        LibraryPath(_)
      },
      prerefineClass=prerefine match {
        case "" => None
        case prerefine => Some(LibraryPath(prerefine))
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

    def Link(selfClass: String,
             params: Map[String, init.ValInit] = Map(),
             ports: Map[String, elem.PortLike] = Map(),
             links: Map[String, elem.LinkLike] = Map(),
             constraints: Map[String, expr.ValueExpr] = Map(),
            ): elem.LinkLike = elem.LinkLike(`type`=elem.LinkLike.Type.Link(elem.Link(
      params=params, ports=ports, links=links,
      constraints=constraints,
      selfClass=selfClass match {
        case "" => None
        case superclass => Some(LibraryPath(superclass))
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

    def Port(selfClass: String,
             params: Map[String, init.ValInit] = Map(),
             constraints: Map[String, expr.ValueExpr] = Map(),
            ): elem.PortLike = elem.PortLike(`is`=elem.PortLike.Is.Port(elem.Port(
      params=params,
      constraints=constraints,
      selfClass=selfClass match {
        case "" => None
        case selfClass => Some(LibraryPath(selfClass))
      }
    )))

    def Bundle(selfClass: String,
               params: Map[String, init.ValInit] = Map(),
               ports: Map[String, elem.PortLike] = Map(),
               constraints: Map[String, expr.ValueExpr] = Map(),
              ): elem.PortLike = elem.PortLike(`is`=elem.PortLike.Is.Bundle(elem.Bundle(
      params=params, ports=ports,
      constraints=constraints,
      selfClass=selfClass match {
        case "" => None
        case superclass => Some(LibraryPath(superclass))
      }
    )))

    // Unelaborated (unknown length) PortArray, containing just a superclass reference
    def Array(selfClass: String): elem.PortLike = elem.PortLike(`is`=elem.PortLike.Is.Array(elem.PortArray(
      selfClass=Some(LibraryPath(selfClass))
    )))

    // Fully elaborated (known length) PortArray
    def Array(selfClass: String, count: Int, port: elem.PortLike): elem.PortLike =
      elem.PortLike(`is`=elem.PortLike.Is.Array(elem.PortArray(
        selfClass=Some(LibraryPath(selfClass)),
        ports=(0 until count).map { i =>
          i.toString -> port
        }.toMap
      )))
  }

  def LibraryPath(name: String): ref.LibraryPath = ref.LibraryPath(target=Some(
    ref.LocalStep(step=ref.LocalStep.Step.Name(name))
  ))

  def Library(blocks: Seq[elem.BlockLike] = Seq(),
              links: Seq[elem.LinkLike] = Seq(),
              ports: Seq[elem.PortLike] = Seq()): schema.Library = {
    schema.Library(root=Some(schema.Library.NS(members=
      blocks.map { _.`type` match {
        case elem.BlockLike.Type.Hierarchy(block) =>
          block.getSelfClass.toFullString -> schema.Library.NS.Val(`type` = schema.Library.NS.Val.Type.HierarchyBlock(block))
        case block => throw new NotImplementedError(s"Unknown BlockLike in library $block")
      }}.toMap ++
      links.map { _.`type` match {
        case elem.LinkLike.Type.Link(link) =>
          link.getSelfClass.toFullString -> schema.Library.NS.Val(`type` = schema.Library.NS.Val.Type.Link (link))
        case link => throw new NotImplementedError(s"Unknown LinkLike in library $link")
      }}.toMap ++
      ports.map { _.`is` match {
        case elem.PortLike.Is.Port(port) =>
          port.getSelfClass.toFullString -> schema.Library.NS.Val(`type` = schema.Library.NS.Val.Type.Port(port))
        case elem.PortLike.Is.Bundle(bundle) =>
          bundle.getSelfClass.toFullString -> schema.Library.NS.Val(`type` = schema.Library.NS.Val.Type.Bundle(bundle))
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

  object Metadata {
    def Node(contents: Map[String, common.Metadata]): common.Metadata = {
      common.Metadata(meta=common.Metadata.Meta.Members(common.Metadata.Members(
        node=contents
      )))
    }
    def Text(contents: String): common.Metadata = {
      common.Metadata(meta=common.Metadata.Meta.TextLeaf(contents))
    }
    def Bytes(contents: ByteString): common.Metadata = {
      common.Metadata(meta=common.Metadata.Meta.BinLeaf(contents))
    }
    def Bytes(contents: Array[Byte]): common.Metadata = {
      common.Metadata(meta=common.Metadata.Meta.BinLeaf(ByteString.copyFrom(contents)))
    }
  }
}
