from typing import Annotated

from pydantic import Field
from pydantic.dataclasses import dataclass


@dataclass(frozen=True, kw_only=True)
class Node:
    key_length: Annotated[int | None, Field(ge=2)] = None
