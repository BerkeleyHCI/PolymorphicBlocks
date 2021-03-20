package edg


/** Convenience functions for building edg ir expression trees with less proto boilerplate
  */
object ExprBuilder {
  import edg.common.common
  import edg.expr.expr
  import edg.init.init
  import edg.lit.lit
  import edg.ref.ref

  object ValueExpr {
    def Literal(literal: lit.ValueLit): expr.ValueExpr = expr.ValueExpr(expr = expr.ValueExpr.Expr.Literal(literal))

    def Literal(value: Float): expr.ValueExpr = Literal(ExprBuilder.Literal.Floating(value))

    def Literal(value: Double): expr.ValueExpr = Literal(value.toFloat) // convenience method
    def Literal(value: BigInt): expr.ValueExpr = Literal(ExprBuilder.Literal.Integer(value))

    def Literal(value: Int): expr.ValueExpr = Literal(ExprBuilder.Literal.Integer(BigInt(value))) // convenience method
    def Literal(value: Boolean): expr.ValueExpr = Literal(ExprBuilder.Literal.Boolean(value))

    def Literal(value: String): expr.ValueExpr = Literal(ExprBuilder.Literal.Text(value))

    def Literal(valueMin: Float, valueMax: Float): expr.ValueExpr =
      Literal(ExprBuilder.Literal.Range(valueMin, valueMax))

    def Literal(valueMin: Double, valueMax: Double): expr.ValueExpr = // convenience method
      Literal(valueMin.toFloat, valueMax.toFloat)

    def BinOp(op: expr.BinaryExpr.Op, lhs: expr.ValueExpr, rhs: expr.ValueExpr): expr.ValueExpr = expr.ValueExpr(
      expr = expr.ValueExpr.Expr.Binary(expr.BinaryExpr(op = op, lhs = Some(lhs), rhs = Some(rhs)))
    )

    def Reduce(op: expr.ReductionExpr.Op, vals: expr.ValueExpr): expr.ValueExpr = expr.ValueExpr(
      expr = expr.ValueExpr.Expr.Reduce(expr.ReductionExpr(op = op, vals = Some(vals)))
    )

    def IfThenElse(cond: expr.ValueExpr, tru: expr.ValueExpr, fal: expr.ValueExpr): expr.ValueExpr = expr.ValueExpr(
      expr = expr.ValueExpr.Expr.IfThenElse(expr.IfThenElseExpr(cond = Some(cond), tru = Some(tru), fal = Some(fal)))
    )

    object MapExtract {
      def apply(container: ref.LocalPath, path: ref.LocalPath): expr.ValueExpr = expr.ValueExpr(
        expr = expr.ValueExpr.Expr.MapExtract(expr.MapExtractExpr(container = Some(Ref(container)), path = Some(path)))
      )
      def apply(container: ref.LocalPath, path: String*): expr.ValueExpr = expr.ValueExpr(
        expr = expr.ValueExpr.Expr.MapExtract(expr.MapExtractExpr(container = Some(Ref(container)),
          path = Some(ExprBuilder.Ref(path: _*))))
      )

      def unapply(that: expr.ValueExpr): Option[(expr.ValueExpr, ref.LocalPath)] = that.expr match {
        case expr.ValueExpr.Expr.MapExtract(expr) => Some(expr.container.get, expr.path.get)
        case _ => None
      }
    }

    object Ref {
      def apply(path: ref.LocalPath): expr.ValueExpr = expr.ValueExpr(
        expr = expr.ValueExpr.Expr.Ref(path)
      )
      def apply(path: String*): expr.ValueExpr = expr.ValueExpr( // convenience method
        expr = expr.ValueExpr.Expr.Ref(ExprBuilder.Ref(path: _*))
      )

      def unapply(that: expr.ValueExpr): Option[Seq[String]] = that.expr match {
        case expr.ValueExpr.Expr.Ref(ref) => ExprBuilder.Ref.unapply(ref)
        case _ => None
      }
    }

