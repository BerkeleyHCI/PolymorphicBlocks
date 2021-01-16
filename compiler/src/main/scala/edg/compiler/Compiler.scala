package edg.compiler

import edg.schema.schema


/** Compiler for a particular design, with an associated library to elaborate references from.
  * TODO also needs a Python interface for generators, somewhere.
  *
  * During the compilation process, internal data structures are mutated.
  */
class Compiler(inputDesignPb: schema.Design, library: edg.wir.Library) {
  /** Performs full compilation and returns the resulting design. Might take a while.
    */
  def compile(): schema.Design = {

  }
}
