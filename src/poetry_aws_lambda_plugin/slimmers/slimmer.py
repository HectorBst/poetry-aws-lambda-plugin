from __future__ import annotations

from typing import TYPE_CHECKING

from poetry_aws_lambda_plugin.steps.step import Step

if TYPE_CHECKING:
    from pathlib import Path
    from typing import IO, Set

    from poetry_aws_lambda_plugin.utils.config import Config


class Slimmer(Step):
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

    @property
    def input_paths(self) -> Set[Path]:
        return self._input_paths

    @property
    def id(self) -> str:
        raise NotImplementedError()

    def should_run(self) -> bool:
        return self.config.slimmer_enabled(self.id)
