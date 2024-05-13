from __future__ import annotations

from functools import cached_property, lru_cache
from typing import TYPE_CHECKING

from poetry.core.constraints.version import Version, VersionRange
from poetry_aws_lambda_plugin.utils.enums import LambdaResource, LambdaArchitecture, CompressionAlgorithm
from poetry_aws_lambda_plugin.utils.exceptions import PoetryAwsLambdaPluginException

if TYPE_CHECKING:
    from pathlib import Path
    from typing import Set, Optional

    from poetry.console.commands.group_command import GroupCommand


class Config:
    def __init__(
            self,
            command: GroupCommand
    ) -> None:
        self._command = command

    @cached_property
    def all_artefacts_path(self) -> Path:
        return self._command.poetry.pyproject_path.parent.joinpath("dist")

    @cached_property
    def lambda_artefacts_path(self) -> Path:
        return self.all_artefacts_path.joinpath("lambda")

    @cached_property
    def dry_run(self) -> bool:
        return self._command.option("dry-run")

    @cached_property
    def activated_groups(self) -> Set[str]:
        return self._command.activated_groups

    @cached_property
    def no_root(self) -> bool:
        return self._command.option("no-root")

    @cached_property
    def only_root(self) -> bool:
        return self._command.option("only-root")

    @cached_property
    def lambda_runtime_python_version(self) -> Version:
        python_constraint = self._command.poetry.package.python_constraint
        python_version = None
        if isinstance(python_constraint, VersionRange):
            if python_constraint.include_min:
                python_version = python_constraint.min

        if (python_version is None) or (python_version.major is None) or (python_version.minor is None):
            raise PoetryAwsLambdaPluginException(
                f"Cannot determine a Lambda Python Runtime "
                f"from package Python constraint {python_constraint}"
            )

        return Version.parse(f"{python_version.major}.{python_version.minor}")

    @cached_property
    def lambda_resource(self) -> LambdaResource:
        resource_option = self._command.option("lambda-resource").upper()
        if resource_option not in LambdaResource.__members__:
            raise PoetryAwsLambdaPluginException(
                f"Invalid Lambda Resource ({resource_option}), "
                f"must be one of {', '.join(LambdaResource.__members__)}."
            )
        return LambdaResource[resource_option]

    @cached_property
    def lambda_architecture(self) -> LambdaArchitecture:
        architecture_option = self._command.option("lambda-architecture").upper()
        if architecture_option not in LambdaArchitecture.__members__:
            raise PoetryAwsLambdaPluginException(
                f"Invalid Lambda Architecture ({architecture_option}), "
                f"must be one of {', '.join(LambdaArchitecture.__members__)}."
            )
        return LambdaArchitecture[architecture_option]

    @cached_property
    def compression_algorithm(self) -> CompressionAlgorithm:
        algorithm_option = self._command.option("compression-algorithm").upper()
        if algorithm_option not in CompressionAlgorithm.__members__:
            raise PoetryAwsLambdaPluginException(
                f"Invalid Compression Algorithm ({algorithm_option}), "
                f"must be one of {', '.join(CompressionAlgorithm.__members__)}."
            )
        return CompressionAlgorithm[algorithm_option]

    @cached_property
    def compression_level(self) -> int:
        algorithm = self.compression_algorithm
        level_option = self._command.option("compression-level")
        if level_option is None:
            level_option = algorithm.min_compression_level
        else:
            level_option = int(level_option)

        if algorithm.adjustable:
            if (level_option < algorithm.min_compression_level) or (level_option > algorithm.max_compression_level):
                raise PoetryAwsLambdaPluginException(
                    f"Invalid Compression Level ({level_option}), "
                    f"must be between {algorithm.min_compression_level} and {algorithm.max_compression_level} "
                    f"for {algorithm.name}."
                )
        elif level_option != algorithm.min_compression_level:
            raise PoetryAwsLambdaPluginException(
                f"Invalid Compression Level ({level_option}), "
                f"must be {algorithm.min_compression_level} for {algorithm.name} (not adjustable)."
            )

        return level_option

    @cached_property
    def slimmers(self) -> Optional[Set[str]]:
        return (self._command.poetry.pyproject.data
                .get("aws-lambda", {})
                .get("slimmers", None))

    @lru_cache(maxsize=None)
    def slimmer_enabled(self, slimmer: str) -> bool:
        return (self.slimmers is None) or (slimmer in self.slimmers)
