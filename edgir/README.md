IR definition in protocol buffer format.

To compile, run in this directory:

```
protoc -I=. --python_out=../edg_core/edgir --mypy_out=../edg_core/edgir *.proto
```

Follow the [instructions on the mypy-protobuf repo](https://github.com/dropbox/mypy-protobuf) for setting up protobuf with mypy to generate type stubs.

If installing with `pip` under Ubuntu, you may have to invoke `pip` with `sudo` so the executables are found in your PATH. 

Note that both the Python and mypy generators do not support modules (they expect the generated files to be dumped in the project top directory), so post-processing is reequired. **In the same directory**, run this find-and-replace script:

```
sed -i -E 's/^import.*__pb2/from . \0/' ../edg_core/edgir/*.py
sed -i -E 's/^from (.*)_pb2 import/from .\1_pb2 import/'  ../edg_core/edgir/*.pyi
```

See https://github.com/protocolbuffers/protobuf/issues/1491 for more details.

The current committed stubs are generated with mypy-protobuf 1.23.
pip can be forced to install particular versions of packages, such as with: 
```
pip install --force-reinstall 'mypy-protobuf==1.23'
```
