logLevel := Level.Warn

addSbtPlugin("com.thesamet" % "sbt-protoc" % "1.0.6")
libraryDependencies += "com.thesamet.scalapb" %% "compilerplugin" % "0.11.11"

addSbtPlugin("com.eed3si9n" % "sbt-assembly" % "1.2.0")
