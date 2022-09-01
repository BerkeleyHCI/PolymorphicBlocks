package edg.util

object MapUtils {
  /**
    * Merges the argument maps, erroring out if there are duplicate names
    */
  def mergeMapSafe[K, V](maps: Map[K, V]*): Map[K, V] = {
    maps.flatMap(_.toSeq) // to a list of pairs in the maps
        .groupBy(_._1) // sort by name
        .map {
          case (name, Seq((_, value))) => name -> value
          case (name, values) => throw new IllegalArgumentException(
            s"maps contains ${values.length} conflicting members with name $name: $values")
        }
  }
}
