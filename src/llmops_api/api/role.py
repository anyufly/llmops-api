from typing import Annotated

from dependency_injector.wiring import Provide, inject
from fastapi import APIRouter, Depends, Path, Query

from llmops_api.base.response.base_response import Base, BaseResponse
from llmops_api.base.view.model import ListViewModel
from llmops_api.const.constant import SUCCESS_CODE
from llmops_api.depends.auth import get_current_user_id
from llmops_api.form.role import AddRoleForm, EditRoleForm
from llmops_api.service.role import RoleService
from llmops_api.view.role import RoleViewModel

router = APIRouter(prefix="/role", tags=["role"])


@router.get(
    "",
    dependencies=[Depends(get_current_user_id)],
    response_model=BaseResponse[ListViewModel[RoleViewModel]],
)
@inject
async def role_list(
    role_service: Annotated[RoleService, Depends(Provide["role_module.role_service"])],
    query: Annotated[str, Query(description="查询字段")] = "",
):
    role_list = await role_service.role_list(query)
    return BaseResponse[ListViewModel[RoleViewModel]](
        code=SUCCESS_CODE, msg="获取角色列表成功", data=role_list
    )


@router.get(
    "/{role_id}",
    dependencies=[Depends(get_current_user_id)],
    response_model=BaseResponse[RoleViewModel],
    description="获取角色",
)
@inject
async def get_role(
    role_service: Annotated[RoleService, Depends(Provide["role_module.role_service"])],
    role_id: Annotated[int, Path(description="角色ID")],
):
    role = await role_service.get_role(role_id)
    return BaseResponse[RoleViewModel](code=SUCCESS_CODE, msg="获取角色列表成功", data=role)


@router.post(
    "",
    response_model=BaseResponse[RoleViewModel],
    description="添加角色",
)
@inject
async def add_role(
    role_service: Annotated[RoleService, Depends(Provide["role_module.role_service"])],
    current_user_id: Annotated[int, Depends(get_current_user_id)],
    add_role_form: AddRoleForm,
):
    role = add_role_form.to_role()
    role.create_by = current_user_id
    role_view = await role_service.add_role(role)
    return BaseResponse[RoleViewModel](code=SUCCESS_CODE, msg="获取角色列表成功", data=role_view)


@router.put(
    "/{role_id}",
    response_model=BaseResponse[RoleViewModel],
    description="编辑角色",
)
@inject
async def edit_role(
    role_service: Annotated[RoleService, Depends(Provide["role_module.role_service"])],
    current_user_id: Annotated[int, Depends(get_current_user_id)],
    role_id: Annotated[int, Path(description="角色ID")],
    edit_role_form: EditRoleForm,
):
    kwargs = edit_role_form.model_dump(exclude_unset=True)
    kwargs.update({"update_by": current_user_id})
    role = await role_service.edit_role(role_id, **kwargs)
    return BaseResponse[RoleViewModel](code=SUCCESS_CODE, msg="获取角色列表成功", data=role)


@router.delete(
    "/{role_id}",
    response_model=BaseResponse[Base],
    description="删除角色",
)
@inject
async def delete_role(
    role_service: Annotated[RoleService, Depends(Provide["role_module.role_service"])],
    current_user_id: Annotated[int, Depends(get_current_user_id)],
    role_id: Annotated[int, Path(description="角色ID")],
):
    await role_service.delete_role(role_id, delete_by=current_user_id)
    return BaseResponse[Base](code=SUCCESS_CODE, data={}, msg="删除角色成功")
