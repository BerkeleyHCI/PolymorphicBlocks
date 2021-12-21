package edg.wir

import edgir.common.common

object ProtoUtil {
  def getNameOrder(pb: Option[common.Metadata]): Seq[String] = {
    pb.getOrElse(common.Metadata()).meta.members match {
      case Some(members) => members.node.collect {
        case (name, meta) if meta.meta.namespaceOrder.isDefined => meta.getNamespaceOrder.names
      }.flatten.toSeq
      case None => Seq()
    }
  }

  def toNameOrder(nameOrder: Seq[String]): common.Metadata = {
    common.Metadata(meta=common.Metadata.Meta.NamespaceOrder(common.NamespaceOrder(names=nameOrder)))
  }
}
