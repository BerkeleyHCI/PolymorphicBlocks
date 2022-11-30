package edg.wir

import edgir.init.init
import edgir.elem.elem
import edgir.expr.expr

import scala.collection.SeqMap

object ProtoUtil {
  class BaseSeqMapToProto[ProtoType, ValueType](items: SeqMap[String, ValueType],
                                                ctor: (String, Option[ValueType]) => ProtoType) {
    def toPb: Seq[ProtoType] = {
      items.map { case (name, value) =>
        ctor(name, Some(value))
      }.toSeq
    }
  }

  implicit class ParamSeqMapToProto(items: SeqMap[String, init.ValInit])
      extends BaseSeqMapToProto[elem.NamedValInit, init.ValInit](items, elem.NamedValInit(_, _)) {
  }

  implicit class PortSeqMapToProto(items: SeqMap[String, elem.PortLike])
      extends BaseSeqMapToProto[elem.NamedPortLike, elem.PortLike](items, elem.NamedPortLike(_, _)) {
  }

  implicit class BlockSeqMapToProto(items: SeqMap[String, elem.BlockLike])
      extends BaseSeqMapToProto[elem.NamedBlockLike, elem.BlockLike](items, elem.NamedBlockLike(_, _)) {
  }

  implicit class LinkSeqMapToProto(items: SeqMap[String, elem.LinkLike])
      extends BaseSeqMapToProto[elem.NamedLinkLike, elem.LinkLike](items, elem.NamedLinkLike(_, _)) {
  }

  implicit class ConstraintSeqMapToProto(items: SeqMap[String, expr.ValueExpr])
      extends BaseSeqMapToProto[elem.NamedValueExpr, expr.ValueExpr](items, elem.NamedValueExpr(_, _)) {
  }
}
