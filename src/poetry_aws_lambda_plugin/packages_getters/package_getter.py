from __future__ import annotations

import shutil

from typing import TYPE_CHECKING

from poetry_aws_lambda_plugin.steps.step import Step

if TYPE_CHECKING:
    from pathlib import Path

    from cleo.io.io import IO

    from poetry_aws_lambda_plugin.utils.config import Config


class PackagesGetter(Step):
    def __init__(
            self,
            config: Config,
            io: IO,
            output_path: Path
    ) -> None:
        super().__init__(
            config,
            io
        )

        self._output_path = output_path

    @property
    def output_path(self) -> Path:
        return self._output_path

    def clean(self) -> None:
        if not self.dry_run:
            shutil.rmtree(self.output_path, ignore_errors=True)
