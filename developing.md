# Developer Documentation

## Quick Reference Commands

### Static checking
This project has optional static typing annotations for Python which can be checked using [mypy](http://mypy-lang.org/).
If you have mypy installed (you may also need the type stubs for protobuf: `pip install mypy-protobuf`), you can typecheck code using:

```
mypy .
```

Or faster, with mypy in daemon mode:
```
dmypy run .
```

Or, using the [Mypy plugin for Intellij](https://plugins.jetbrains.com/plugin/13348-mypy-official-).

### Unit testing
```
python -m unittest discover
```

Or, to run tests for a specific package (eg, `edg_core` in this command):
```
python -m unittest discover -s edg.core -t .
```

Or, to run one specific test:
```
python -m unittest examples.test_blinky.BlinkyTestCase.test_design_complete
```


### Compiling the Compiler
A pre-compiled compiler JAR is included.
If you have not modified any of the .scala files, you do not need to recompile the compiler.

1. [Download and install sbt](https://www.scala-sbt.org/download.html), a build tool or Scala.
2. In the `compiler/` folder, run `sbt assembly` to compile the compiler JAR file.
   The system will automatically prefer the locally built JAR file over the pre-compiled JAR and indicate its use through the console.
3. Optionally, to commit a new pre-compiled JAR, move the newly compiled JAR from `compiler/target/scala-*/edg-compiler-assembly-*-SNAPSHOT.jar` to `edg_core/resources/edg-compiler-precompiled.jar`.
