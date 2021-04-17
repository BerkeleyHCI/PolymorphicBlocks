import scalapb.compiler.Version.{grpcJavaVersion, scalapbVersion}

name := "edg-compiler"

version := "0.1-SNAPSHOT"

scalaVersion := "2.13.4"

libraryDependencies ++= Seq(
  "org.scalatest" %% "scalatest" % "3.2.0" % "test",

  "com.thesamet.scalapb" %% "scalapb-runtime" % scalapbVersion % "protobuf",
  "com.thesamet.scalapb" %% "scalapb-runtime-grpc" % scalapbVersion,
  "io.grpc" % "grpc-netty" % grpcJavaVersion,
)

PB.protoSources in Compile := Seq(
  baseDirectory.value / "../edgir",
  baseDirectory.value / "rpc",
)

PB.targets in Compile := Seq(
  scalapb.gen() -> (sourceManaged in Compile).value / "scalapb"
)

test in assembly := {}
assemblyMergeStrategy in assembly := {
  case PathList("META-INF", "io.netty.versions.properties") => MergeStrategy.first
  case PathList("META-INF", "MANIFEST.MF") => MergeStrategy.discard
  case PathList("META-INF", xs @ _*) => MergeStrategy.first
  case x => MergeStrategy.deduplicate
}
