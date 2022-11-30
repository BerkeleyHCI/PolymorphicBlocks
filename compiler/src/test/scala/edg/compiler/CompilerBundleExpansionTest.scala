package edg.compiler

import org.scalatest._
import org.scalatest.flatspec.AnyFlatSpec
import matchers.should.Matchers._
import edg.ElemBuilder._
import edg.ExprBuilder.{Ref, ValInit, ValueExpr}
import edg.wir.ProtoUtil.{BlockProtoToSeqMap, LinkProtoToSeqMap, PortProtoToSeqMap}
import edg.{CompilerTestUtil, wir}
import edg.wir.{IndirectDesignPath, IndirectStep}

import scala.collection.SeqMap


/** Tests compiler Bundle expansion / elaboration, including nested links.
  */
class CompilerBundleExpansionTest extends AnyFlatSpec with CompilerTestUtil {
  val library = Library(
    ports = Seq(
      Port.Port(
        selfClass = "innerPort",
        params = SeqMap(
          "param" -> ValInit.Integer,
        ),
      ),
      Port.Bundle(
        selfClass = "outerPort",
        params = SeqMap(
          "param" -> ValInit.Integer,
        ),
        ports = SeqMap(
          "inner" -> Port.Library("innerPort"),
        )
      ),
    ),
    blocks = Seq(
      Block.Block(
        selfClass = "sourceBlock",
        params = SeqMap(
          "innerParam" -> ValInit.Integer,
          "outerParam" -> ValInit.Integer,
        ),
        ports = SeqMap(
          "port" -> Port.Library("outerPort"),
        ),
        constraints = SeqMap(
          "outerVal" -> Constraint.Assign(Ref("port", "param"), ValueExpr.Ref("outerParam")),
          "innerVal" -> Constraint.Assign(Ref("port", "inner", "param"), ValueExpr.Ref("innerParam")),
        )
      )
    ),
    links = Seq(
      Link.Link(
        selfClass = "innerLink",
        params = SeqMap(
          "innerParam" -> ValInit.Integer,
        ),
        ports = SeqMap(
          "innerPort" -> Port.Library("innerPort"),
        ),
        constraints = SeqMap(
          "innerParamVal" -> ValueExpr.Assign(Ref("innerParam"), ValueExpr.Ref("innerPort", "param")),
        )
      ),
      Link.Link(
        selfClass = "outerLink",
        params = SeqMap(
          "outerParam" -> ValInit.Integer,
        ),
        ports = SeqMap(
          "outerPort" -> Port.Library("outerPort"),
        ),
        links = SeqMap(
          "inner" -> Link.Library("innerLink"),
        ),
        constraints = SeqMap(
          "innerExport" -> Constraint.Exported(Ref("outerPort", "inner"), Ref("inner", "innerPort")),
          "outerParamVal" -> ValueExpr.Assign(Ref("outerParam"), ValueExpr.Ref("outerPort", "param")),
        )
      ),
    )
  )

