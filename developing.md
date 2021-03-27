# Developer Documentation

## Quick Reference Commands

### Static checking
This project has optional static typing annotations for Python which can be checked using [mypy](http://mypy-lang.org/).
If you have mypy installed, you can typecheck code using:

```
mypy --check-untyped-defs -p edg_core -p electronics_model -p electronics_abstract_parts -p electronics_lib -p edg -p examples
```

Or faster, with mypy in daemon mode:
```
dmypy run -- --follow-imports=error --check-untyped-defs -p edg_core -p electronics_model -p electronics_abstract_parts -p electronics_lib -p edg -p examples
```

Note: since mypy currently doesn't infer return types (see mypy issue 4409), some defs might be incomplete, so the type check is leaky and we can't currently use `--disallow-incomplete-defs` or `--disallow-untyped-defs`.
If that doesn't get resolved, we might go through and manually annotate all return types. 

### Unit testing
```
python -m unittest discover
```

Or, to run tests for a specific package (eg, `edg_core` in this command):
```
python -m unittest discover -s edg_core -t .
```

PROTIP: run both by combining the commands with `&&`


## Setup

## Code Architecture
_Some documentation may be out of date._

### Core
`edg_core` is the core package, and sets up base classes for the hierarchy block and links model.
These are domain-neutral (not specific to circuit boards, or even electronics).
The Python implementation of the compiler (backend) also lives here.

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

#### Intermediate Representation
The fundamental hierarchy blocks and links model is encoded as an [intermediate representation](https://en.wikipedia.org/wiki/Intermediate_representation) in [Protocol Buffer](https://developers.google.com/protocol-buffers), 
The Protocol Buffers schema is in the [edgir](edgir) folder, and generated Protocol Buffers code (including Python type annotations) is committed to this repository.
The intent behind this is to allow cross-language interoperability (eg, solver implemented in another, more efficient, language) and to define a compiled object format.

You can ignore this section, unless you are changing the Protocol Buffer structure.

### Electronics Model
`electronics_model` uses the `edg_core` classes to define an electronics model, by adding base classes to support circuit design (pin ports, copper-net links, and footprint blocks) and defining common electronics types. 

- VoltageSink/Source/Link/Bridge: represents a single copper net, and models runtime voltage and currents as well as their limits
  Can be used as a base class for other single-copper-net ports.
- DigitalSink/Source/Link/Bridge: subclass of Voltage*, additionally models logic IO thresholds
- BaseCircuitBlock: a Block with associated footprints (where pins can be mapped to Voltage* ports) and nets (connections between Voltage* ports)
  This can be used for component-level blocks, links (with nets defining copper connectivity between ports), and hierarchy blocks.
  Not all blocks need a footprint: abstract blocks can rely on a refinement for a footprint, and hierarchy blocks can rely on internal blocks for footprints.

`electronics_abstract_parts` further defines abstract block types for the type hierarchy of components.

### Standard Parts
`electronics_lib` contains a standard library of actual parts (eg, could buy off DigiKey), their models, and supporting reference implementation components / circuits.

### Examples
`examples` contains several example top-level boards, written as test cases and run with the unit test suite.
