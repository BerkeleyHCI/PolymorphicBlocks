name := "edg-compiler"

version := "0.1-SNAPSHOT"

scalaVersion := "2.13.4"

libraryDependencies ++= Seq(
  "org.scalatest" %% "scalatest" % "3.2.0" % "test",

  "com.thesamet.scalapb" %% "scalapb-runtime" % scalapb.compiler.Version.scalapbVersion % "protobuf",
)

PB.protoSources in Compile := Seq(
  baseDirectory.value / "../edgir",
  baseDirectory.value / "rpc",
)

PB.targets in Compile := Seq(
  scalapb.gen() -> (sourceManaged in Compile).value / "scalapb"
)
