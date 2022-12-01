package edg.wir

import edgir.init.init
import edgir.elem.elem
import edgir.expr.expr

import scala.collection.{SeqMap, mutable}

object ProtoUtil {
  // Implicit allowing toPb from the SeqMap that creates the Named* pair protos
  class BaseSeqMapToProto[ProtoType, ValueType](items: SeqMap[String, ValueType],
                                                ctor: (String, Option[ValueType]) => ProtoType) {
    def toPb: Seq[ProtoType] = {
      items.map { case (name, value) =>
        ctor(name, Some(value))
      }.toSeq
    }
  }

  implicit class ParamSeqMapToProto(items: SeqMap[String, init.ValInit])
      extends BaseSeqMapToProto[elem.NamedValInit, init.ValInit](items, elem.NamedValInit(_, _))

  implicit class PortSeqMapToProto(items: SeqMap[String, elem.PortLike])
      extends BaseSeqMapToProto[elem.NamedPortLike, elem.PortLike](items, elem.NamedPortLike(_, _))

  implicit class BlockSeqMapToProto(items: SeqMap[String, elem.BlockLike])
      extends BaseSeqMapToProto[elem.NamedBlockLike, elem.BlockLike](items, elem.NamedBlockLike(_, _))

  implicit class LinkSeqMapToProto(items: SeqMap[String, elem.LinkLike])
      extends BaseSeqMapToProto[elem.NamedLinkLike, elem.LinkLike](items, elem.NamedLinkLike(_, _))

  implicit class ConstraintSeqMapToProto(items: SeqMap[String, expr.ValueExpr])
      extends BaseSeqMapToProto[elem.NamedValueExpr, expr.ValueExpr](items, elem.NamedValueExpr(_, _))


  // Implicit allowing toPb from a (name, value) pair that creates the wrapping Named* pair proto
  class BaseTupleToProto[ProtoType, ValueType](item: (String, ValueType),
                                               ctor: (String, Option[ValueType]) => ProtoType) {
    def toPb: ProtoType = {
      ctor(item._1, Some(item._2))
    }
  }


  implicit class ParamTupleToProto(item: (String, init.ValInit))
      extends BaseTupleToProto[elem.NamedValInit, init.ValInit](item, elem.NamedValInit(_, _))

  implicit class PortTupleToProto(item: (String, elem.PortLike))
      extends BaseTupleToProto[elem.NamedPortLike, elem.PortLike](item, elem.NamedPortLike(_, _))

  implicit class BlockTupleToProto(item: (String, elem.BlockLike))
      extends BaseTupleToProto[elem.NamedBlockLike, elem.BlockLike](item, elem.NamedBlockLike(_, _))

  implicit class LinkTupleToProto(item: (String, elem.LinkLike))
      extends BaseTupleToProto[elem.NamedLinkLike, elem.LinkLike](item, elem.NamedLinkLike(_, _))

  implicit class ConstraintTupleToProto(item: (String, expr.ValueExpr))
      extends BaseTupleToProto[elem.NamedValueExpr, expr.ValueExpr](item, elem.NamedValueExpr(_, _))

  class BaseProtoToSeqMap[ProtoType, ValueType](items: Seq[ProtoType],
                                                nameExtractor: ProtoType => String,
                                                valueExtractor: ProtoType => Option[ValueType],
                                                ctor: (String, Option[ValueType]) => ProtoType) {
    def toSeqMap: SeqMap[String, ValueType] = {
      items.map { item =>
        nameExtractor(item) -> valueExtractor(item).get
      }.to(SeqMap)
    }

    def toMutableSeqMap: mutable.SeqMap[String, ValueType] = {
      items.map { item =>
        nameExtractor(item) -> valueExtractor(item).get
      }.to(mutable.SeqMap)
    }

    // This is named differently from filter because otherwise Seq.filter seems to be preferred
    def pairsFilter(fn: (String, ValueType) => Boolean): Seq[ProtoType] = {
      items.filter { item => fn(nameExtractor(item), valueExtractor(item).get) }
    }

    def pairsMap[KeyType, TargetType](fn: (String, ValueType) => (KeyType, TargetType)): SeqMap[KeyType, TargetType] = {
      items.map { item =>
        fn(nameExtractor(item), valueExtractor(item).get)
      }.to(SeqMap)
    }

    def pairsMap[TargetType](fn: (String, ValueType) => TargetType): Seq[TargetType] = {
      items.map { item =>
        fn(nameExtractor(item), valueExtractor(item).get)
      }
    }

    def pairsFlatMap[TargetType](fn: (String, ValueType) => IterableOnce[TargetType]): Iterable[TargetType] = {
      items.flatMap { item =>
        fn(nameExtractor(item), valueExtractor(item).get)
      }
    }

    def mapValues(fn: ValueType => ValueType): Seq[ProtoType] = {
      items.map { item => ctor(nameExtractor(item), Some(fn(valueExtractor(item).get))) }
    }

    // Gets the value by key
    def apply(key: String): ValueType = {
      valueExtractor(items.find(nameExtractor(_) == key).get).get
    }

    def indexOfKey(key: String): Int = {
      items.map(nameExtractor).indexOf(key)
    }
  }

  implicit class ParamProtoToSeqMap(items: Seq[elem.NamedValInit])
      extends BaseProtoToSeqMap[elem.NamedValInit, init.ValInit](items, _.name, _.value, elem.NamedValInit(_, _))

  implicit class PortProtoToSeqMap(items: Seq[elem.NamedPortLike])
      extends BaseProtoToSeqMap[elem.NamedPortLike, elem.PortLike](items, _.name, _.value, elem.NamedPortLike(_, _))

  implicit class BlockProtoToSeqMap(items: Seq[elem.NamedBlockLike])
      extends BaseProtoToSeqMap[elem.NamedBlockLike, elem.BlockLike](items, _.name, _.value, elem.NamedBlockLike(_, _))

  implicit class LinkProtoToSeqMap(items: Seq[elem.NamedLinkLike])
      extends BaseProtoToSeqMap[elem.NamedLinkLike, elem.LinkLike](items, _.name, _.value, elem.NamedLinkLike(_, _))

  implicit class ConstraintProtoToSeqMap(items: Seq[elem.NamedValueExpr])
      extends BaseProtoToSeqMap[elem.NamedValueExpr, expr.ValueExpr](items, _.name, _.value, elem.NamedValueExpr(_, _))
}
