from __future__ import annotations


class PoetryAwsLambdaPluginException(Exception):
    def __init__(
            self,
            line_error: str
    ):
        self.line_error = line_error
