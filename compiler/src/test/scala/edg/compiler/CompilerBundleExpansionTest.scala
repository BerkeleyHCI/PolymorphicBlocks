package edg.compiler

import org.scalatest._
import org.scalatest.flatspec.AnyFlatSpec
import matchers.should.Matchers._
import edg.ElemBuilder._
import edg.ExprBuilder.{Ref, ValInit, ValueExpr}
import edg.{CompilerTestUtil, wir}
import edg.wir.{IndirectDesignPath, IndirectStep}


/** Tests compiler Bundle expansion / elaboration, including nested links.
  */
class CompilerBundleExpansionTest extends AnyFlatSpec with CompilerTestUtil {
  val library = Library(
    ports = Seq(
      Port.Port(
        selfClass = "innerPort",
        params = Map(
          "param" -> ValInit.Integer,
        ),
      ),
      Port.Bundle(
        selfClass = "outerPort",
        params = Map(
          "param" -> ValInit.Integer,
        ),
        ports = Map(
          "inner" -> Port.Library("innerPort"),
        )
      ),
    ),
    blocks = Seq(
      Block.Block(
        selfClass = "sourceBlock",
        params = Map(
          "innerParam" -> ValInit.Integer,
          "outerParam" -> ValInit.Integer,
        ),
        ports = Map(
          "port" -> Port.Library("outerPort"),
        ),
        constraints = Map(
          "outerVal" -> Constraint.Assign(Ref("port", "param"), ValueExpr.Ref("outerParam")),
          "innerVal" -> Constraint.Assign(Ref("port", "inner", "param"), ValueExpr.Ref("innerParam")),
        )
      )
    ),
    links = Seq(
      Link.Link(
        selfClass = "innerLink",
        params = Map(
          "innerParam" -> ValInit.Integer,
        ),
        ports = Map(
          "innerPort" -> Port.Library("innerPort"),
        ),
        constraints = Map(
          "innerParamVal" -> ValueExpr.Assign(Ref("innerParam"), ValueExpr.Ref("innerPort", "param")),
        )
      ),
      Link.Link(
        selfClass = "outerLink",
        params = Map(
          "outerParam" -> ValInit.Integer,
        ),
        ports = Map(
          "outerPort" -> Port.Library("outerPort"),
        ),
        links = Map(
          "inner" -> Link.Library("innerLink"),
        ),
        constraints = Map(
          "innerExport" -> Constraint.Exported(Ref("outerPort", "inner"), Ref("inner", "innerPort")),
          "outerParamVal" -> ValueExpr.Assign(Ref("outerParam"), ValueExpr.Ref("outerPort", "param")),
        )
      ),
    )
  )

