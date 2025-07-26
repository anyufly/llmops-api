from contextlib import AbstractAsyncContextManager
from typing import Any, Callable, cast

from loguru._logger import Logger
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload

from llmops_api.base.db.model import User
from llmops_api.base.db.repo import Paginator, QueryConfig
from llmops_api.base.view.model import PaginationListViewModel
from llmops_api.exception.user import UsernameExists, UserNotExists
from llmops_api.form.user import UserListQuery
from llmops_api.repo.user import UserRepo
from llmops_api.view.user import UserViewModel


class UserService:
    def __init__(
        self,
        repo: UserRepo,
        transaction_factory: Callable[..., AbstractAsyncContextManager[AsyncSession]],
        logger: Logger,
    ):
        self.repo = repo
        self.transaction_factory = transaction_factory
        self.logger = logger

    async def add_user(self, user: User) -> UserViewModel:
        async with self.transaction_factory() as session:
            username_exists = await self.repo.exists_username(session, user.username)
            if username_exists:
                raise UsernameExists

            await self.repo.add(session, user)

            return user.to_pydantic(UserViewModel)

    async def edit_user(self, user_id: int, **kwargs: Any) -> UserViewModel:
        async with self.transaction_factory() as session:
            user_exists = await self.repo.exists(session, user_id)
            if not user_exists:
                raise UserNotExists

            if len(kwargs.keys()) > 0:
                await self.repo.update_by_id(session, user_id, **kwargs)

        return await self.get_user(user_id)

    async def delete_user(self, user_id: int, delete_by: int) -> None:
        async with self.transaction_factory() as session:
            user_exists = await self.repo.exists(session, user_id)
            if not user_exists:
                raise UserNotExists

            await self.repo.remove_by_id(session, user_id, delete_by=delete_by)

    async def get_user(self, user_id: int) -> UserViewModel:
        async with self.transaction_factory() as session:
            user = await self.repo.get_by_id(
                session,
                user_id,
                options=[
                    joinedload(User.creator),
                    joinedload(User.updator),
                ],
            )

        if user is None:
            raise UserNotExists

        return user.to_pydantic(UserViewModel)

    async def user_list(
        self, user_list_query: UserListQuery
    ) -> PaginationListViewModel[UserViewModel]:
        async with self.transaction_factory() as session:
            result = await self.repo.fetch_list(
                session,
                QueryConfig(
                    options=[joinedload(User.creator), joinedload(User.updator)],
                    condition=user_list_query,
                    paginator=Paginator(
                        page=user_list_query.page,
                        page_size=user_list_query.page_size,
                    ),
                    order_by=[User.create_at.desc()],
                ),
            )

            count, user_list = result

            user_view_list = [user.to_pydantic(UserViewModel) for user in user_list]
            return PaginationListViewModel[UserViewModel](
                items=user_view_list,
                page=user_list_query.page,
                page_size=user_list_query.page_size,
                total=cast(int, count),
            )
