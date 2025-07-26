from dataclasses import dataclass
from typing import Literal, Optional, Set, Type, Union

from pydantic import BaseModel


@dataclass
class Relation:
    pydantic_model: Union[Type[BaseModel], Literal["self"]]
    include: Optional[Set[str]] = None
    exclude: Optional[Set[str]] = None