  "Compiler on design with bundles" should "expand structurally" in {
    val inputDesign = Design(Block.Block("topDesign",
      blocks = Map(
        "source" -> Block.Library("sourceBlock"),
      ),
      links = Map(
        "link" -> Link.Library("outerLink")
      ),
      constraints = Map(
        "sourceConnect" -> Constraint.Connected(Ref("source", "port"), Ref("link", "outerPort")),

        "outerParamVal" -> Constraint.Assign(Ref("source", "outerParam"), ValueExpr.Literal(42)),
        "innerParamVal" -> Constraint.Assign(Ref("source", "innerParam"), ValueExpr.Literal(7)),
      )
    ))
    val referenceElaborated = Design(Block.Block("topDesign",
      blocks = Map(
        "source" -> Block.Block(selfClass="sourceBlock",
          params = Map(
            "innerParam" -> ValInit.Integer,
            "outerParam" -> ValInit.Integer,
          ),
          ports = Map(
            "port" -> Port.Bundle(selfClass="outerPort",
              params = Map(
                "param" -> ValInit.Integer,
              ),
              ports = Map(
                "inner" -> Port.Port(selfClass="innerPort",
                  params = Map(
                    "param" -> ValInit.Integer,
                  ),
                ),
              )
            ),
          ),
          constraints = Map(
            "outerVal" -> Constraint.Assign(Ref("port", "param"), ValueExpr.Ref("outerParam")),
            "innerVal" -> Constraint.Assign(Ref("port", "inner", "param"), ValueExpr.Ref("innerParam")),
          )
        ),
      ),
      links = Map(
        "link" -> Link.Link(selfClass="outerLink",
          params = Map(
            "outerParam" -> ValInit.Integer,
          ),
          ports = Map(
            "outerPort" -> Port.Bundle(selfClass="outerPort",
              params = Map(
                "param" -> ValInit.Integer,
              ),
              ports = Map(
                "inner" -> Port.Port(selfClass="innerPort",
                  params = Map(
                    "param" -> ValInit.Integer,
                  ),
                ),
              )
            ),
          ),
          links = Map(
            "inner" -> Link.Link(selfClass="innerLink",
              params = Map(
                "innerParam" -> ValInit.Integer,
              ),
              ports = Map(
                "innerPort" -> Port.Port(selfClass="innerPort",
                  params = Map(
                    "param" -> ValInit.Integer,
                  ),
                ),
              ),
              constraints = Map(
                "innerParamVal" -> ValueExpr.Assign(Ref("innerParam"), ValueExpr.Ref("innerPort", "param")),
              )
            ),
          ),
          constraints = Map(
            "innerExport" -> Constraint.Exported(Ref("outerPort", "inner"), Ref("inner", "innerPort")),
            "outerParamVal" -> ValueExpr.Assign(Ref("outerParam"), ValueExpr.Ref("outerPort", "param")),
          )
        )
      ),
      constraints = Map(
        "sourceConnect" -> Constraint.Connected(Ref("source", "port"), Ref("link", "outerPort")),

        "outerParamVal" -> Constraint.Assign(Ref("source", "outerParam"), ValueExpr.Literal(42)),
        "innerParamVal" -> Constraint.Assign(Ref("source", "innerParam"), ValueExpr.Literal(7)),
      )
    ))
    val (compiler, compiled) = testCompile(inputDesign, library)

    // Smaller comparisons to allow more targeted error messages
    val compiledBlock = compiled.contents.get
    val referenceBlock = referenceElaborated.contents.get

    compiledBlock.blocks("source").`type`.hierarchy.get.ports("port") should
        equal(referenceBlock.blocks("source").`type`.hierarchy.get.ports("port"))
    compiledBlock.blocks("source") should equal(referenceBlock.blocks("source"))

    compiledBlock.links("link").`type`.link.get.ports("outerPort") should
        equal(referenceBlock.links("link").`type`.link.get.ports("outerPort"))
    compiledBlock.links("link").`type`.link.get.links("inner") should
        equal(referenceBlock.links("link").`type`.link.get.links("inner"))
    compiledBlock.links("link") should equal(referenceBlock.links("link"))

    compiledBlock.constraints should equal(referenceBlock.constraints)

    // The catch-all equivalence comparison
    compiled should equal(referenceElaborated)
  }

  "Compiler on design with bundles" should "propagate and evaluate values" in {
    val inputDesign = Design(Block.Block("topDesign",
      blocks = Map(
        "source" -> Block.Library("sourceBlock"),
      ),
      links = Map(
        "link" -> Link.Library("outerLink")
      ),
      constraints = Map(
        "sourceConnect" -> Constraint.Connected(Ref("source", "port"), Ref("link", "outerPort")),

        "outerParamVal" -> Constraint.Assign(Ref("source", "outerParam"), ValueExpr.Literal(42)),
        "innerParamVal" -> Constraint.Assign(Ref("source", "innerParam"), ValueExpr.Literal(7)),
      )
    ))
    val (compiler, compiled) = testCompile(inputDesign, library)

    // Check basic to-link value propagation
    compiler.getValue(IndirectDesignPath() + "link" + "outerParam") should equal(Some(IntValue(42)))
    compiler.getValue(IndirectDesignPath() + "link" + "inner" + "innerParam") should equal(Some(IntValue(7)))

    // Check the CONNECTED_LINK propagation
    compiler.getValue(IndirectDesignPath() + "source" + "port" + IndirectStep.ConnectedLink + "outerParam") should
        equal(Some(IntValue(42)))
    compiler.getValue(IndirectDesignPath() + "source" + "port" + IndirectStep.ConnectedLink + IndirectStep.Name) should
        equal(Some(TextValue("link")))
    compiler.getValue(IndirectDesignPath() + "source" + "port" + "inner" + IndirectStep.ConnectedLink + "innerParam") should
        equal(Some(IntValue(7)))
    compiler.getValue(IndirectDesignPath() + "source" + "port" + "inner" + IndirectStep.ConnectedLink + IndirectStep.Name) should
        equal(Some(TextValue("link.inner")))
  }
}
