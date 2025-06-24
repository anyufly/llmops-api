from dataclasses import dataclass
from typing import List, Tuple

from sqlalchemy import or_, tuple_
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.sql._typing import _ColumnExpressionArgument

from llmops_api.base.db.repo import BaseRepo, Condition
from llmops_api.model.menu import Action


@dataclass
class FindActionByName(Condition):
    name: str

    def to_condition(self) -> List[_ColumnExpressionArgument[bool]]:
        return [
            Action.name == self.name,
        ]


@dataclass
class FindActionByMenuID(Condition):
    menu_id: int

    def to_condition(self) -> List[_ColumnExpressionArgument[bool]]:
        return [Action.menu_id == self.menu_id]


@dataclass
class FindActionByPathAndMethod(Condition):
    path_and_method_tuple_list: List[Tuple[str, str]]

    def to_condition(self) -> List[_ColumnExpressionArgument[bool]]:
        return [tuple_(Action.path, Action.method).in_(self.path_and_method_tuple_list)]


class FetchActionByMenuIDAndQuery(FindActionByMenuID):
    def __init__(self, menu_id: int, query: str = ""):
        super().__init__(menu_id)
        self.query = query

    def to_condition(self) -> List[_ColumnExpressionArgument[bool]]:
        where = super().to_condition()

        if self.query and self.query != "":
            where.append(
                or_(Action.name.like(f"{self.query}%"), Action.title.like(f"{self.query}%"))
            )
        return where


class ActionRepo(BaseRepo[Action]):
    async def exists_action_in_menu(self, session: AsyncSession, menu_id: int):
        return await self.exists_when(session, FindActionByMenuID(menu_id))
