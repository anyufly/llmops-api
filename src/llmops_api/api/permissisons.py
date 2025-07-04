from typing import Annotated

from dependency_injector.wiring import Provide, inject
from fastapi import APIRouter, Depends, Path, Query

from llmops_api.base.db.repo import Paginator
from llmops_api.base.response.base_response import Base, BaseResponse
from llmops_api.base.view.model import ListViewModel, PaginationListViewModel
from llmops_api.const.constant import SUCCESS_CODE
from llmops_api.depends.auth import get_current_user_id
from llmops_api.form.permissions import (
    AddRoleActionForm,
    AddUserRoleForm,
    DeleteRoleActionForm,
    DeleteUserRoleForm,
)
from llmops_api.service.permissions import PermissionsService
from llmops_api.view.action import ActionViewModel
from llmops_api.view.permissions import PermissionViewModel
from llmops_api.view.role import RoleViewModel
from llmops_api.view.user import UserViewModel

router = APIRouter(
    prefix="/permissions",
    tags=["permissions"],
)


@router.get(
    "/user_role/{user_id}",
    dependencies=[Depends(get_current_user_id)],
    description="获取用户角色",
    response_model=BaseResponse[ListViewModel[RoleViewModel]],
)
@inject
async def get_user_roles(
    permissions_service: Annotated[
        PermissionsService, Depends(Provide["permissions_module.permissions_service"])
    ],
    user_id: Annotated[int, Path(description="用户ID")],
):
    user_list = await permissions_service.get_roles_for_user(user_id)
    return BaseResponse[ListViewModel[RoleViewModel]](
        code=SUCCESS_CODE, data=user_list, msg="获取用户角色成功"
    )


@router.get(
    "/role_user/{role_id}",
    dependencies=[Depends(get_current_user_id)],
    description="获取角色用户",
    response_model=BaseResponse[PaginationListViewModel[UserViewModel]],
)
@inject
async def get_role_users(
    permissions_service: Annotated[
        PermissionsService, Depends(Provide["permissions_module.permissions_service"])
    ],
    role_id: Annotated[int, Path(description="角色ID")],
    paginator: Annotated[Paginator, Query()],
):
    role_list = await permissions_service.get_users_for_role(role_id, paginator)
    return BaseResponse[PaginationListViewModel[UserViewModel]](
        code=SUCCESS_CODE, data=role_list, msg="获取角色用户成功"
    )


@router.post(
    "/role_user",
    dependencies=[Depends(get_current_user_id)],
    description="添加角色用户",
    response_model=BaseResponse[Base],
)
@inject
async def add_role_for_user(
    permissions_service: Annotated[
        PermissionsService, Depends(Provide["permissions_module.permissions_service"])
    ],
    add_user_role_form: AddUserRoleForm,
):
    await permissions_service.add_role_for_user(
        add_user_role_form.user_id, add_user_role_form.role_id
    )

    return BaseResponse[Base](code=SUCCESS_CODE, data={}, msg="添加用户角色成功")  # type: ignore


@router.delete(
    "/role_user",
    dependencies=[Depends(get_current_user_id)],
    description="删除角色用户",
    response_model=BaseResponse[Base],
)
@inject
async def delete_role_for_user(
    permissions_service: Annotated[
        PermissionsService, Depends(Provide["permissions_module.permissions_service"])
    ],
    delete_user_role_form: DeleteUserRoleForm,
):
    await permissions_service.delete_role_for_user(
        delete_user_role_form.user_id, delete_user_role_form.role_id
    )

    return BaseResponse[Base](code=SUCCESS_CODE, data={}, msg="删除用户角色成功")  # type: ignore


@router.post(
    "/role_action",
    dependencies=[Depends(get_current_user_id)],
    description="添加角色权限",
    response_model=BaseResponse[Base],
)
@inject
async def add_action_for_role(
    permissions_service: Annotated[
        PermissionsService, Depends(Provide["permissions_module.permissions_service"])
    ],
    add_role_action_form: AddRoleActionForm,
):
    await permissions_service.add_action_for_role(
        add_role_action_form.role_id, add_role_action_form.action_id
    )

    return BaseResponse[Base](code=SUCCESS_CODE, data={}, msg="添加角色权限成功")  # type: ignore


@router.delete(
    "/role_action",
    dependencies=[Depends(get_current_user_id)],
    description="删除角色权限",
    response_model=BaseResponse[Base],
)
@inject
async def delete_action_for_role(
    permissions_service: Annotated[
        PermissionsService, Depends(Provide["permissions_module.permissions_service"])
    ],
    delete_role_action_form: DeleteRoleActionForm,
):
    await permissions_service.delete_action_for_role(
        delete_role_action_form.role_id, delete_role_action_form.action_id
    )

    return BaseResponse[Base](code=SUCCESS_CODE, data={}, msg="删除角色权限成功")  # type: ignore


@router.get(
    "/role_action/{role_id}",
    dependencies=[Depends(get_current_user_id)],
    description="获取角色权限",
)
@inject
async def get_role_actions(
    permissions_service: Annotated[
        PermissionsService, Depends(Provide["permissions_module.permissions_service"])
    ],
    role_id: Annotated[int, Path(description="角色ID")],
):
    action_list = await permissions_service.get_action_for_role(role_id)
    return BaseResponse[ListViewModel[ActionViewModel]](
        data=action_list, code=SUCCESS_CODE, msg="获取角色权限"
    )


@router.get(
    "/user_permission/{user_id}",
    dependencies=[Depends(get_current_user_id)],
    description="获取用户权限",
    response_model=BaseResponse[ListViewModel[PermissionViewModel]],
)
@inject
async def get_user_permissions(
    permissions_service: Annotated[
        PermissionsService, Depends(Provide["permissions_module.permissions_service"])
    ],
    user_id: Annotated[int, Path(description="用户ID")],
):
    user_permissions = await permissions_service.get_user_permissions(user_id)
    return BaseResponse[ListViewModel[PermissionViewModel]](
        data=user_permissions, code=SUCCESS_CODE, msg="获取用户权限成功"
    )
