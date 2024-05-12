from __future__ import annotations

import os
import zipfile
from pathlib import Path

from cleo.io.outputs.output import Verbosity

from poetry_aws_lambda_plugin.builders.builder import Builder
from poetry_aws_lambda_plugin.utils.enums import LambdaResource
from poetry_aws_lambda_plugin.utils.logging import write_lines


class ZipBuilder(Builder):
    def get_arc_file_path(self, path: Path, input_path: Path) -> Path:
        raise NotImplementedError()

    def description(self) -> str:
        raise NotImplementedError()

    def do(self) -> None:
        write_lines(self.io, f"Building {self.description()}")

        if not self.dry_run:
            with zipfile.ZipFile(
                    self.output_path,
                    mode="w",
                    compression=self.config.compression_type.numeric_constant,
                    compresslevel=self.config.compression_level
            ) as archive:
                for input_path in self.input_paths:
                    for root, _, files in os.walk(input_path):
                        for file in files:
                            file_path = Path(root).joinpath(file)
                            arc_file_path = self.get_arc_file_path(file_path, input_path)

                            if self.io.is_very_verbose():
                                self.io.write_line(
                                    f"Adding {file_path.relative_to(self.config.lambda_artefacts_path)} as {arc_file_path}.",
                                    verbosity=Verbosity.VERBOSE
                                )

                            archive.write(
                                file_path,
                                arcname=arc_file_path,
                                compress_type=self.config.compression_type.numeric_constant,
                                compresslevel=self.config.compression_level
                            )

        write_lines(self.io, f"Built <c1>{self.output_path.name}</c1>")


class FunctionBuilder(ZipBuilder):
    def should_run(self):
        return self.config.lambda_resource == LambdaResource.FUNCTION

    def get_arc_file_path(self, path: Path, input_path: Path) -> Path:
        return path.relative_to(input_path)

    def description(self) -> str:
        return "AWS Lambda function"


class LayerBuilder(ZipBuilder):
    def should_run(self):
        return self.config.lambda_resource == LambdaResource.LAYER

    def get_arc_file_path(self, path: Path, input_path: Path) -> Path:
        return Path("python").joinpath(path.relative_to(input_path))

    def description(self) -> str:
        return "AWS Lambda layer"
