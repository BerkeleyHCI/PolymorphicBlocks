package edg.wir

import edg.ref.ref


/**
  * Absolute path (from the design root) to some element, including indirect elements like CONNECTED_LINK and link-side
  * ports. Should be a path only, and independent of any particular design (so designs can be transformed while the
  * paths remain valid).
  *
  * Needs a connectivity table to resolve.
  */
sealed trait IndirectStep {
  def asLocalStep: ref.LocalStep
}

object IndirectStep {  // namespace
  case class Element(name: String) extends IndirectStep {
    override def toString: String = name
    override def asLocalStep: ref.LocalStep = {
      ref.LocalStep(step = ref.LocalStep.Step.Name(name))
    }
  }
  object IsConnected extends IndirectStep {
    override def toString: String = "IS_CONNECTED"
    override def asLocalStep: ref.LocalStep = {
      ref.LocalStep(step = ref.LocalStep.Step.ReservedParam(ref.Reserved.IS_CONNECTED))
    }
  }
  object Length extends IndirectStep {
    override def toString: String = "LENGTH"
    override def asLocalStep: ref.LocalStep = {
      ref.LocalStep(step = ref.LocalStep.Step.ReservedParam(ref.Reserved.LENGTH))
    }
  }
  object Name extends IndirectStep {
    override def toString: String = "NAME"
    override def asLocalStep: ref.LocalStep = {
      ref.LocalStep(step = ref.LocalStep.Step.ReservedParam(ref.Reserved.NAME))
    }
  }
  object ConnectedLink extends IndirectStep {  // block-side port -> link
    override def toString: String = "CONNECTED_LINK"
    override def asLocalStep: ref.LocalStep = {
      ref.LocalStep(step = ref.LocalStep.Step.ReservedParam(ref.Reserved.CONNECTED_LINK))
    }
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

  def ++(suffix: PathSuffix): IndirectDesignPath = {
    IndirectDesignPath(steps ++ suffix.steps)
  }

  def ++(suffix: ref.LocalPath): IndirectDesignPath = {
    IndirectDesignPath(steps ++ suffix.steps.map { step => step.step match {
      case ref.LocalStep.Step.Name(name) => IndirectStep.Element(name)
      case ref.LocalStep.Step.ReservedParam(ref.Reserved.IS_CONNECTED) => IndirectStep.IsConnected
      case ref.LocalStep.Step.ReservedParam(ref.Reserved.LENGTH) => IndirectStep.Length
      case ref.LocalStep.Step.ReservedParam(ref.Reserved.NAME) => IndirectStep.Name
      case ref.LocalStep.Step.ReservedParam(ref.Reserved.CONNECTED_LINK) => IndirectStep.ConnectedLink
      case ref.LocalStep.Step.ReservedParam(ref.Reserved.ALLOCATE) =>
        throw new IllegalArgumentException(s"Unexpected step ALLOCATE in resolving $suffix from $this")
      case ref.LocalStep.Step.ReservedParam(step @
          (ref.Reserved.UNDEFINED | ref.Reserved.Unrecognized(_))
      ) =>
        throw new NotImplementedError(s"Unknown step $step in resolving $suffix from $this")
      case ref.LocalStep.Step.Empty =>
        throw new NotImplementedError(s"Empty step resolving $suffix from $this")
    } } )
  }

  def toLocalPath: ref.LocalPath = {
    ref.LocalPath(steps=steps.map{
      case IndirectStep.Element(name) => ref.LocalStep(step=ref.LocalStep.Step.Name(name))
      case IndirectStep.IsConnected => ref.LocalStep(step=ref.LocalStep.Step.ReservedParam(
        ref.Reserved.IS_CONNECTED
      ))
      case IndirectStep.Length => ref.LocalStep(step=ref.LocalStep.Step.ReservedParam(
        ref.Reserved.LENGTH
      ))
      case IndirectStep.Name => ref.LocalStep(step=ref.LocalStep.Step.ReservedParam(
        ref.Reserved.NAME
      ))
      case IndirectStep.ConnectedLink => ref.LocalStep(step=ref.LocalStep.Step.ReservedParam(
        ref.Reserved.CONNECTED_LINK
      ))
    })
  }

  override def toString = steps.map(_.toString).mkString(".")
}

object IndirectDesignPath {
  def apply(): IndirectDesignPath = IndirectDesignPath(Seq())
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

  // Appends a PathSuffix. Errors out if the PathSuffix contains indirect elements.
  def ++(suffix: PathSuffix): DesignPath = {
    DesignPath(steps ++ suffix.steps.map(_.asInstanceOf[IndirectStep.Element].name))
  }

  def ++(suffix: ref.LocalPath): DesignPath = {
    DesignPath(steps ++ suffix.steps.map { step => step.step match {
      case ref.LocalStep.Step.Name(name) => name
      case step => throw new DesignPath.IndirectPathException(
        s"Found non-direct step $step when appending LocalPath $suffix")
    } } )
  }

  override def toString = steps.map(_.toString).mkString(".")

  def asIndirect: IndirectDesignPath = IndirectDesignPath(steps.map { IndirectStep.Element(_) })
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

  def asLocalPath(): ref.LocalPath = {
    ref.LocalPath(steps = steps.map(_.asLocalStep))
  }
}
