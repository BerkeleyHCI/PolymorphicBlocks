# Setup
_Setting up and using the IDE is recommended, but HDL-only setup is also documented below._
_Runs natively on Windows, Linux, and Mac._

1. Download [sbt](https://www.scala-sbt.org/download.html), the Scala build tool.
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
3. Download or clone the IDE plugin sources from https://github.com/BerkeleyHCI/edg-ide.
    - If using command line git: make sure to initialize submodules: `git submodule update --init --recursive`.
    - If using GitHub Desktop: it should automatically clone submodules for you.
4. In the `edg-ide` directory, run `sbt runIDE`.
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
5. In the IDE, **open the `PolymorphicBlocks` folder as a project**.
    - You do not need to clone `PolymorphicBlocks` separately, you can use the submodule in `edg-ide`.
6. Once the project loads, open `blinky_skeleton.py`.
7. Set up the Python interpreter once the prompt shows up, "Configure Python interpreter".
    - Recommended: set up a Virtualenv environment based on a Python 3.7 (or later) interpreter.
    - Install Python requirements (packages) if prompted, this banner should show up in the `blinky_skeleton.py` editor:  
      ![Dependencies banner](docs/ide/ide_deps.png)
    - When requirements finish installing, this popup will show up on the bottom right:  
      ![Install complete popup](docs/ide/ide_deps_complete.png)
   <details> <summary>Using other interpreters</summary>

    - If using Pipenv (may need to be installed separately), IntelliJ should also prompt you to install dependencies similarly to the Virtualenv case above.
    - If using System Interpreter or Conda: you will need to install dependencies manually, `pip install -r requirements.txt`.
        - On Ubuntu, you may need to select a particular version of Python for pip, using `python3.8 -m pip` instead of `pip` directly.
   </details>
9. Open the Block Visualizer tab on the right.
   It will be empty right now.


<details> <summary>Alternatively, HDL-only setup...</summary>

_This isn't necessary if you're using the IDE._
_Runs natively on Windows, Linux, and Mac._

1. Make sure you are using Python 3.7 (or later).
2. Make sure you have Java 11 or later.
3. Install the needed dependencies.
   If using pip: `pip install -r requirements.txt`
    - If on Linux and you get an error along the lines of `python: command not found`, you may need to `apt install python-is-python3`.
</details>
