from __future__ import annotations

import shutil

from typing import TYPE_CHECKING

from cleo.io.outputs.output import Verbosity

from poetry_aws_lambda_plugin.slimmers.slimmer import Slimmer
from poetry_aws_lambda_plugin.utils.logging import write_lines, is_verbosity

if TYPE_CHECKING:
    from pathlib import Path
    from typing import Set


class FilesRemoverSlimmer(Slimmer):
    def find_directories(self, path: Path) -> Set[Path]:
        raise NotImplementedError()

    @property
    def description(self) -> str:
        raise NotImplementedError()

    @property
    def directories(self) -> bool:
        raise NotImplementedError()

    def do(self) -> None:
        found_paths = [
            (ip, fp)
            for ip in self.input_paths
            for fp in self.find_directories(ip)
        ]

        write_lines(self.io, f"Removing {self.description}")
        if is_verbosity(self.io, Verbosity.VERBOSE):
            paths = sorted([f"{path[1].relative_to(self.config.project_root_path)}" for path in found_paths])
            write_lines(self.io, *paths, stack_level=2, verbosity=Verbosity.VERBOSE)

        if not self.dry_run:
            for _, found_path in found_paths:
                if self.directories:
                    shutil.rmtree(found_path, ignore_errors=True)
                else:
                    found_path.unlink(missing_ok=True)

        write_lines(self.io, f"Removed {len(found_paths)} {'directories' if self.directories else 'files'}")


class BinDirectoryRemoverSlimmer(FilesRemoverSlimmer):
    def find_directories(self, path: Path) -> Set[Path]:
        return set(path.glob("bin"))

    @property
    def id(self) -> str:
        return "bin"

    @property
    def description(self) -> str:
        return "bin directory"

    @property
    def directories(self) -> bool:
        return True


class DistInfoDirectoriesRemoverSlimmer(FilesRemoverSlimmer):
    def find_directories(self, path: Path) -> Set[Path]:
        return set(path.glob("*.dist-info"))

    @property
    def id(self) -> str:
        return "dist-info"

    @property
    def description(self) -> str:
        return "dist-info directories"

    @property
    def directories(self) -> bool:
        return True


class PycacheDirectoriesRemoverSlimmer(FilesRemoverSlimmer):
    def find_directories(self, path: Path) -> Set[Path]:
        return set(path.rglob("__pycache__"))

    @property
    def id(self) -> str:
        return "__pycache__"

    @property
    def description(self) -> str:
        return "__pycache__ directories"

    @property
    def directories(self) -> bool:
        return True


class PyTypedFilesRemoverSlimmer(FilesRemoverSlimmer):
    def find_directories(self, path: Path) -> Set[Path]:
        return set(path.glob("**/py.typed"))

    @property
    def id(self) -> str:
        return "py.typed"

    @property
    def description(self) -> str:
        return "py.typed files"

    @property
    def directories(self) -> bool:
        return False


class TestsDirectoriesRemoverSlimmer(FilesRemoverSlimmer):
    def find_directories(self, path: Path) -> Set[Path]:
        return set(path.glob("**/tests"))

    @property
    def id(self) -> str:
        return "tests"

    @property
    def description(self) -> str:
        return "tests directories"

    @property
    def directories(self) -> bool:
        return True
