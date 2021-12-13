from cleo.commands.command import Command


class AwsLambdaBuild(Command):
    name = "aws-lambda-build"

    def handle(self) -> int:
        self.line("Hello world, handle!")

        return 0
