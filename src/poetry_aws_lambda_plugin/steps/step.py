from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from cleo.io.io import IO

    from poetry_aws_lambda_plugin.utils.config import Config


class Step:
    def __init__(
            self,
            config: Config,
            io: IO
    ) -> None:
        self._config = config
        self._io = io

    @property
    def config(self) -> Config:
        return self._config

    @property
    def io(self) -> IO:
        return self._io

    def should_run(self) -> bool:
        return True

    def clean(self) -> None:
        pass

    def do(self) -> None:
        pass

    def run(self) -> None:
        self.clean()

        if self.should_run():
            self.do()

    @property
    def dry_run(self) -> bool:
        return self._config.dry_run
