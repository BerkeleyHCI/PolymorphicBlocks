package edg.compiler

object CliMain {
  def main(args: Array[String]): Unit = {
    val moduleName = args[1]
    val blockName = args[2]
    println(s"Compile with modules $moduleName, block $blockName")

  }
}
