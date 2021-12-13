from poetry.plugins.application_plugin import ApplicationPlugin

from poetry_aws_lambda_plugin.commands.aws_lambda_build import AwsLambdaBuild


class AwsLambdaApplicationPlugin(ApplicationPlugin):
    def activate(self, application):
        application.command_loader.register_factory(AwsLambdaBuild.name, AwsLambdaBuild)
