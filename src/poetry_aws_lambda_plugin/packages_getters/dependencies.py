from __future__ import annotations

from typing import TYPE_CHECKING

from cleo.io.outputs.output import Verbosity
from poetry.utils.env import MockEnv

from poetry_aws_lambda_plugin.packages_getters.package_getter import PackagesGetter
from poetry_aws_lambda_plugin.utils.logging import write_lines

if TYPE_CHECKING:
    from pathlib import Path
    from typing import List

    from cleo.io.io import IO
    from poetry.installation import Installer
    from poetry.installation.operations.operation import Operation
    from poetry.utils.env import Env

    from poetry_aws_lambda_plugin.utils.config import Config


class DependenciesPackagesGetter(PackagesGetter):
    def __init__(
            self,
            config: Config,
            io: IO,
            installer: Installer
    ) -> None:
        super().__init__(
            config,
            io,
            config.lambda_artefacts_path
            .joinpath("packages")
            .joinpath("dependencies")
            .joinpath(config.lambda_architecture.pip_machine)
        )

        self._installer = installer

    def should_run(self) -> bool:
        return not self.config.only_root

    def do(self) -> None:
        # hook, custom installer
        lambda_env = LambdaEnv(self.config, self.output_path)
        self._installer._env = lambda_env
        self._installer._executor = LambdaExecutor(
            lambda_env,
            self.io,
            self.config.dry_run,
            self.io.is_verbose()
        )
        self._installer._installed_repository = self._installer._get_installed()
        # end hook

        self._installer.only_groups(self.config.activated_groups)
        self._installer.dry_run(self.config.dry_run)
        self._installer.verbose(self.io.is_verbose())

        self._installer.run()


class LambdaEnv(MockEnv):
    def __init__(
            self,
            config: Config,
            path: Path
    ):
        python_version = config.lambda_runtime_python_version

        version_info = [python_version.major, python_version.minor, 0]
        python_implementation = "CPython"
        platform = "manylinux2014"
        platform_machine = config.lambda_architecture.pip_machine

        super().__init__(
            version_info=version_info,
            path=path,
            python_implementation=python_implementation,
            platform=platform,
            platform_machine=platform_machine,
            os_name="posix",
            is_venv=False,
            sys_path=[],
            marker_env={
                "python_implementation": python_implementation,
                "version_info": version_info,
                "python_version": f"{version_info[0]}.{version_info[1]}",
                "python_full_version": f"{version_info[0]}.{version_info[1]}.{version_info[2]}",
                "sys_platform": platform,
                "platform_machine": platform_machine,
                "interpreter_name": python_implementation.lower(),
                "interpreter_version": f"cp{version_info[0]}{version_info[1]}"
            },
            execute=not config.dry_run
        )


class LambdaExecutor:
    def __init__(
            self,
            env: Env,
            io: IO,
            dry_run: bool,
            verbose: bool
    ):
        self._env = env
        self._io = io
        self._dry_run = dry_run
        self._verbose = verbose

    def execute(self, operations: List[Operation]) -> int:
        for operation in operations:
            if operation.job_type != "install":
                raise ValueError(f"Unexpected operation job type {operation.job_type} for {operation}")

        pip_packages = sorted([f"{operation.package.name}=={operation.package.version}" for operation in operations])
        write_lines(self._io, "Installing dependencies packages")
        write_lines(self._io, *pip_packages, stack_level=2, verbosity=Verbosity.VERBOSE)

        pip_args = [
            "install",
            *pip_packages,
            "--no-deps",
            "--disable-pip-version-check",
            "--isolated",
            "--no-input",
            "--no-compile",
            "--python-version", self._env.marker_env['python_version'],
            "--platform", f"{self._env.marker_env['sys_platform']}_{self._env.marker_env['platform_machine']}",
            "--implementation", "cp",
            "--only-binary=:all:",
            "--target", str(self._env.path)
        ]

        write_lines(self._io, " ".join(["pip", *pip_args]), stack_level=2, verbosity=Verbosity.VERY_VERBOSE)

        if not self._dry_run:
            pip_output = self._env.run_pip(*pip_args)
            write_lines(self._io, pip_output, stack_level=2, verbosity=Verbosity.VERY_VERBOSE)

        write_lines(self._io, f"Installed {len(pip_packages)} packages")

        return 0

    def dry_run(self, dry_run: bool = True) -> "LambdaExecutor":
        self._dry_run = dry_run

        return self

    def verbose(self, verbose: bool = True) -> "LambdaExecutor":
        self._verbose = verbose

        return self

    @property
    def enabled(self) -> bool:
        return True
