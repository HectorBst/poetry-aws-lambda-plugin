from __future__ import annotations

from typing import TYPE_CHECKING

from cleo.io.outputs.output import Verbosity

from poetry_aws_lambda_plugin.steps.step import Step
from poetry_aws_lambda_plugin.utils.logging import write_lines, is_verbosity

if TYPE_CHECKING:
    from pathlib import Path
    from typing import IO, Set

    from poetry_aws_lambda_plugin.utils.config import Config


class Publisher(Step):
    def __init__(
            self,
            config: Config,
            io: IO,
            input_paths: Set[Path]
    ) -> None:
        super().__init__(
            config,
            io
        )

        self._input_paths = input_paths

    def do(self) -> None:
        paths = [path for path in self._input_paths if path.exists()]

        write_lines(self.io, "Publishing AWS Lambda package")
        if is_verbosity(self.io, Verbosity.VERBOSE):
            write_lines(
                self.io,
                *[str(path.relative_to(self.config.project_root_path)) for path in paths],
                stack_level=2,
                verbosity=Verbosity.VERBOSE
            )

        if not self.dry_run:
            for path in paths:
                self._publish(path)

        write_lines(self.io, "Published package")

    def _publish(self, path: Path) -> None:
        raise NotImplementedError()
