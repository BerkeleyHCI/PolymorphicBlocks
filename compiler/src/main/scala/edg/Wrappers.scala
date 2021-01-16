package edg

sealed trait IrPorts  // to box Port-like types because of lack of union types in SScala
object IrPorts {
  import edg.elem.elem

  case class Port(pb: elem.Port) extends IrPorts
  case class Bundle(pb: elem.Bundle) extends IrPorts
}
