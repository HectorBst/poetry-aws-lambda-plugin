from __future__ import annotations

import shutil

from typing import TYPE_CHECKING

from cleo.io.outputs.output import Verbosity
from poetry.core.masonry.builders.builder import Builder

from poetry_aws_lambda_plugin.packages_getters.package_getter import PackagesGetter
from poetry_aws_lambda_plugin.utils.logging import write_lines, is_verbosity

if TYPE_CHECKING:
    from cleo.io.io import IO
    from poetry.core.poetry import Poetry

    from poetry_aws_lambda_plugin.utils.config import Config


class ProjectPackageGetter(PackagesGetter):
    def __init__(
            self,
            config: Config,
            io: IO,
            poetry: Poetry
    ) -> None:
        super().__init__(
            config,
            io,
            config.lambda_artefacts_path
            .joinpath("packages")
            .joinpath("project")
        )

        self._poetry = poetry

    def should_run(self) -> bool:
        return not self.config.no_root

    def do(self) -> None:
        builder = Builder(self._poetry)
        builder.format = "wheel"

        files = builder.find_files_to_add()

        write_lines(
            self.io,
            f"Installing current project "
            f"<c1>{self._poetry.package.pretty_name}</c1> "
            f"<c2>{self._poetry.package.version}</c2>"
        )
        if is_verbosity(self.io, Verbosity.VERBOSE):
            paths = sorted([file.relative_to_source_root() for file in files])
            write_lines(self.io, *paths, stack_level=2, verbosity=Verbosity.VERBOSE)

        if not self.dry_run:
            for file in files:
                dst = self.output_path.joinpath(file.relative_to_source_root())
                dst.parent.mkdir(parents=True, exist_ok=True)
                shutil.copy(file.path, dst)

        write_lines(self.io, f"Copied {len(files)} files from current project")
