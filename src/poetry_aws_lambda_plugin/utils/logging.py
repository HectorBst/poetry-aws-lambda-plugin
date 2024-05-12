from __future__ import annotations

from contextlib import contextmanager
from typing import TYPE_CHECKING

from cleo.io.outputs.output import Verbosity

if TYPE_CHECKING:
    from cleo.io.io import IO


def write_lines(
        io: IO,
        *messages: str,
        stack_level: int = 1,
        verbosity: Verbosity = Verbosity.NORMAL
) -> None:
    formatted_messages = [f"{'  ' * stack_level}- {message}" for message in messages]
    io.write_line(formatted_messages, verbosity=verbosity)


def is_verbosity(io: IO, verbosity: Verbosity) -> bool:
    return verbosity.value <= io.output.verbosity.value
