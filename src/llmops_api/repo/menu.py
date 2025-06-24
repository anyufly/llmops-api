from typing import List

from sqlalchemy import or_
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.sql._typing import _ColumnExpressionArgument

from llmops_api.base.db.repo import BaseRepo, Condition
from llmops_api.form.menu import MenuQuery
from llmops_api.model.menu import Menu


class FindMenuByParentID(Condition):
    def __init__(self, parent_id: int):
        self.parent_id = parent_id

    def to_condition(self) -> List[_ColumnExpressionArgument[bool]]:
        return [Menu.parent_id == self.parent_id]


class FindMenuByIDs(Condition):
    def __init__(self, ids: List[int]):
        self.ids = ids

    def to_condition(self) -> List[_ColumnExpressionArgument[bool]]:
        return [Menu.id.in_(self.ids)]


class FindMenuByName(Condition):
    def __init__(self, name: str):
        self.name = name

    def to_condition(self) -> List[_ColumnExpressionArgument[bool]]:
        return [Menu.name == self.name]


class FetchFirstLevelMenuByMenuQuery(Condition):
    def __init__(self, menu_query: MenuQuery):
        self.menu_query = menu_query

    def to_condition(self) -> List[_ColumnExpressionArgument[bool]]:
        where = [Menu.parent_id.is_(None)]

        if self.menu_query.query != "":
            where.append(
                or_(
                    Menu.name.like(f"{self.menu_query.query}%"),
                    Menu.title.like(f"{self.menu_query.query}%"),
                )
            )

        if self.menu_query.menu_type is not None:
            where.append(Menu.menu_type == self.menu_query.menu_type)

        return where


class FetchSecondLevelMenuByMenuQuery(Condition):
    def __init__(self, menu_ids: List[int], menu_query: MenuQuery):
        self.menu_ids = menu_ids
        self.menu_query = menu_query

    def to_condition(self) -> List[_ColumnExpressionArgument[bool]]:
        where = [Menu.parent_id.in_(self.menu_ids)]

        if self.menu_query.query != "":
            where.append(
                or_(
                    Menu.name.like(f"{self.menu_query.query}%"),
                    Menu.title.like(f"{self.menu_query.query}%"),
                )
            )

        if self.menu_query.menu_type is not None:
            where.append(Menu.menu_type == self.menu_query.menu_type)

        return where


class MenuRepo(BaseRepo[Menu]):
    async def has_child(self, session: AsyncSession, id: int) -> bool:
        return await self.exists_when(session, FindMenuByParentID(id))
