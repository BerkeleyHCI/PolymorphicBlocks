package edg.wir

import edgir.ref.ref

/** Absolute path (from the design root) to some element, including indirect elements like CONNECTED_LINK and link-side
  * ports. Should be a path only, and independent of any particular design (so designs can be transformed while the
  * paths remain valid).
  *
  * Needs a connectivity table to resolve.
  */
sealed trait IndirectStep {
  def asLocalStep: ref.LocalStep
}

object IndirectStep { // namespace
  case class Element(name: String) extends IndirectStep {
    override def toString: String = name
    override def asLocalStep: ref.LocalStep = {
      ref.LocalStep(step = ref.LocalStep.Step.Name(name))
    }
  }
  case object IsConnected extends IndirectStep {
    override def toString: String = "IS_CONNECTED"
    override def asLocalStep: ref.LocalStep = {
      ref.LocalStep(step = ref.LocalStep.Step.ReservedParam(ref.Reserved.IS_CONNECTED))
    }
  }
  case object Length extends IndirectStep {
    override def toString: String = "LENGTH"
    override def asLocalStep: ref.LocalStep = {
      ref.LocalStep(step = ref.LocalStep.Step.ReservedParam(ref.Reserved.LENGTH))
    }
  }
  case object Elements extends IndirectStep {
    override def toString: String = "ELEMENTS"
    override def asLocalStep: ref.LocalStep = {
      ref.LocalStep(step = ref.LocalStep.Step.ReservedParam(ref.Reserved.ELEMENTS))
    }
  }
  case class Allocate(suggestedName: Option[String] = None) extends IndirectStep {
    override def toString: String = s"ALLOCATE($suggestedName)"
    override def asLocalStep: ref.LocalStep = {
      ref.LocalStep(step = ref.LocalStep.Step.Allocate(suggestedName.getOrElse("")))
    }
  }
  case object Allocated extends IndirectStep {
    override def toString: String = "ALLOCATED"
    override def asLocalStep: ref.LocalStep = {
      ref.LocalStep(step = ref.LocalStep.Step.ReservedParam(ref.Reserved.ALLOCATED))
    }
  }
  case object Name extends IndirectStep {
    override def toString: String = "NAME"
    override def asLocalStep: ref.LocalStep = {
      ref.LocalStep(step = ref.LocalStep.Step.ReservedParam(ref.Reserved.NAME))
    }
  }
  case object ConnectedLink extends IndirectStep { // block-side port -> link
    override def toString: String = "CONNECTED_LINK"
    override def asLocalStep: ref.LocalStep = {
      ref.LocalStep(step = ref.LocalStep.Step.ReservedParam(ref.Reserved.CONNECTED_LINK))
    }
  }

  def apply(pb: ref.LocalStep): IndirectStep = pb.step match {
    case ref.LocalStep.Step.Name(name) => IndirectStep.Element(name)
    case ref.LocalStep.Step.Allocate("") => Allocate(None)
    case ref.LocalStep.Step.Allocate(suggestedName) => Allocate(Some(suggestedName))
    case ref.LocalStep.Step.ReservedParam(ref.Reserved.IS_CONNECTED) => IndirectStep.IsConnected
    case ref.LocalStep.Step.ReservedParam(ref.Reserved.LENGTH) => IndirectStep.Length
    case ref.LocalStep.Step.ReservedParam(ref.Reserved.ELEMENTS) => IndirectStep.Elements
    case ref.LocalStep.Step.ReservedParam(ref.Reserved.ALLOCATED) => IndirectStep.Allocated
    case ref.LocalStep.Step.ReservedParam(ref.Reserved.NAME) => IndirectStep.Name
    case ref.LocalStep.Step.ReservedParam(ref.Reserved.CONNECTED_LINK) => IndirectStep.ConnectedLink
    case ref.LocalStep.Step.ReservedParam(step @ (ref.Reserved.UNDEFINED | ref.Reserved.Unrecognized(_))) =>
      throw new NotImplementedError(s"Unknown step $step to resolve into IndirectStep")
    case ref.LocalStep.Step.Empty =>
      throw new NotImplementedError(s"Can't resolve Empty into IndirectStep")
  }
}
case class IndirectDesignPath(steps: Seq[IndirectStep]) {
  def +(suffix: String): IndirectDesignPath = {
    IndirectDesignPath(steps :+ IndirectStep.Element(suffix))
  }
  def +(suffix: IndirectStep): IndirectDesignPath = { // TODO: kinda abstraction breaking?
    IndirectDesignPath(steps :+ suffix)
  }

  def ++(suffix: Seq[String]): IndirectDesignPath = {
    IndirectDesignPath(steps ++ suffix.map { IndirectStep.Element(_) })
  }

  def ++(suffix: PathSuffix): IndirectDesignPath = {
    IndirectDesignPath(steps ++ suffix.steps)
  }

  def ++(suffix: ref.LocalPath): IndirectDesignPath = {
    IndirectDesignPath(steps ++ suffix.steps.map(IndirectStep(_)))
  }

  def toLocalPath: ref.LocalPath = {
    ref.LocalPath(steps = steps.map(_.asLocalStep))
  }

  // if this starts with CONNECTED_LINK, returns the split as the CONNECTED_LINK portion (including
  // the CONNECTED_LINK) and the postfix as a LocalPath
  def splitConnectedLink: Option[(DesignPath, ref.LocalPath)] = {
    steps.indexOf(IndirectStep.ConnectedLink) match {
      case index if index >= 0 =>
        val (connectedLinkSteps, postfixSteps) = steps.splitAt(index + 1)
        val portSteps = connectedLinkSteps.init.map { _.asInstanceOf[IndirectStep.Element].name }
        Some((DesignPath(portSteps), ref.LocalPath(steps = postfixSteps.map(_.asLocalStep))))
      case _ => None
    }
  }

  def init: IndirectDesignPath = IndirectDesignPath(steps.init)

  override def toString = steps.map(_.toString).mkString(".")
}

