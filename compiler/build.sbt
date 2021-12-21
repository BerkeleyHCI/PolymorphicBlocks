import scalapb.compiler.Version.{scalapbVersion}

name := "edg-compiler"

version := "0.1-SNAPSHOT"

scalaVersion := "2.13.4"

scalacOptions += "-deprecation"

libraryDependencies ++= Seq(
  "org.scalatest" %% "scalatest" % "3.2.0" % "test",

  "com.thesamet.scalapb" %% "scalapb-runtime" % scalapbVersion % "protobuf",
)

Compile / PB.protoSources := Seq(
  baseDirectory.value / "../proto",
  baseDirectory.value / "rpc",
)

Compile / PB.targets := Seq(
  scalapb.gen() -> (Compile / sourceManaged).value / "scalapb"
)
