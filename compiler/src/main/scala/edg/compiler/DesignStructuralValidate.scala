package edg.compiler

import edgir.elem.elem
import edgir.ref.ref
import edg.wir.DesignPath

import scala.collection.SeqMap


/** Performs structural design validation on a protobuf design, checking for:
  * - unelaborated generators
  * - unelaborated library elements
  */
class DesignStructuralValidate extends DesignMap[Seq[CompilerError], Seq[CompilerError], Seq[CompilerError]] {
  override def mapPort(path: DesignPath, port: elem.Port): Seq[CompilerError] = {
    Seq()
  }
  override def mapPortArray(path: DesignPath, port: elem.PortArray,
                   ports: SeqMap[String, Seq[CompilerError]]): Seq[CompilerError] = {
    val undefinedError = if (!port.contains.isPorts) {
      Seq(CompilerError.UndefinedPortArray(path, port.getSelfClass))
    } else {
      Seq()
    }
    undefinedError ++ ports.values.flatten.toSeq
  }
  override def mapBundle(path: DesignPath, port: elem.Bundle,
                ports: SeqMap[String, Seq[CompilerError]]): Seq[CompilerError] = {
    ports.values.flatten.toSeq
  }
  override def mapPortLibrary(path: DesignPath, port: ref.LibraryPath): Seq[CompilerError] = {
    Seq(CompilerError.LibraryElement(path, port))
  }

  override def mapBlock(path: DesignPath, block: elem.HierarchyBlock,
               ports: SeqMap[String, Seq[CompilerError]], blocks: SeqMap[String, Seq[CompilerError]],
               links: SeqMap[String, Seq[CompilerError]]): Seq[CompilerError] = {
    val abstractError = if (block.isAbstract) {
      Seq(CompilerError.AbstractBlock(path, block.getSelfClass))
    } else {
      Seq()
    }
    val errors = ports.values.flatten ++ blocks.values.flatten ++ links.values.flatten
    errors.toSeq ++ abstractError
  }
  override def mapBlockLibrary(path: DesignPath, block: ref.LibraryPath): Seq[CompilerError] = {
    Seq(CompilerError.LibraryElement(path, block))
  }

  override def mapLink(path: DesignPath, block: elem.Link,
              ports: SeqMap[String, Seq[CompilerError]], links: SeqMap[String, Seq[CompilerError]]): Seq[CompilerError] = {
    (ports.values.flatten ++ links.values.flatten).toSeq
  }
  override def mapLinkLibrary(path: DesignPath, link: ref.LibraryPath): Seq[CompilerError] = {
    Seq(CompilerError.LibraryElement(path, link))
  }
}
