## Getting Started
See [the getting started document](getting-started.md).
Also, see [the reference document](reference.md) for a list and short description of ports, links, and parts.

## Developing and running

### Python packages
```python
pip install protobuf py4j
```
(or, on Ubuntu, to select a different version of Python, use eg `python3.8 -m pip` instead of `pip` directly)

### Static checking
```
mypy --check-untyped-defs -p edg_core -p electronics_model -p electronics_abstract_parts -p electronics_lib -p edg -p examples -p compiler_gui
```

Or faster, with mypy in daemon mode:
```
dmypy run -- --follow-imports=error --check-untyped-defs -p edg_core -p electronics_model -p electronics_abstract_parts -p electronics_lib -p edg -p examples -p compiler_gui
```

Note: since mypy currently doesn't infer return types (see mypy issue 4409), some defs might be incomplete, so the type check is leaky and we can't currently use `--disallow-incomplete-defs` or `--disallow-untyped-defs`.
If that doesn't get resolved, we might go through and manually annotate all return types. 

### Unit testing
```
python -m unittest discover
```

PROTIP: run both by combining the commands with `&&`

### Building Java dependencies
#### IntelliJ Project Setup
- Open `frontend\compiler_gui\resources\java\py4j_elk` in IntelliJ
- From main menu > File > Project Structure:
  - In Project Settings > Libraries, add these as Maven libraries:
    - net.sf.py4j:py4j:0.10.8.1
    - org.eclipse.elk:org.eclipse.elk.alg.graphviz.dot:0.5.0
    - org.eclipse.elk:org.eclipse.elk.alg.layered:0.5.0
    - org.eclipse.elk:org.eclipse.elk.graph.json:0.5.0
  - In Project Settings > Modules, ensure py4j_elk is added as a Module, and the `src/` folder is marked as source
  - In Project Settings > Modules, add a JAR build, "from module with dependencies".
    - For "Main class", choose "org.edg.Main"
    - For "JAR files from libraries", select "copy to the output directory and link via manifest", to avoid signature mismatches


## Frontend Model and Architecture

### Core
#### Block Diagram
- BaseBlock: abstract base class for all block-like constructs, which contain ports (IOs), parameters, and constraints between them.
  In general, subclasses may override superclass ports with a subtype port. (TODO: is this a good idea?)
  Provides infrastructure to record the names of ports and parameters (by overriding __setattr__) with the syntax self.[name] = self.Port([port])
- Link: abstract base class for all links, which are inferred to fit a connection between ports.
- Block: abstract base class for blocks.
- ConcreteBlock: abstract base class for blocks that can be part of a final design.
- PortBridge: block-like construct that defines how an external port of a hierarchy block connects to an internal link, such as by adapting the type and propagating constraints.
- HierarchyBlock: abstract base class for blocks that contain an internal block diagram (with internal blocks and connections), which may also link to external ports.
- GeneratorPart (TODO: needs renaming and implementation): a hierarchy block that contains a function to generate the internal block diagram once the external block diagram is solved.
  Allows arbitrary Python to control the internal generation, since it is not part of the SMT loop.
- BasePort: abstract mixin for all port-like constructs, which knows its parent (either a block or a container port).
- BaseContainerPort: abstract base class for all ports that contains other ports.
- Port: abstract base class for leaf-level ports, which contains parameters.
  Defines the link_type it may connect to (TODO: should it support multiple link types, of a common superclass?), and provides access to the connected link which can be used to avoid propagating duplicate parameters.
  Also defines the bridge_type, if one exists where this port is the external port on a hierarchy block.
- Bundle: a Port and a BaseContainerPort, that defines internal fields (other ports).
- Vector: an unknown-sized vector (array) of ports, which supports a map-extract operation to return an Array of some inner parameter as well as reduction operators that wrap the map-extract and an Array reduction.

#### Parameters & Expressions
- ConstraintExpr: abstract base class for constraint expressions.
- BoolExpr: ConstraintExpr that is a Bool.
- NumLikeExpr: ConstraintExpr abstract base class for numeric expressions, provides arithmetic operations compatible with SMT solvers (add, subtract, comparison).
- FloatExpr: ConstraintExpr that is a real number.
- RangeExpr: ConstraintExpr that is a real-valued interval type, with a min and max. (TODO: may support null-intervals)
- Array: an unknown-sized array (container) of ConstraintExpr, which supports reduction operators (eg, sum, min, max, intersection).

#### Other
- Driver: provides auto-discovery of block diagram components in a Python library.
  (TODO: provides conversion to design, including recursive instantiation of library elements)

### Electronics Model
- ElectricaSink/Source/Link/Bridge: represents a single copper net, and models runtime voltage and currents as well as their limits
  Can be used as a base class for other single-copper-net ports.
- DigitalSink/Source/Link/Bridge: subclass of Electrical*, additionally models logic IO thresholds
- BaseCircuitBlock: a Block with associated footprints (where pins can be mapped to Electrical* ports) and nets (connections between Electrical* ports)
  This can be used for component-level blocks, links (with nets defining copper connectivity between ports), and hierarchy blocks.
  Not all blocks need a footprint: abstract blocks can rely on a refinement for a footprint, and hierarchy blocks can rely on internal blocks for footprints.

### Standard Parts
A standard library of actual parts (eg, could buy off DigiKey), their models, and supporting reference implementation components / circuits.
