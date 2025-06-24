from typing import List

from sqlalchemy import or_
from sqlalchemy.sql._typing import _ColumnExpressionArgument

from llmops_api.base.db.repo import BaseRepo, Condition
from llmops_api.model.role import Role


class FetchRoleByIDs(Condition):
    def __init__(self, ids: List[int]):
        self.ids = ids

    def to_condition(self) -> List[_ColumnExpressionArgument[bool]]:
        return [Role.id.in_(self.ids)]


class FindRoleByName(Condition):
    def __init__(self, name: str):
        self.name = name

    def to_condition(self) -> List[_ColumnExpressionArgument[bool]]:
        return [Role.name == self.name]


class FindRoleByQuery(Condition):
    def __init__(self, query: str):
        self.query = query

    def to_condition(self) -> List[_ColumnExpressionArgument[bool]]:
        if self.query and self.query != "":
            return [or_(Role.name.like(f"{self.query}%"), Role.title.like(f"{self.query}%"))]

        return [True]


class RoleRepo(BaseRepo[Role]):
    pass
