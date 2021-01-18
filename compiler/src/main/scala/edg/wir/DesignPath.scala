package edg.wir

import edg.ref.ref


/**
  * Absolute path (from the design root) to some element, including indirect elements like CONNECTED_LINK and link-side
  * ports. Should be a path only, and independent of any particular design (so designs can be transformed while the
  * paths remain valid).
  *
  * Needs a connectivity table to resolve.
  */
sealed trait IndirectStep
object IndirectStep {  // namespace
  case class ConnectedLink() extends IndirectStep {  // block-side port -> link
    override def toString: String = "CONNECTED_LINK"
  }
  case class Element(name: String) extends IndirectStep {
    override def toString = name
  }
}
case class IndirectDesignPath(steps: Seq[IndirectStep]) {
  def +(suffix: String): IndirectDesignPath = {
    IndirectDesignPath(steps :+ IndirectStep.Element(suffix))
  }
  def +(suffix: IndirectStep): IndirectDesignPath = {  // TODO: kinda abstraction breaking?
    IndirectDesignPath(steps :+ suffix)
  }

  def ++(suffix: Seq[String]): IndirectDesignPath = {
    IndirectDesignPath(steps ++ suffix.map { IndirectStep.Element(_) })
  }

  def ++(suffix: ref.LocalPath): IndirectDesignPath = {
    IndirectDesignPath(steps ++ suffix.steps.map { step => step.step match {
      case ref.LocalStep.Step.Name(name) => IndirectStep.Element(name)
      case ref.LocalStep.Step.ReservedParam(ref.Reserved.CONNECTED_LINK) => IndirectStep.ConnectedLink()
      case step => throw new NotImplementedError(s"Unknown step $step in appending $suffix from $this")
    } } )
  }

  override def toString = steps.map(_.toString).mkString(".")
}

object IndirectDesignPath {
  def root: IndirectDesignPath = IndirectDesignPath(Seq())
  def fromDesignPath(designPath: DesignPath): IndirectDesignPath = {
    IndirectDesignPath(designPath.steps.map { IndirectStep.Element(_) })
  }
}


/**
  * Absolute path (from the design root) to some element.
  * TODO: should exclude link ports, since the block side port is treated as authoritative.
  */
case class DesignPath(steps: Seq[String]) {
  // Separates into (prefix, last) where last is the last element, and prefix is a DesignPath of all but the last
  // element.
  def split: (DesignPath, String) = {
    require(steps.nonEmpty)
    (DesignPath(steps.slice(0, steps.length - 1)), steps.last)
  }

  def +(elem: String): DesignPath = {
    DesignPath(steps :+ elem)
  }

  def ++(suffix: Seq[String]): DesignPath = {
    DesignPath(steps ++ suffix)
  }

  def ++(suffix: ref.LocalPath): DesignPath = {
    DesignPath(steps ++ suffix.steps.map { step => step.step match {
      case ref.LocalStep.Step.Name(name) => name
      case step => throw new DesignPath.IndirectPathException(
        s"Found non-direct step $step when appending LocalPath $suffix")
    } } )
  }

  override def toString = steps.map(_.toString).mkString(".")
}

object DesignPath {
  class IndirectPathException(message: String) extends Exception(message)

  /**
    * Converts an indirect path to a (direct) design path, throwing an exception if there are indirect references
    */
  def fromIndirectOption(indirect: IndirectDesignPath): Option[DesignPath] = {
    val stepsOpt = indirect.steps.map {
      case IndirectStep.Element(name) => Some(name)
      case step => None
    }
    if (stepsOpt.contains(None)) {
      None
    } else {
      Some(DesignPath(stepsOpt.map(_.get)))
    }
  }

  def fromIndirect(indirect: IndirectDesignPath): DesignPath = {
    DesignPath(indirect.steps.map {
      case IndirectStep.Element(name) => name
      case step => throw new IndirectPathException(s"Found non-direct $step when converting indirect $indirect")
    })
  }

  def root: DesignPath = DesignPath(Seq())
}
