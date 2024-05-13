from __future__ import annotations

import zipfile

from enum import Enum
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from typing import Type, Optional, Any


def describe_enum_config(
        enum: Type[Enum],
        default: Optional[Any] = None
) -> str:
    values = sorted([name.lower() for name in enum.__members__.keys()])
    desc = f"{', '.join(values[:-1])} or {values[-1]}"

    if default is not None:
        desc = f"{desc}, default to {default.name.lower()}"

    return desc


class CompressionAlgorithm(Enum):
    BZIP2 = (zipfile.ZIP_BZIP2, True, 1, 9)
    DEFLATED = (zipfile.ZIP_DEFLATED, True, 1, 9)
    LZMA = (zipfile.ZIP_LZMA, False, -1, -1)
    STORED = (zipfile.ZIP_STORED, False, -1, -1)

    @property
    def numeric_constant(self) -> int:
        return self.value[0]

    @property
    def adjustable(self) -> bool:
        return self.value[1]

    @property
    def min_compression_level(self) -> int:
        return self.value[2]

    @property
    def max_compression_level(self) -> int:
        return self.value[3]


class LambdaArchitecture(Enum):
    ARM64 = "aarch64"
    X86_64 = "x86_64"

    @property
    def pip_machine(self) -> str:
        return self.value

    @property
    def pip_platform(self) -> str:
        return f"manylinux2014_{self.pip_machine}"


class LambdaResource(Enum):
    FUNCTION = "function"
    LAYER = "layer"

    @property
    def resource_name(self) -> str:
        return self.value
