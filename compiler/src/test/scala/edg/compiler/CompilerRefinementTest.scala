package edg.compiler

import org.scalatest._
import org.scalatest.flatspec.AnyFlatSpec
import matchers.should.Matchers._
import edg.ElemBuilder._
import edg.ExprBuilder.{Ref, ValInit}
import edg.wir


/** Basic test that tests block, link, and port expansion behavior, by matching the reference output exactly.
  */
class CompilerRefinementTest extends AnyFlatSpec {
  val library = Library(
    ports = Map(
      "port" -> Port.Port(),
    ),
    blocks = Map(
      "superclassBlock" -> Block.Block(
        params = Map(
          "superParam" -> ValInit.Integer,
        ),
        ports = Map(
          "port" -> Port.Library("port"),
        )
      ),
      "subclassBlock" -> Block.Block(
        superclass="superclassBlock",
        params = Map(
          "superParam" -> ValInit.Integer,
          "subParam" -> ValInit.Integer,
        ),
        ports = Map(
          "port" -> Port.Library("port"),
        )
      ),
      "block" -> Block.Block(  // specifically no superclass
        params = Map(
          "superParam" -> ValInit.Integer,
        ),
        ports = Map(
          "port" -> Port.Library("port"),
        )
      ),
    ),
    links = Map(
    )
  )

  "Compiler on design with subclass refinement" should "work" in {

  }

  "Compiler on design with subclass refinement" should "error if selected class is not a subclass" in {

  }

  "Compiler on design with instance refinement" should "work" in {

  }

  "Compiler on design with subclass values" should "work" in {

  }

  "Compiler on design with path values" should "work" in {

  }
}
