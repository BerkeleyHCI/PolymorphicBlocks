package edg

import org.scalatest.flatspec.AnyFlatSpec
import org.scalatest.matchers.should.Matchers._

class EdgirUtilsTest extends AnyFlatSpec {
  behavior.of("metadata utils")

  it should "roundtrip Map" in {
    val testdata = Map("a" -> "b", "c" -> "d")
    EdgirUtils.metaToStrMap(EdgirUtils.strMapToMeta(testdata)) should equal(testdata)
  }

  it should "roundtrip Seq" in {
    val testdata = Seq("a", "b", "c", "d")
//    EdgirUtils.metaToStrSeq(EdgirUtils.strSeqToMeta(testdata)) should equal(testdata)
  }
}