    object RefAllocate {
      def unapply(that: expr.ValueExpr): Option[Seq[String]] = that.expr match {
        case expr.ValueExpr.Expr.Ref(that) => that.steps match {
          case init :+ ExprBuilder.Ref.AllocateStep =>
            localPathStepsNameOption(init)
          case _ => None
        }
        case _ => None
      }
    }

    def Assign(dst: ref.LocalPath, src: expr.ValueExpr): expr.ValueExpr = expr.ValueExpr(
      expr = expr.ValueExpr.Expr.Assign(expr.AssignExpr(dst=Some(dst), src=Some(src)))
    )
  }

  object Literal {
    def Floating(value: Double): lit.ValueLit = Floating(value.toFloat)
    def Floating(value: Float): lit.ValueLit = lit.ValueLit(`type` = lit.ValueLit.Type.Floating(lit.FloatLit(value)))

    def Integer(value: BigInt): lit.ValueLit = lit.ValueLit(`type` = lit.ValueLit.Type.Integer(lit.IntLit(value.toLong)))

    def Boolean(value: Boolean): lit.ValueLit = lit.ValueLit(`type` = lit.ValueLit.Type.Boolean(lit.BoolLit(value)))

    def Text(value: String): lit.ValueLit = lit.ValueLit(`type` = lit.ValueLit.Type.Text(lit.TextLit(value)))

    def Range(valueMin: Float, valueMax: Float): lit.ValueLit = {
      require((valueMin <= valueMax) || (valueMin.isNaN || valueMax.isNaN), s"malformed range ($valueMin, $valueMax)")
      lit.ValueLit(`type` = lit.ValueLit.Type.Range(lit.RangeLit(
        minimum = Some(Floating(valueMin)), maximum = Some(Floating(valueMax)))))
    }
  }

  private def localPathStepsNameOption(steps: Seq[ref.LocalStep]): Option[Seq[String]] = {
    val names = steps.collect { step => step.step match {
      case ref.LocalStep.Step.Name(name) => name
    }}
    if (names.length == steps.length) {
      Some(names)
    } else {
      None
    }
  }

  object Ref {
    val AllocateStep = ref.LocalStep(step=ref.LocalStep.Step.ReservedParam(ref.Reserved.ALLOCATE))
    val IsConnectedStep = ref.LocalStep(step=ref.LocalStep.Step.ReservedParam(ref.Reserved.IS_CONNECTED))

    def apply(path: String*): ref.LocalPath = {
      ref.LocalPath(steps = path.map { step =>
        ref.LocalStep(step = ref.LocalStep.Step.Name(step))
      })
    }

    def unapply(that: ref.LocalPath): Option[Seq[String]] = {
      localPathStepsNameOption(that.steps)
    }

    object Allocate {
      def apply(prefix: ref.LocalPath): ref.LocalPath = {
        ref.LocalPath(steps = prefix.steps :+ AllocateStep)
      }
      def unapply(that: ref.LocalPath): Option[ref.LocalPath] = that.steps match {
        case init :+ ExprBuilder.Ref.AllocateStep => Some(ref.LocalPath(steps=init))
        case _ => None
      }
    }

    object IsConnected {
      def apply(prefix: ref.LocalPath): ref.LocalPath = {
        ref.LocalPath(steps = prefix.steps :+ IsConnectedStep)
      }
      def unapply(that: ref.LocalPath): Option[ref.LocalPath] = that.steps match {
        case init :+ ExprBuilder.Ref.IsConnectedStep => Some(ref.LocalPath(steps=init))
        case _ => None
      }
    }
  }

  object ValInit {
    val Floating: init.ValInit = init.ValInit(`val` = init.ValInit.Val.Floating(common.Empty()))
    val Integer: init.ValInit = init.ValInit(`val` = init.ValInit.Val.Integer(common.Empty()))
    val Boolean: init.ValInit = init.ValInit(`val` = init.ValInit.Val.Boolean(common.Empty()))
    val Text: init.ValInit = init.ValInit(`val` = init.ValInit.Val.Text(common.Empty()))
    val Range: init.ValInit = init.ValInit(`val` = init.ValInit.Val.Range(common.Empty()))
  }
}
