from contextlib import AbstractAsyncContextManager
from typing import Any, Callable, Dict

from loguru._logger import Logger
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload

from llmops_api.base.casbin.enforcer import CasbinEnforcer
from llmops_api.base.db.repo import QueryConfig
from llmops_api.base.view.model import ListViewModel
from llmops_api.exception.role import RoleHasUsers, RoleNameExists, RoleNotExists
from llmops_api.model.role import Role
from llmops_api.repo.role import FindRoleByName, FindRoleByQuery, RoleRepo
from llmops_api.view.role import RoleViewModel


class RoleService:
    def __init__(
        self,
        repo: RoleRepo,
        enforcer: CasbinEnforcer,
        transaction_factory: Callable[..., AbstractAsyncContextManager[AsyncSession]],
        logger: Logger,
    ):
        self.repo = repo
        self.enforcer = enforcer
        self.transaction_factory = transaction_factory
        self.logger = logger

    async def role_list(self, query: str = "") -> ListViewModel[RoleViewModel]:
        async with self.transaction_factory() as session:
            _, role_list = await self.repo.fetch_list(
                session,
                QueryConfig(
                    condition=FindRoleByQuery(query),
                    order_by=[Role.create_at.desc()],
                    options=[joinedload(Role.creator), joinedload(Role.updator)],
                ),
            )

            role_view_list = [role.to_pydantic(RoleViewModel) for role in role_list]
            return ListViewModel[RoleViewModel](items=role_view_list)

    async def _check_role_name_exists(self, session: AsyncSession, name: str):
        role_name_exists = await self.repo.exists_when(session, FindRoleByName(name))

        if role_name_exists:
            raise RoleNameExists

    async def add_role(self, role: Role) -> RoleViewModel:
        async with self.transaction_factory() as session:
            await self._check_role_name_exists(session, role.name)
            await self.repo.add(session, role)
            return role.to_pydantic(RoleViewModel)

    async def get_role(self, role_id: int) -> RoleViewModel:
        async with self.transaction_factory() as session:
            role = await self.repo.get_by_id(
                session,
                role_id,
                options=[joinedload(Role.creator), joinedload(Role.updator)],
            )

            if role is None:
                raise RoleNotExists

            return role.to_pydantic(RoleViewModel)

    async def edit_role(self, role_id: int, **kwargs: Any) -> RoleViewModel:
        async with self.transaction_factory() as session:
            role_exists = await self.repo.exists(session, role_id)

            if not role_exists:
                raise RoleNotExists

            name = kwargs.get("name")
            if name is not None:
                await self._check_role_name_exists(session, name)

            await self.repo.update_by_id(session, role_id, **kwargs)

        return await self.get_role(role_id)

    async def delete_role(self, role_id: int, delete_by: int) -> None:
        users = await self.enforcer.enforcer.get_users_for_role(f"role::{role_id}")
        if len(users) > 0:
            raise RoleHasUsers
        async with self.transaction_factory() as session:
            role_exists = await self.repo.exists(session, role_id)
            if not role_exists:
                raise RoleNotExists

            await self.repo.remove_by_id(session, role_id, delete_by=delete_by)
