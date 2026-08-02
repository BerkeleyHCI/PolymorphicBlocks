from pathlib import Path
from typing import Optional, Any, Type, Iterable, Union, Dict, List, Tuple

import os
import subprocess
import sys
import jdk

from .. import edgir
from .. import edgrpc
from .BufferSerializer import BufferSerializer, BufferDeserializer
from .Core import builder
from .HierarchyBlock import Block
from .DesignTop import DesignTop
from .Refinements import Refinements


class CompilerCheckError(BaseException):
    pass


class CompiledDesign:
    @staticmethod
    def from_compiler_result(result: edgrpc.CompilerResult) -> "CompiledDesign":
        connections = [(conn.block_port, conn.link_port) for conn in result.connections]
        return CompiledDesign(
            result.design,
            [(value.path, value.value) for value in result.solvedValues],
            connections,
            list(result.errors),
        )

    @staticmethod
    def from_request(design: edgir.Design, values: Iterable[edgrpc.ExprValue]) -> "CompiledDesign":
        return CompiledDesign(design, [(value.path, value.value) for value in values], [], [])

    def __init__(
        self,
        design: edgir.Design,
        values: List[Tuple[edgir.LocalPath, edgir.ValueLit]],
        connections: List[Tuple[edgir.LocalPath, edgir.LocalPath]],
        errors: List[edgrpc.ErrorRecord],
    ):
        self.design = design
        self.contents = design.contents  # convenience accessor
        self.errors = errors
        self._values = {path.SerializeToString(): edgir.valuelit_to_lit(value) for path, value in values}
        self._block_to_link_ports = {block_port.SerializeToString(): link_port for block_port, link_port in connections}
        self._link_to_block_ports: Dict[bytes, List[edgir.LocalPath]] = {}
        for block_port, link_port in connections:
            link_port_str = link_port.SerializeToString()
            self._link_to_block_ports.setdefault(link_port_str, []).append(block_port)

    def errors_str(self) -> str:
        err_strs = []
        for error in self.errors:
            error_pathname = edgir.local_path_to_str(error.path)
            if error.name:
                error_pathname += ":" + error.name
            err_strs.append(f"{error.kind} @ {error_pathname}: {error.details}")
        return "\n".join([f"- {err_str}" for err_str in err_strs])

    # Reserved.V is a string because it doesn't load properly at runtime
    # Serialized strings are used since proto objects are mutable and unhashable
    def get_value(
        self, path: Union[edgir.LocalPath, Iterable[Union[str, "edgir.Reserved.V"]]]
    ) -> Optional[edgir.LitTypes]:
        if isinstance(path, edgir.LocalPath):
            localpath = path
        else:
            localpath = edgir.LocalPathList(path)
        return self._values.get(localpath.SerializeToString(), None)

    def append_values(self, values: List[Tuple[edgir.LocalPath, edgir.ValueLit]]) -> None:
        """Append solved values to this design, such as from a refinement pass"""
        for value_path, value_value in values:
            value_path_str = value_path.SerializeToString()
            assert value_path_str not in self._values
            self._values[value_path_str] = edgir.valuelit_to_lit(value_value)

    def get_connected_link_port(self, block_port: edgir.LocalPath) -> Optional[edgir.LocalPath]:
        """For a block port, return the connected link side port."""
        return self._block_to_link_ports.get(block_port.SerializeToString())

    def get_connected_block_ports(self, link_port: edgir.LocalPath) -> Optional[List[edgir.LocalPath]]:
        """For a link port, return connected block side ports (possibly multiple through an export chain)."""
        return self._link_to_block_ports.get(link_port.SerializeToString())


