from contextlib import AbstractAsyncContextManager
from typing import Any, Callable, Dict

from loguru._logger import Logger
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload

from llmops_api.base.casbin.enforcer import CasbinEnforcer
from llmops_api.base.db.repo import QueryConfig
from llmops_api.base.view.model import ListViewModel
from llmops_api.exception.action import ActionInUse, ActionNameExists, ActionNotExists
from llmops_api.exception.menu import MenuNotExists
from llmops_api.model.menu import Action
from llmops_api.repo.action import ActionRepo, FetchActionByMenuIDAndQuery, FindActionByName
from llmops_api.repo.menu import MenuRepo
from llmops_api.view.action import ActionViewModel


class ActionService:
    def __init__(
        self,
        casbin_enforcer: CasbinEnforcer,
        action_repo: ActionRepo,
        menu_repo: MenuRepo,
        transaction_factory: Callable[..., AbstractAsyncContextManager[AsyncSession]],
        logger: Logger,
    ):
        self.casbin_enforcer = casbin_enforcer
        self.action_repo = action_repo
        self.menu_repo = menu_repo
        self.transaction_factory = transaction_factory
        self.logger = logger

    async def get_action(self, action_id: int) -> ActionViewModel:
        async with self.transaction_factory() as session:
            action = await self.action_repo.get_by_id(
                session,
                action_id,
                options=[joinedload(Action.creator), joinedload(Action.updator)],
            )

            if action is None:
                raise ActionNotExists

            return action.to_pydantic(ActionViewModel)

    async def get_menu_actions(
        self, menu_id: int, query: str = ""
    ) -> ListViewModel[ActionViewModel]:
        async with self.transaction_factory() as session:
            menu_exists = await self.menu_repo.exists(session, menu_id)

            if not menu_exists:
                raise MenuNotExists

            _, action_list = await self.action_repo.fetch_list(
                session,
                QueryConfig(
                    condition=FetchActionByMenuIDAndQuery(menu_id, query),
                    order_by=[Action.create_at.desc()],
                    options=[joinedload(Action.creator), joinedload(Action.updator)],
                ),
            )

            view_list = [action.to_pydantic(ActionViewModel) for action in action_list]
            return ListViewModel[ActionViewModel](items=view_list)

    async def _check_action_name_exists(self, session: AsyncSession, name: str):
        action_name_exists = await self.action_repo.exists_when(session, FindActionByName(name))

        if action_name_exists:
            raise ActionNameExists

    async def add_menu_action(self, action: Action) -> ActionViewModel:
        async with self.transaction_factory() as session:
            menu_exists = await self.menu_repo.exists(session, action.menu_id)

            if not menu_exists:
                raise MenuNotExists

            await self._check_action_name_exists(session, action.name)

            await self.action_repo.add(session, action)

            return action.to_pydantic(ActionViewModel)

    async def delete_action(self, action_id: int) -> None:
        async with self.transaction_factory() as session:
            action = await self.action_repo.get_by_id(session, action_id)

            if action is None:
                raise ActionNotExists

            users = await self.casbin_enforcer.enforcer.get_implicit_users_for_permission(
                action.path, action.method.value
            )

            if len(users) > 0:
                raise ActionInUse

            await self.action_repo.remove_by_id(session, action_id)

    async def edit_action(self, action_id: int, **kwargs: Any) -> ActionViewModel:
        async with self.transaction_factory() as session:
            action_exists = await self.action_repo.exists(session, action_id)

            if not action_exists:
                raise ActionNotExists

            name = kwargs.get("name")
            if name is not None:
                await self._check_action_name_exists(session, name)

            await self.action_repo.update_by_id(session, action_id, **kwargs)
        return await self.get_action(action_id)
