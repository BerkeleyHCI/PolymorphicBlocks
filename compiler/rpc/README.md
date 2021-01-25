gRPC for the compiler-Python (HDL) interface.

See [edgir](../../edgir) for more details 

To compile the Python bindings, run in this folder:
```
protoc -I=. -I=../../edgir --python_out=../../edg_core/edgrpc --mypy_out=../../edg_core/edgrpc *.proto
```

And to fix up package imports:
```
sed -i -E 's/^import.*_pb2/from . \0/' ../edg_core/edgrpc/*.py
sed -i -E 's/^from (.*)_pb2 import/from .\1_pb2 import/'  ../edg_core/edgir/*.pyi
```

Note: mypy-protobuf [does not currently generate gRPC stubs](https://github.com/dropbox/mypy-protobuf/issues/46).

Scala bindings are automatically compiled as part of the SBT project.
