package edg.wir

import edgir.init.init
import edgir.elem.elem
import edgir.expr.expr

import scala.collection.{SeqMap, mutable}

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


  class BaseProtoToSeqMap[ProtoType, ValueType](items: Seq[ProtoType],
                                                nameExtractor: ProtoType => String,
                                                valueExtractor: ProtoType => Option[ValueType]) {
    def toSeqMap: SeqMap[String, ValueType] = {
      items.map { item =>
        nameExtractor(item) -> valueExtractor(item).get
      }.to(SeqMap)
    }
  }

  implicit class ParamProtoToSeqMap(items: Seq[elem.NamedValInit])
      extends BaseProtoToSeqMap[elem.NamedValInit, init.ValInit](items, _.name, _.value)

  implicit class PortProtoToSeqMap(items: Seq[elem.NamedPortLike])
      extends BaseProtoToSeqMap[elem.NamedPortLike, elem.PortLike](items, _.name, _.value)

  implicit class BlockProtoToSeqMap(items: Seq[elem.NamedBlockLike])
      extends BaseProtoToSeqMap[elem.NamedBlockLike, elem.BlockLike](items, _.name, _.value)

  implicit class LinkProtoToSeqMap(items: Seq[elem.NamedLinkLike])
      extends BaseProtoToSeqMap[elem.NamedLinkLike, elem.LinkLike](items, _.name, _.value)

  implicit class ConstraintProtoToSeqMap(items: Seq[elem.NamedValueExpr])
      extends BaseProtoToSeqMap[elem.NamedValueExpr, expr.ValueExpr](items, _.name, _.value)
}