class ScalaCompilerInstance:
    kDevRelpath = "../../compiler/target/scala-2.13/edg-compiler-assembly-0.1-SNAPSHOT.jar"
    kPrecompiledRelpath = "resources/edg-compiler-precompiled.jar"
    kJreVersion = 17
    kInstallJrePath = Path.home() / ".edg" / f"jre-{kJreVersion}"

    def __init__(self) -> None:
        self.process: Optional[Any] = None

    def check_started(self) -> None:
        if self.process is None:
            installed = False
            java_bin: Optional[Path] = None
            while java_bin is None:
                if self.kInstallJrePath.exists():
                    items = [
                        item
                        for item in self.kInstallJrePath.iterdir()
                        if item.is_dir() and ("jre" in item.name or "jdk" in item.name)
                    ]
                    if len(items) > 0:
                        if len(items) != 1:
                            raise RuntimeError(f"Expected one JRE in {self.kInstallJrePath}, delete extras and re-run.")
                        java_bin_path = items[0] / "bin"
                        if not java_bin_path.exists() or not java_bin_path.is_dir():
                            raise RuntimeError(f"Expected JRE bin folder {java_bin_path} to exist.")
                        java_bin = java_bin_path / "java"  # can't test this since it has os-specific extensions

                if java_bin is None:
                    if installed:
                        raise RuntimeError("Internal error, failed to install JRE")
                    print("Installing JRE for compiler core...")
                    self.kInstallJrePath.mkdir(parents=True, exist_ok=True)
                    jdk.install(str(self.kJreVersion), path=str(self.kInstallJrePath), jre=True)
                    installed = True

            dev_path = os.path.join(os.path.dirname(__file__), self.kDevRelpath)
            precompiled_path = os.path.join(os.path.dirname(__file__), self.kPrecompiledRelpath)
            if os.path.exists(dev_path):
                jar_path = dev_path
                print("Using development JAR")
            elif os.path.exists(precompiled_path):
                jar_path = precompiled_path
            else:
                raise ValueError(f"No EDG Compiler JAR found")

            self.process = subprocess.Popen(
                [str(java_bin), "-jar", jar_path], stdin=subprocess.PIPE, stdout=subprocess.PIPE
            )

    def compile(
        self, block: Type[Block], refinements: Refinements = Refinements(), *, ignore_errors: bool = False
    ) -> CompiledDesign:
        from ..hdl_server.__main__ import process_request

        self.check_started()

        assert self.process is not None
        assert self.process.stdin is not None
        assert self.process.stdout is not None
        request_serializer = BufferSerializer[edgrpc.CompilerRequest](self.process.stdin)

        block_obj = block()
        request = edgrpc.CompilerRequest(design=edgir.Design(contents=builder.elaborate_toplevel(block_obj)))
        if isinstance(block_obj, DesignTop):
            refinements = block_obj.refinements() + refinements
        refinements.populate_proto(request.refinements)

        # write the initial request to the compiler process
        request_serializer.write(request)

        # until the compiler gives back the response, this acts as the HDL server,
        # taking requests in the opposite direction
        assert self.process.stdin is not None
        assert self.process.stdout is not None
        hdl_request_deserializer = BufferDeserializer(edgrpc.HdlRequest, self.process.stdout)
        hdl_response_serializer = BufferSerializer[edgrpc.HdlResponse](self.process.stdin)
        while True:
            sys.stdout.buffer.write(hdl_request_deserializer.read_stdout())
            sys.stdout.buffer.flush()
            hdl_request = hdl_request_deserializer.read()
            assert hdl_request is not None
            hdl_response = process_request(hdl_request)
            if hdl_response is None:
                break
            hdl_response_serializer.write(hdl_response)

        response_deserializer = BufferDeserializer(edgrpc.CompilerResult, self.process.stdout)
        result = response_deserializer.read()

        sys.stdout.buffer.write(response_deserializer.read_stdout())
        sys.stdout.buffer.flush()

        assert result is not None
        assert result.HasField("design")
        design = CompiledDesign.from_compiler_result(result)
        if result.errors and not ignore_errors:
            raise CompilerCheckError(f"error during compilation:\n{design.errors_str()}")
        return design

    def close(self) -> None:
        assert self.process is not None
        self.process.stdin.close()
        self.process.stdout.close()
        self.process.stderr.close()
        self.process.wait()


ScalaCompiler = ScalaCompilerInstance()