object IndirectDesignPath {
  def apply(): IndirectDesignPath = IndirectDesignPath(Seq())
}

/** Absolute path (from the design root) to some element.
  */
case class DesignPath(steps: Seq[String]) {
  // Separates into (prefix, last) where last is the last element, and prefix is a DesignPath of all but the last
  // element.
  def split: (DesignPath, String) = {
    require(steps.nonEmpty, s"splitting empty DesignPath")
    (DesignPath(steps.slice(0, steps.length - 1)), steps.last)
  }

  def +(elem: String): DesignPath = {
    DesignPath(steps :+ elem)
  }

  def ++(suffix: Seq[String]): DesignPath = {
    DesignPath(steps ++ suffix)
  }

  def ++(suffix: ref.LocalPath): DesignPath = {
    DesignPath(steps ++ suffix.steps.map { step =>
      step.step match {
        case ref.LocalStep.Step.Name(name) => name
        case step => throw new DesignPath.IndirectPathException(
            s"Found non-direct step $step when appending LocalPath $suffix"
          )
      }
    })
  }

  override def toString = steps match {
    case Seq() => "(root)"
    case steps => steps.map(_.toString).mkString(".")
  }

  def lastString: String = steps match {
    case Seq() => "(root)"
    case steps => steps.last
  }

  def startsWith(other: DesignPath): Boolean = steps.startsWith(other.steps)
  def postfixFromOption(prefix: DesignPath): Option[ref.LocalPath] = {
    if (!startsWith(prefix)) {
      return None
    }
    val postfixSteps = steps.drop(prefix.steps.size)
    Some(ref.LocalPath(steps = postfixSteps.map { step =>
      ref.LocalStep().update(_.name := step)
    }))
  }

  def asIndirect: IndirectDesignPath = IndirectDesignPath(steps.map { IndirectStep.Element(_) })
}

object DesignPath {
  class IndirectPathException(message: String) extends Exception(message)

  /** Converts an indirect path to a (direct) design path, throwing an exception if there are indirect references
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

  def apply(): DesignPath = DesignPath(Seq())

  def unapply(path: DesignPath): Option[Seq[String]] = Some(path.steps)
}

case class PathSuffix(steps: Seq[IndirectStep] = Seq()) {
  def +(elem: String): PathSuffix = {
    PathSuffix(steps :+ IndirectStep.Element(elem))
  }
  def +(elem: IndirectStep): PathSuffix = {
    PathSuffix(steps :+ elem)
  }
  def ++(suffix: ref.LocalPath): PathSuffix = {
    PathSuffix(steps ++ suffix.steps.map(IndirectStep(_)))
  }

  def asLocalPath(): ref.LocalPath = {
    ref.LocalPath(steps = steps.map(_.asLocalStep))
  }
}