  "Compiler on design with bundles" should "expand structurally" in {
    val inputDesign = Design(Block.Block("topDesign",
      blocks = SeqMap(
        "source" -> Block.Library("sourceBlock"),
      ),
      links = SeqMap(
        "link" -> Link.Library("outerLink")
      ),
      constraints = SeqMap(
        "sourceConnect" -> Constraint.Connected(Ref("source", "port"), Ref("link", "outerPort")),

        "outerParamVal" -> Constraint.Assign(Ref("source", "outerParam"), ValueExpr.Literal(42)),
        "innerParamVal" -> Constraint.Assign(Ref("source", "innerParam"), ValueExpr.Literal(7)),
      )
    ))
    val referenceElaborated = Design(Block.Block("topDesign",
      blocks = SeqMap(
        "source" -> Block.Block(selfClass="sourceBlock",
          params = SeqMap(
            "innerParam" -> ValInit.Integer,
            "outerParam" -> ValInit.Integer,
          ),
          ports = SeqMap(
            "port" -> Port.Bundle(selfClass="outerPort",
              params = SeqMap(
                "param" -> ValInit.Integer,
              ),
              ports = SeqMap(
                "inner" -> Port.Port(selfClass="innerPort",
                  params = SeqMap(
                    "param" -> ValInit.Integer,
                  ),
                ),
              )
            ),
          ),
          constraints = SeqMap(
            "outerVal" -> Constraint.Assign(Ref("port", "param"), ValueExpr.Ref("outerParam")),
            "innerVal" -> Constraint.Assign(Ref("port", "inner", "param"), ValueExpr.Ref("innerParam")),
          )
        ),
      ),
      links = SeqMap(
        "link" -> Link.Link(selfClass="outerLink",
          params = SeqMap(
            "outerParam" -> ValInit.Integer,
          ),
          ports = SeqMap(
            "outerPort" -> Port.Bundle(selfClass="outerPort",
              params = SeqMap(
                "param" -> ValInit.Integer,
              ),
              ports = SeqMap(
                "inner" -> Port.Port(selfClass="innerPort",
                  params = SeqMap(
                    "param" -> ValInit.Integer,
                  ),
                ),
              )
            ),
          ),
          links = SeqMap(
            "inner" -> Link.Link(selfClass="innerLink",
              params = SeqMap(
                "innerParam" -> ValInit.Integer,
              ),
              ports = SeqMap(
                "innerPort" -> Port.Port(selfClass="innerPort",
                  params = SeqMap(
                    "param" -> ValInit.Integer,
                  ),
                ),
              ),
              constraints = SeqMap(
                "innerParamVal" -> ValueExpr.Assign(Ref("innerParam"), ValueExpr.Ref("innerPort", "param")),
              )
            ),
          ),
          constraints = SeqMap(
            "innerExport" -> Constraint.Exported(Ref("outerPort", "inner"), Ref("inner", "innerPort")),
            "outerParamVal" -> ValueExpr.Assign(Ref("outerParam"), ValueExpr.Ref("outerPort", "param")),
          )
        )
      ),
      constraints = SeqMap(
        "sourceConnect" -> Constraint.Connected(Ref("source", "port"), Ref("link", "outerPort")),

        "outerParamVal" -> Constraint.Assign(Ref("source", "outerParam"), ValueExpr.Literal(42)),
        "innerParamVal" -> Constraint.Assign(Ref("source", "innerParam"), ValueExpr.Literal(7)),
      )
    ))
    val (compiler, compiled) = testCompile(inputDesign, library)

    // Smaller comparisons to allow more targeted error messages
    val compiledBlock = compiled.contents.get
    val referenceBlock = referenceElaborated.contents.get

    compiledBlock.blocks.toSeqMap("source").`type`.hierarchy.get.ports.toSeqMap("port") should
        equal(referenceBlock.blocks.toSeqMap("source").`type`.hierarchy.get.ports.toSeqMap("port"))
    compiledBlock.blocks.toSeqMap("source") should equal(referenceBlock.blocks.toSeqMap("source"))

    compiledBlock.links.toSeqMap("link").`type`.link.get.ports.toSeqMap("outerPort") should
        equal(referenceBlock.links.toSeqMap("link").`type`.link.get.ports.toSeqMap("outerPort"))
    compiledBlock.links.toSeqMap("link").`type`.link.get.links.toSeqMap("inner") should
        equal(referenceBlock.links.toSeqMap("link").`type`.link.get.links.toSeqMap("inner"))
    compiledBlock.links.toSeqMap("link") should equal(referenceBlock.links.toSeqMap("link"))

    compiledBlock.constraints should equal(referenceBlock.constraints)

    // The catch-all equivalence comparison
    compiled should equal(referenceElaborated)
  }

  "Compiler on design with bundles" should "propagate and evaluate values" in {
    val inputDesign = Design(Block.Block("topDesign",
      blocks = SeqMap(
        "source" -> Block.Library("sourceBlock"),
      ),
      links = SeqMap(
        "link" -> Link.Library("outerLink")
      ),
      constraints = SeqMap(
        "sourceConnect" -> Constraint.Connected(Ref("source", "port"), Ref("link", "outerPort")),

        "outerParamVal" -> Constraint.Assign(Ref("source", "outerParam"), ValueExpr.Literal(42)),
        "innerParamVal" -> Constraint.Assign(Ref("source", "innerParam"), ValueExpr.Literal(7)),
      )
    ))
    val (compiler, compiled) = testCompile(inputDesign, library)

    // Check basic to-link value propagation
    compiler.getValue(IndirectDesignPath() + "link" + "outerParam") should equal(Some(IntValue(42)))
    compiler.getValue(IndirectDesignPath() + "link" + "inner" + "innerParam") should equal(Some(IntValue(7)))

    // Check IS_CONNECTED, including recursively
    compiler.getValue(IndirectDesignPath() + "link" + "outerPort" + IndirectStep.IsConnected) should
        equal(Some(BooleanValue(true)))
    compiler.getValue(IndirectDesignPath() + "link" + "inner" + "innerPort" + IndirectStep.IsConnected) should
        equal(Some(BooleanValue(true)))
    compiler.getValue(IndirectDesignPath() + "source" + "port" + IndirectStep.IsConnected) should
        equal(Some(BooleanValue(true)))
    compiler.getValue(IndirectDesignPath() + "source" + "port" + "inner" + IndirectStep.IsConnected) should
      equal(None)  // inner ports should not have connected status

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

  "Compiler on design with disconnected inner links" should "propagate is-connected" in {
    val inputDesign = Design(Block.Block("topDesign",
      blocks = SeqMap(
        "source" -> Block.Library("sourceBlock"),
      ),
      links = SeqMap(
        "link" -> Link.Library("outerLink")
      ),
    ))
    val (compiler, compiled) = testCompile(inputDesign, library)

    compiler.getValue(IndirectDesignPath() + "link" + "outerPort" + IndirectStep.IsConnected) should
        equal(Some(BooleanValue(false)))
    compiler.getValue(IndirectDesignPath() + "link" + "inner" + "innerPort" + IndirectStep.IsConnected) should
        equal(Some(BooleanValue(false)))
    compiler.getValue(IndirectDesignPath() + "source" + "port" + IndirectStep.IsConnected) should
        equal(Some(BooleanValue(false)))
    compiler.getValue(IndirectDesignPath() + "source" + "port" + "inner" + IndirectStep.IsConnected) should
      equal(None)  // inner ports should not have connected status
  }
}
