import dataclasses
from typing import List, Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.sql._typing import _ColumnExpressionArgument

from llmops_api.base.db.model import User
from llmops_api.base.db.repo import BaseRepo, Condition


@dataclasses.dataclass
class ExistsUsername(Condition):
    username: str

    def to_condition(self) -> List[_ColumnExpressionArgument[bool]]:
        return [
            User.username == self.username,
        ]


class FetchUserByIDs(Condition):
    def __init__(self, ids: List[int]):
        self.ids = ids

    def to_condition(self) -> List[_ColumnExpressionArgument[bool]]:
        return [User.id.in_(self.ids)]


class UserRepo(BaseRepo[User]):
    async def exists_username(self, session: AsyncSession, username: str) -> bool:
        return await self.exists_when(session, ExistsUsername(username=username))

    async def get_by_username(self, session: AsyncSession, username: str) -> Optional[User]:
        result = await session.scalars(
            select(User).where(User.username == username).where(User.delete_at.is_(None))
        )

        user = result.one_or_none()
        return user
