from __future__ import annotations

import shutil

from typing import TYPE_CHECKING

from poetry_aws_lambda_plugin.steps.step import Step

if TYPE_CHECKING:
    from pathlib import Path
    from typing import IO, Set

    from poetry.core.packages.project_package import ProjectPackage

    from poetry_aws_lambda_plugin.utils.config import Config


class Builder(Step):
    def __init__(
            self,
            config: Config,
            io: IO,
            input_paths: Set[Path],
            project_package: ProjectPackage
    ) -> None:
        super().__init__(
            config,
            io
        )

        self._input_paths = input_paths
        self._output_path = config.lambda_artefacts_path.joinpath(
            f"{project_package.name}-"
            f"{project_package.version}-"
            f"{config.lambda_architecture.pip_machine}-"
            f"{config.lambda_resource.resource_name}.zip"
        )

    @property
    def input_paths(self) -> Set[Path]:
        return self._input_paths

    @property
    def output_path(self) -> Path:
        return self._output_path

    def clean(self) -> None:
        if not self.dry_run:
            shutil.rmtree(self.output_path, ignore_errors=True)
