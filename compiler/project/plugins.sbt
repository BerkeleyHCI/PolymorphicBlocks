logLevel := Level.Warn

addSbtPlugin("com.thesamet" % "sbt-protoc" % "0.99.28")
libraryDependencies += "com.thesamet.scalapb" %% "compilerplugin" % "0.10.0"

addSbtPlugin("com.eed3si9n" % "sbt-assembly" % "0.15.0")
