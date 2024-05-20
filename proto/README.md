IR definition in protocol buffer format.

You will need [mypy-protobuf](https://github.com/dropbox/mypy-protobuf) (to generate type stubs) and protoletariat (post-processing to use relative imports)
```commandline
pip install mypy-protobuf
pip install protoletariat
```

To compile, run in this directory:

```
protoc --proto_path=. --python_out=.. --mypy_out=../edg edgir/*.proto edgrpc/*.proto
protol --in-place --python-out ../edg protoc --proto-path=. edgir/*.proto edgrpc/*.proto
```

Follow the [instructions on the mypy-protobuf repo](https://github.com/dropbox/mypy-protobuf) for setting up protobuf with mypy to generate type stubs.

If installing with `pip` under Ubuntu, you may have to invoke `pip` with `sudo` so the executables are found in your PATH. 

See https://github.com/protocolbuffers/protobuf/issues/1491 for more details.

The current committed stubs are generated with mypy-protobuf 3.0.0.
pip can be forced to install particular versions of packages, such as with: 
```
pip install --force-reinstall 'mypy-protobuf==3.0.0'
```
