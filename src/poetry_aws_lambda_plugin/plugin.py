from __future__ import annotations

from typing import TYPE_CHECKING

from poetry.plugins.application_plugin import ApplicationPlugin

from poetry_aws_lambda_plugin.commands.build_aws_lambda import BuildAwsLambdaCommand

if TYPE_CHECKING:
    from cleo.commands.command import Command
    from typing import List, Type


class AwsLambdaPlugin(ApplicationPlugin):

    @property
    def commands(self) -> List[Type[Command]]:
        return [BuildAwsLambdaCommand]
