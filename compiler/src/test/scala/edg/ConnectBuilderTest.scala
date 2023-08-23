package edg

import edg.ElemBuilder.Constraint
import edg.ExprBuilder.Ref
import org.scalatest.flatspec.AnyFlatSpec
import org.scalatest.matchers.should.Matchers._

class ConnectBuilderTest extends AnyFlatSpec {
  behavior.of("ConnectBuilder")

  it should "decode connections" in {
    ConnectTypes.fromConnect(Constraint.Connected(Ref("source", "port"), Ref("link", "source"))) should equal(Some(Seq(
      ConnectTypes.BlockPort("source", "port")
    )))
    ConnectTypes.fromConnect(
      Constraint.Connected(Ref("sink0", "port"), Ref.Allocate(Ref("link", "sinks")))
    ) should equal(Some(Seq(
      ConnectTypes.BlockPort("sink0", "port")
    )))
    ConnectTypes.fromConnect(Constraint.Exported(Ref("source", "a"), Ref("a", "source"))) should equal(Some(Seq(
      ConnectTypes.BoundaryPort("source", Seq("a")),
      ConnectTypes.BlockPort("a", "source")
    )))
  }
}
