from typing import Annotated

from dependency_injector.wiring import Provide, inject
from fastapi import APIRouter, Depends, Path, Query

from llmops_api.base.response.base_response import Base, BaseResponse
from llmops_api.base.view.model import PaginationListViewModel
from llmops_api.const.constant import SUCCESS_CODE
from llmops_api.depends.auth import get_current_user_id
from llmops_api.form.user import AddUserForm, EditUserForm, UserListQuery
from llmops_api.service.user import UserService
from llmops_api.view.user import UserViewModel

router = APIRouter(prefix="/user", tags=["user"])


@router.post(
    "",
    description="创建用户",
    response_model=BaseResponse[UserViewModel],
)
@inject
async def add_user(
    user_service: Annotated[
        UserService,
        Depends(Provide["user_module.user_service"]),
    ],
    current_user_id: Annotated[int, Depends(get_current_user_id)],
    add_user_form: AddUserForm,
):
    user = add_user_form.convert_to_user()
    user.create_by = current_user_id
    user_view = await user_service.add_user(user)
    return BaseResponse[UserViewModel](code=SUCCESS_CODE, data=user_view, msg="成功")


@router.get(
    "/{user_id}",
    description="用户详情",
    dependencies=[Depends(get_current_user_id)],
    response_model=BaseResponse[UserViewModel],
)
@inject
async def get_user(
    user_service: Annotated[
        UserService,
        Depends(Provide["user_module.user_service"]),
    ],
    user_id: Annotated[int, Path(description="用户ID")],
):
    user = await user_service.get_user(user_id)
    return BaseResponse[UserViewModel](code=SUCCESS_CODE, msg="成功", data=user)


@router.delete("/{user_id}", description="删除用户", response_model=BaseResponse[Base])
@inject
async def delete_user(
    user_service: Annotated[
        UserService,
        Depends(Provide["user_module.user_service"]),
    ],
    user_id: Annotated[int, Path(description="用户ID")],
    current_user_id: Annotated[int, Depends(get_current_user_id)],
):
    await user_service.delete_user(user_id, current_user_id)
    return BaseResponse[Base](code=SUCCESS_CODE, msg="删除成功", data={})  # type: ignore


@router.put(
    "/{user_id}",
    description="编辑用户",
    dependencies=[Depends(get_current_user_id)],
    response_model=BaseResponse[UserViewModel],
)
@inject
async def edit_user(
    user_service: Annotated[
        UserService,
        Depends(Provide["user_module.user_service"]),
    ],
    user_id: Annotated[int, Path(description="用户ID")],
    edit_user_form: EditUserForm,
    current_user_id: Annotated[int, Depends(get_current_user_id)],
):
    values = edit_user_form.model_dump(exclude_unset=True)
    values.update({"update_by": current_user_id})
    user = await user_service.edit_user(user_id, **values)

    return BaseResponse[UserViewModel](code=SUCCESS_CODE, msg="修改用户成功", data=user)


@router.get(
    "",
    description="用户列表",
    dependencies=[Depends(get_current_user_id)],
    response_model=BaseResponse[PaginationListViewModel[UserViewModel]],
)
@inject
async def user_list(
    user_service: Annotated[
        UserService,
        Depends(Provide["user_module.user_service"]),
    ],
    user_list_query: Annotated[UserListQuery, Query()],
):
    user_list = await user_service.user_list(user_list_query)
    return BaseResponse[PaginationListViewModel[UserViewModel]](
        code=SUCCESS_CODE, msg="获取用户列表成功", data=user_list
    )
