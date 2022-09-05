package edg.compiler

import edg.wir.{DesignPath, IndirectDesignPath}
import edgir.expr.expr

object ConstPropImplicit {
  // Adds addAssign* methods that have a default dummy root and name, useful for tests
  implicit class ConstPropDefaultImplicit(constProp: ConstProp) {
    def addAssignExpr(target: IndirectDesignPath, targetExpr: expr.ValueExpr): Unit = {
      constProp.addAssignExpr(target, targetExpr, DesignPath(), "")
    }

    def addAssignValue(target: IndirectDesignPath, value: ExprValue): Unit = {
      constProp.addAssignValue(target, value, DesignPath(), "")
    }

    def addAssignEqual(target: IndirectDesignPath, source: IndirectDesignPath): Unit = {
      constProp.addAssignEqual(target, source, DesignPath(), "")
    }
  }
}
