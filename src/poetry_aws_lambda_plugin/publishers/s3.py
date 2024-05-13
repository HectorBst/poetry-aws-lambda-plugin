from __future__ import annotations

from typing import TYPE_CHECKING

import boto3

from cleo.io.outputs.output import Verbosity

from poetry_aws_lambda_plugin.publishers.publisher import Publisher
from poetry_aws_lambda_plugin.utils.logging import write_lines, is_verbosity

if TYPE_CHECKING:
    from pathlib import Path


class S3Publisher(Publisher):
    def should_run(self) -> bool:
        return self.config.upload

    def _publish(self, path: Path) -> None:
        object_key = f"{self.config.object_key_prefix}{path.name}"
        write_lines(
            self.io,
            f"Uploading {path.name} to s3://{self.config.bucket_name}/{object_key}",
            stack_level=2
        )

        s3_client = boto3.client("s3")

        total_length = path.stat().st_size
        uploaded_length = 0

        def upload_callback(chunk: int) -> None:
            nonlocal uploaded_length
            uploaded_length += chunk
            percent = uploaded_length / total_length
            write_lines(
                self.io,
                f"Uploading: {percent:.2%}",
                stack_level=3,
                verbosity=Verbosity.VERBOSE
            )

        s3_client.upload_file(
            Filename=path,
            Bucket=self.config.bucket_name,
            Key=object_key,
            Callback=upload_callback if is_verbosity(self.io, Verbosity.VERBOSE) else None
        )
