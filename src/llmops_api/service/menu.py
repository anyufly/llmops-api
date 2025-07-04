from contextlib import AbstractAsyncContextManager
from typing import Any, Callable

from loguru._logger import Logger
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload, selectinload

from llmops_api.base.db.repo import QueryConfig
from llmops_api.base.view.model import ListViewModel
from llmops_api.exception.menu import (
    MenuHasAction,
    MenuHasChild,
    MenuNameExists,
    MenuNotExists,
    ParentMenuNotExists,
)
from llmops_api.form.menu import MenuQuery
from llmops_api.model.menu import Menu
from llmops_api.repo.action import ActionRepo
from llmops_api.repo.menu import (
    FetchFirstLevelMenuByMenuQuery,
    FetchSecondLevelMenuByMenuQuery,
    FindMenuByName,
    MenuRepo,
)
from llmops_api.view.menu import MenuViewModel


class MenuService:
    def __init__(
        self,
        menu_repo: MenuRepo,
        action_repo: ActionRepo,
        transaction_factory: Callable[..., AbstractAsyncContextManager[AsyncSession]],
        logger: Logger,
    ):
        self.transaction_factory = transaction_factory
        self.logger = logger
        self.menu_repo = menu_repo
        self.action_repo = action_repo

    async def _check_menu_name_exists(self, session: AsyncSession, name: str):
        menu_name_exists = await self.menu_repo.exists_when(session, FindMenuByName(name))

        if menu_name_exists:
            raise MenuNameExists

    async def add_menu(self, menu: Menu) -> MenuViewModel:
        async with self.transaction_factory() as session:
            if menu.parent_id is not None:
                parant_menu = await self.menu_repo.get_by_id(session, menu.parent_id)
                if parant_menu is None:
                    raise ParentMenuNotExists
                menu.menu_type = parant_menu.menu_type

            await self._check_menu_name_exists(session, menu.name)
            await self.menu_repo.add(session, menu)
            return menu.to_pydantic(MenuViewModel)  # type: ignore

    async def delete_menu(self, menu_id: int, delete_by: int) -> None:
        async with self.transaction_factory() as session:
            menu_exists = await self.menu_repo.exists(session, menu_id)

            if not menu_exists:
                raise MenuNotExists

            has_child = await self.menu_repo.has_child(session, menu_id)

            if has_child:
                raise MenuHasChild

            has_action = await self.action_repo.exists_action_in_menu(session, menu_id)

            if has_action:
                raise MenuHasAction

            await self.menu_repo.remove_by_id(session, menu_id, delete_by=delete_by)

    async def get_menu(self, menu_id: int) -> MenuViewModel:
        async with self.transaction_factory() as session:
            menu = await self.menu_repo.get_by_id(
                session,
                menu_id,
                options=[joinedload(Menu.creator), joinedload(Menu.updator)],
            )

            if menu is None:
                raise MenuNotExists

            return menu.to_pydantic(MenuViewModel)  # type: ignore

    async def add_child_menu(self, parent_id: int, menu: Menu) -> MenuViewModel:
        menu.parent_id = parent_id
        return await self.add_menu(menu)

    async def edit_menu(self, menu_id: int, **kwargs: Any):
        async with self.transaction_factory() as session:
            menu_exists = await self.menu_repo.exists(session, menu_id)

            if not menu_exists:
                raise MenuNotExists

            name = kwargs.get("name")
            if name is not None:
                await self._check_menu_name_exists(session, name)

            await self.menu_repo.update_by_id(session, menu_id, **kwargs)

        return await self.get_menu(menu_id)

    async def menu_list(self, menu_query: MenuQuery):
        async with self.transaction_factory() as session:
            _, first_level_menus = await self.menu_repo.fetch_list(
                session,
                QueryConfig(
                    condition=FetchFirstLevelMenuByMenuQuery(menu_query),
                    options=[
                        joinedload(Menu.creator),
                        joinedload(Menu.updator),
                        selectinload(Menu.actions),
                    ],
                    order_by=[Menu.create_at.desc()],
                ),
            )

            first_level_menus = [menu.to_pydantic(MenuViewModel) for menu in first_level_menus]
            first_level_menu_ids = [menu.id for menu in first_level_menus]  # type: ignore

            _, second_level_menus = await self.menu_repo.fetch_list(
                session,
                QueryConfig(
                    condition=FetchSecondLevelMenuByMenuQuery(first_level_menu_ids, menu_query),
                    options=[
                        joinedload(Menu.creator),
                        joinedload(Menu.updator),
                        selectinload(Menu.actions),
                    ],
                    order_by=[Menu.create_at.desc()],
                ),
            )

            second_level_menu_dict = {
                first_level_menu_id: [] for first_level_menu_id in first_level_menu_ids
            }
            for menu in second_level_menus:
                second_level_menu_dict[menu.parent_id].append(menu.to_pydantic(MenuViewModel))

            for menu in first_level_menus:
                menu.children = second_level_menu_dict.get(menu.id)  # type: ignore

            return ListViewModel[MenuViewModel](items=first_level_menus)  # type: ignore
