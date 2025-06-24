from dataclasses import dataclass
from typing import Optional, Set, Type

from pydantic import BaseModel


@dataclass
class Relation:
    pydantic_model: Type[BaseModel]
    include: Optional[Set[str]] = None
    exclude: Optional[Set[str]] = None
