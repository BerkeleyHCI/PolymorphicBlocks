IR definition in protocol buffer format.

You will need [mypy-protobuf](https://github.com/dropbox/mypy-protobuf) (to generate type stubs) and protoletariat (post-processing to use relative imports)
```commandline
pip install mypy-protobuf
pip install protoletariat
```

To compile, run in this directory:

```
protoc --proto_path=. --python_out=.. --mypy_out=.. edgir/*.proto edgrpc/*.proto
protol --in-place --python-out .. protoc --proto-path=. edgir/*.proto edgrpc/*.proto
```

If installing with `pip` under Ubuntu, you may have to invoke `pip` with `sudo` so the executables are found in your PATH. 

The current committed stubs are generated with mypy-protobuf 3.0.0.
pip can be forced to install particular versions of packages, such as with: 
```
pip install --force-reinstall 'mypy-protobuf==3.0.0'
```
