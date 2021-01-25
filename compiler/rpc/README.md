gRPC for the compiler-Python (HDL) interface.

See [edgir](../../edgir) for more details 

Make sure the needed pip packages are installed:
```
pip install grpcio-tools
```

To compile the Python bindings, run in this folder:
```
python -m grpc_tools.protoc -I=. -I=../../edgir --python_out=../../edg_core/edgrpc --grpc_python_out=../../edg_core/edgrpc --mypy_out=../../edg_core/edgrpc *.proto
```

And to fix up package imports:
```
sed -i -E 's/^import (schema|ref|elem|lit)_pb2 as (.*)/from edg_core.edgir import \1_pb2 as \2/' ../../edg_core/edgrpc/*.py
sed -i -E 's/^import (compiler|hdl)_pb2 as (.*)/from edg_core.edgrpc import \1_pb2 as \2/' ../../edg_core/edgrpc/*.py
sed -i -E 's/^import grpc/import grpc  # type: ignore/' ../../edg_core/edgrpc/*.py
sed -i -E 's/^from (schema|ref|elem|lit)_pb2 import/from edg_core.edgir.\1_pb2 import/'  ../../edg_core/edgrpc/*.pyi
```

Note: mypy-protobuf [does not currently generate gRPC stubs](https://github.com/dropbox/mypy-protobuf/issues/46).

Scala bindings are automatically compiled as part of the SBT project.
