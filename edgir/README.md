IR definition in protocol buffer format.

To compile, run in this directory:

```
protoc -I=proto --python_out=../edg_core/edgir --mypy_out=../edg_core/edgir *.proto
```

Follow the [instructions on the mypy-protobuf repo](https://github.com/dropbox/mypy-protobuf) for setting up protobuf with mypy to generate type stubs.

If installing with `pip` under Ubuntu, you may have to invoke `pip` with `sudo` so the executables are found in your PATH. 

There appears to be a bug in version 1.10 that creates type signatures incompatible with supertypes. 1.9 appears to work, and if you're using pip, install this specific version with:

```
pip install --force-reinstall 'mypy-protobuf==1.9'
```

Note that both the Python and mypy generators do not support modules (they expect the genreated files to be dumped in the project top directory), so post-processing is reequired. **In the same directory**, run this find-and-replace script:

```
sed -i -E 's/^import.*_pb2/from . \0/' frontend/edg_core/edgir/*.py
sed -i -E 's/^from (.*)_pb2 import/from .\1_pb2 import/'  frontend/edg_core/edgir/*.pyi
```

See https://github.com/protocolbuffers/protobuf/issues/1491 for more details.
