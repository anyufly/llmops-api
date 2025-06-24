from contextlib import AbstractAsyncContextManager
from typing import Callable

from loguru._logger import Logger
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload

from llmops_api.base.casbin.enforcer import CasbinEnforcer
from llmops_api.base.db.model import User
from llmops_api.base.db.repo import Paginator, QueryConfig
from llmops_api.base.view.model import ListViewModel, PaginationListViewModel
from llmops_api.enum.menu import ActionMethod
from llmops_api.exception.action import ActionNotExists
from llmops_api.exception.role import RoleNotExists
from llmops_api.exception.user import UserNotExists
from llmops_api.model.menu import Action, Menu
from llmops_api.model.role import Role
from llmops_api.repo.action import ActionRepo, FindActionByPathAndMethod
from llmops_api.repo.menu import FindMenuByIDs, MenuRepo
from llmops_api.repo.role import FetchRoleByIDs, RoleRepo
from llmops_api.repo.user import FetchUserByIDs, UserRepo
from llmops_api.view.action import ActionViewModel
from llmops_api.view.permissions import PermissionActionViewModel, PermissionViewModel
from llmops_api.view.role import RoleViewModel
from llmops_api.view.user import UserViewModel


class PermissionsService:
    def __init__(
        self,
        casbin_enforcer: CasbinEnforcer,
        transaction_factory: Callable[..., AbstractAsyncContextManager[AsyncSession]],
        user_repo: UserRepo,
        role_repo: RoleRepo,
        action_repo: ActionRepo,
        menu_repo: MenuRepo,
        logger: Logger,
    ):
        self.casbin_enforcer = casbin_enforcer
        self.transaction_factory = transaction_factory
        self.user_repo = user_repo
        self.role_repo = role_repo
        self.action_repo = action_repo
        self.menu_repo = menu_repo
        self.logger = logger

    async def _check_role_exists(self, session: AsyncSession, role_id: int) -> None:
        role_exists = await self.role_repo.exists(session, role_id)

        if not role_exists:
            raise RoleNotExists

    async def _check_user_exists(self, session: AsyncSession, user_id: int) -> None:
        user_exists = await self.user_repo.exists(session, user_id)

        if not user_exists:
            raise UserNotExists

    async def get_users_for_role(
        self, role_id: int, paginator: Paginator
    ) -> PaginationListViewModel[UserViewModel]:
        async with self.transaction_factory() as session:
            await self._check_role_exists(session, role_id)

            users = await self.casbin_enforcer.enforcer.get_users_for_role(f"role::{role_id}")

            user_ids = [int(user.split("::")[1]) for user in users]

            _, user_list = await self.user_repo.fetch_list(
                session,
                QueryConfig(
                    condition=FetchUserByIDs(user_ids),
                    order_by=[User.create_at.desc()],
                    paginator=paginator,
                ),
            )

            user_view_list = [user.to_pydantic(UserViewModel) for user in user_list]

            return PaginationListViewModel[UserViewModel](
                items=user_view_list,
                page=paginator.page,
                page_size=paginator.page_size,
                total=len(users),
            )

    async def get_roles_for_user(self, user_id: int) -> ListViewModel[RoleViewModel]:
        async with self.transaction_factory() as session:
            await self._check_user_exists(session, user_id)

            roles = await self.casbin_enforcer.enforcer.get_roles_for_user(f"user::{user_id}")
            role_ids = [int(role.split("::")[1]) for role in roles]

            _, role_list = await self.role_repo.fetch_list(
                session,
                QueryConfig(condition=FetchRoleByIDs(role_ids), order_by=[Role.create_at.desc()]),
            )

            role_view_list = [role.to_pydantic(RoleViewModel) for role in role_list]
            return ListViewModel[RoleViewModel](items=role_view_list)

    async def add_role_for_user(self, user_id: int, role_id: int) -> None:
        async with self.transaction_factory() as session:
            await self._check_role_exists(session, role_id)
            await self._check_user_exists(session, user_id)

        await self.casbin_enforcer.enforcer.add_role_for_user(
            f"user::{user_id}", f"role::{role_id}"
        )

    async def delete_role_for_user(self, user_id: int, role_id: int) -> None:
        async with self.transaction_factory() as session:
            await self._check_role_exists(session, role_id)
            await self._check_user_exists(session, user_id)

        await self.casbin_enforcer.enforcer.delete_role_for_user(
            f"user::{user_id}", f"role::{role_id}"
        )

    async def _get_action(self, session: AsyncSession, action_id: int) -> Action:
        action = await self.action_repo.get_by_id(session, action_id)
        if action is None:
            raise ActionNotExists
        return action

    async def get_action_for_role(self, role_id: int):
        permissions = await self.casbin_enforcer.enforcer.get_implicit_permissions_for_user(
            f"role::{role_id}"
        )
        permission_list = []
        for permission in permissions:
            _, path, method = permission
            permission_list.append((path, ActionMethod.load(method)))

        async with self.transaction_factory() as session:
            _, actions = await self.action_repo.fetch_list(
                session,
                QueryConfig(
                    condition=FindActionByPathAndMethod(path_and_method_tuple_list=permission_list),
                    order_by=[Action.create_at.desc()],
                ),
            )

            action_views = [action.to_pydantic(ActionViewModel) for action in actions]
            return ListViewModel[ActionViewModel](items=action_views)

    async def add_action_for_role(self, role_id: int, action_id: int) -> None:
        async with self.transaction_factory() as session:
            await self._check_role_exists(session, role_id)
            action = await self._get_action(session, action_id)
            path = action.path
            method = action.method.value

        await self.casbin_enforcer.enforcer.add_permission_for_user(
            f"role::{role_id}",
            path,
            method,
        )

    async def delete_action_for_role(self, role_id: int, action_id: int) -> None:
        async with self.transaction_factory() as session:
            await self._check_role_exists(session, role_id)
            action = await self._get_action(session, action_id)
            path = action.path
            method = action.method.value

        await self.casbin_enforcer.enforcer.delete_permission_for_user(
            f"role::{role_id}",
            path,
            method,
        )

    async def get_user_permissions(self, user_id: int) -> ListViewModel[PermissionViewModel]:
        permissions = await self.casbin_enforcer.enforcer.get_implicit_permissions_for_user(
            f"user::{user_id}"
        )

        permission_list = []
        for permission in permissions:
            _, path, method = permission
            permission_list.append((path, ActionMethod.load(method)))

        async with self.transaction_factory() as session:
            _, actions = await self.action_repo.fetch_list(
                session,
                QueryConfig(
                    condition=FindActionByPathAndMethod(path_and_method_tuple_list=permission_list),
                    order_by=[Action.create_at.desc()],
                    options=[joinedload(Action.menu)],
                ),
            )

            second_level_parent_ids = [
                action.menu.parent_id for action in actions if action.menu.parent_id is not None
            ]

            _, second_level_menu_parents = await self.menu_repo.fetch_list(
                session,
                QueryConfig(
                    condition=FindMenuByIDs(second_level_parent_ids),
                    order_by=[Menu.create_at.desc()],
                ),
            )

            second_level_menu_parents_map = {menu.id: menu for menu in second_level_menu_parents}

            first_level_menu_map = {}
            first_level_actions_map = {}
            second_level_menu_map = {}
            second_level_actions_map = {}

            for action in actions:
                if action.menu.parent_id is None:
                    # 一级菜单处理
                    first_level_menu_map[action.menu_id] = action.menu
                    action_set = first_level_actions_map.get(action.menu_id, set())
                    action_set.add(action)
                    first_level_actions_map[action.menu_id] = action_set

                else:
                    # 二级菜单处理
                    second_level_menu_map[action.menu_id] = action.menu
                    action_set = second_level_actions_map.get(action.menu_id, set())
                    action_set.add(action)
                    second_level_actions_map[action.menu_id] = action_set
            permissions_map = {}

            for menu_id, menu in first_level_menu_map.items():
                permissions_map[menu_id] = PermissionViewModel(
                    menu_id=menu_id,
                    menu_path=menu.path,
                    actions=[
                        PermissionActionViewModel(
                            action_name=action.name,
                            action_path=action.path,
                            action_method=action.method,
                        )
                        for action in first_level_actions_map.get(menu_id, set())
                    ],
                )

            for menu_id, menu in second_level_menu_map.items():
                if permissions_map.get(menu.parent_id, None) is not None:
                    parent_permission = permissions_map[menu.parent_id]
                else:
                    parent_menu = second_level_menu_parents_map[menu.parent_id]
                    parent_permission = PermissionViewModel(
                        menu_id=parent_menu.id,
                        menu_path=parent_menu.path,
                    )

                parent_permission.children.append(
                    PermissionViewModel(
                        menu_id=menu_id,
                        menu_path=menu.path,
                        actions=[
                            PermissionActionViewModel(
                                action_name=action.name,
                                action_path=action.path,
                                action_method=action.method,
                            )
                            for action in second_level_actions_map.get(menu_id, set())
                        ],
                    )
                )
                permissions_map[menu_id] = parent_permission
            return ListViewModel[PermissionViewModel](items=list(permissions_map.values()))
