package edg

sealed trait IrPort // to box Port-like types because of lack of union types in SScala
object IrPort {
  import edgir.elem.elem

  case class Port(pb: elem.Port) extends IrPort
  case class Bundle(pb: elem.Bundle) extends IrPort
}
