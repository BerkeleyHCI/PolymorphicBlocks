# Setup

## HDL Core Setup
_These are the instructions to set up the HDL core, both for command-line compilation as well as using the IDE (requires additional setup in the next section)._
_Runs natively on Windows, Linux, and Mac._

1. Make sure you are using Python 3.9 (or later).
2. If you do not have a Java JDK installed, download and install one.
   An open-source one is [Eclipse Temurin](https://adoptium.net/temurin/releases/?version=17).
   Java 11 (or later) is required.
   <details> <summary>Determining Java version</summary>

   _This is probably not necessary unless you suspect you're running an outdated Java version, most will probably have Java 11+ installed._

   On the command line, run `java --version`.
   If Java is installed, you'll get something like:

     ```
     openjdk 17.0.4.1 2022-08-12
     OpenJDK Runtime Environment Temurin-17.0.4.1+1 (build 17.0.4.1+1)
     OpenJDK 64-Bit Server VM Temurin-17.0.4.1+1 (build 17.0.4.1+1, mixed mode, sharing)
     ```

   The above is an example of a JDK at Java 17.
   Version reporting formats are not standardized, for example Oracle's Java 8 may report as `Oracle Corporation Java 1.8.0_351`.
   </details>
   <!--Reference: JDK compatibility from https://docs.scala-lang.org/overviews/jdk-compatibility/overview.html-->
3. Install the Python package using the package manager:  
   `pip install edg`


## IDE Setup
_Using the IDE is recommended since it provides a design browser and block diagram visualizer, but it's optional._
_Currently, the IDE must be built from source (it's pretty straightforward), but in the future we may make pre-compiled versions available._

1. Download [sbt](https://www.scala-sbt.org/download.html), the Scala build tool.
2. Download or clone the IDE plugin sources from https://github.com/BerkeleyHCI/edg-ide.
    - If using command line git: make sure to initialize submodules: `git submodule update --init --recursive`.
    - If using GitHub Desktop: it should automatically clone submodules for you.
3. In the `edg-ide` directory, run `sbt runIDE`.
   sbt will automatically fetch dependencies, compile the plugin, and start the IDE with the plugin enabled.
    - The first run may take a while.
   <details> <summary>Resolving common errors</summary>

    - If you get an error along the lines of  
      `sbt.librarymanagement.ResolveException: Error downloading edgcompiler:edgcompiler_2.13:0.1.0-SNAPSHOT`  
      or `not found: [...]/edgcompiler/edgcompiler_2.13/0.1.0-SNAPSHOT/edgcompiler_2.13-0.1.0-SNAPSHOT.pom`,  
      this is because the PolymorphicBlocks submodule hasn't been cloned.
      See the section above for instructions.
      The IDE plugin includes the HDL compiler as part of its build and requires the PolymorphicBlocks codebase.
    - If you get an error along the lines of `[error] ...: value strip is not a member of String`,
      this is because your Java version is pre-11.
      See the section above for instructions to install a more recent JDK.
   </details>
4. Within the IDE, create a new Python project.
   - The location can be anywhere.
   - The default environment type of Virtualenv is fine.
   - **Make sure to check "inherit global site-packages"**, so that the pip-installed package will be visible.
   > A prior version of this setup guide had the IDE open the PolymorphicBlocks repository and develop directly on it.
   > Unless you are developing the core HDL or core libraries, this pip package + new project setup flow is recommended.
   > However, the IDE does also support working with the PolymorphicBlocks project.
