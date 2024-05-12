from __future__ import annotations

import sys
import traceback

from functools import cached_property
from typing import TYPE_CHECKING

from cleo.helpers import option
from poetry.console.commands.group_command import GroupCommand
from poetry.console.commands.installer_command import InstallerCommand

from poetry_aws_lambda_plugin.builders.zip import FunctionBuilder, LayerBuilder
from poetry_aws_lambda_plugin.packages_getters.dependencies import DependenciesPackagesGetter
from poetry_aws_lambda_plugin.packages_getters.project import ProjectPackageGetter
from poetry_aws_lambda_plugin.slimmers.files_remover import BinDirectoryRemoverSlimmer, DistInfoDirectoriesRemoverSlimmer, \
    TestsDirectoriesRemoverSlimmer, PycacheDirectoriesRemoverSlimmer, PyTypedFilesRemoverSlimmer
from poetry_aws_lambda_plugin.utils.config import Config
from poetry_aws_lambda_plugin.utils.enums import LambdaResource, describe_enum_config, LambdaArchitecture
from poetry_aws_lambda_plugin.utils.exceptions import PoetryAwsLambdaPluginException

if TYPE_CHECKING:
    from typing import List

    from poetry_aws_lambda_plugin.steps.step import Step


class BuildAwsLambdaCommand(InstallerCommand):
    name = "build-aws-lambda"
    description = "Build the lambda function and/or layer."

    options = [
        *GroupCommand._group_dependency_options(),
        option(
            "no-root",
            None,
            "Do not install the root package (the current project) and install only dependencies."
        ),
        option(
            "only-root",
            None,
            "Exclude all dependencies and only install the root package (the current project)."
        ),
        option(
            "resource",
            "r",
            f"Lambda resource to build ({describe_enum_config(LambdaResource)})",
            flag=False,
            default=LambdaResource.FUNCTION.name.lower()
        ),
        option(
            "architecture",
            "a",
            f"Lambda architecture ({describe_enum_config(LambdaArchitecture)})",
            flag=False,
            default=LambdaArchitecture.X86_64.name.lower()
        )
    ]

    @cached_property
    def config(self) -> Config:
        return Config(self)

    def _get_steps(self) -> List[Step]:
        steps: List[Step] = []

        dependencies = DependenciesPackagesGetter(
            self.config,
            self.io,
            self.installer
        )
        steps.append(dependencies)
        project = ProjectPackageGetter(
            self.config,
            self.io,
            self.poetry
        )
        steps.append(project)

        bin_directory = BinDirectoryRemoverSlimmer(
            self.config,
            self.io,
            {dependencies.output_path}
        )
        steps.append(bin_directory)
        dist_info = DistInfoDirectoriesRemoverSlimmer(
            self.config,
            self.io,
            {dependencies.output_path}
        )
        steps.append(dist_info)
        pycache = PycacheDirectoriesRemoverSlimmer(
            self.config,
            self.io,
            {dependencies.output_path, project.output_path}
        )
        steps.append(pycache)
        pytyped = PyTypedFilesRemoverSlimmer(
            self.config,
            self.io,
            {dependencies.output_path}
        )
        steps.append(pytyped)
        tests = TestsDirectoriesRemoverSlimmer(
            self.config,
            self.io,
            {dependencies.output_path}
        )
        steps.append(tests)

        function = FunctionBuilder(
            self.config,
            self.io,
            {dependencies.output_path, project.output_path},
            self.poetry.package
        )
        steps.append(function)
        layer = LayerBuilder(
            self.config,
            self.io,
            {dependencies.output_path, project.output_path},
            self.poetry.package
        )
        steps.append(layer)

        return steps

    def handle(self) -> int:
        try:
            steps = self._get_steps()

            self.line(
                f"Building AWS Lambda <c2>{self.config.lambda_resource.resource_name}</c2> "
                f"(<c2>{self.config.lambda_architecture.pip_machine}</c2>) "
                f"<c1>{self.poetry.package.pretty_name}</c1> "
                f"(<c2>{self.poetry.package.version}</c2>)"
            )
            for step in steps:
                step.run()

            return 0
        except PoetryAwsLambdaPluginException as e:
            self.line_error(f"<error>{e.line_error}</error>")
            if self.io.is_verbose():
                traceback.print_exception(*sys.exc_info(), file=self.io)
            return 1
