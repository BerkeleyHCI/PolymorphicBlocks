RPC message definitions for the compiler-Python (HDL) interface.

See [edgir](../../edgir) for more details 

To compile the Python bindings, run in this folder:
```
protoc -I=. -I=../../edgir --python_out=../../edg_core/edgrpc --mypy_out=../../edg_core/edgrpc *.proto
sed -i -E "s/^import (schema|ref|elem|lit)_pb2 as (.*)/from edg_core.edgir import \1_pb2 as \2/" ../../edg_core/edgrpc/*.py
sed -i -E "s/^import (compiler|hdl)_pb2 as (.*)/from edg_core.edgrpc import \1_pb2 as \2/" ../../edg_core/edgrpc/*.py

sed -i -E "s/^from (schema|ref|elem|lit)_pb2 import/from edg_core.edgir.\1_pb2 import/"  ../../edg_core/edgrpc/*.pyi
sed -i -E "s/^from (compiler|hdl)_pb2 import/from edg_core.edgrpc.\1_pb2 import/"  ../../edg_core/edgrpc/*.pyi
```

Scala bindings are automatically compiled as part of the SBT project.
