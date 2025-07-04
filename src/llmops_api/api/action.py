from typing import Annotated

from dependency_injector.wiring import Provide, inject
from fastapi import APIRouter, Depends, Path

from llmops_api.base.response.base_response import Base, BaseResponse
from llmops_api.const.constant import SUCCESS_CODE
from llmops_api.depends.auth import get_current_user_id
from llmops_api.form.action import EditActionForm
from llmops_api.service.action import ActionService
from llmops_api.view.action import ActionViewModel

router = APIRouter(
    prefix="/action",
    tags=[
        "action",
    ],
)


@router.get(
    "/{action_id}",
    dependencies=[Depends(get_current_user_id)],
    description="获取操作",
    response_model=BaseResponse[ActionViewModel],
)
@inject
async def get_action(
    action_service: Annotated[ActionService, Depends(Provide["action_module.action_service"])],
    action_id: Annotated[int, Path(description="操作ID")],
):
    action = await action_service.get_action(action_id)
    return BaseResponse[ActionViewModel](code=SUCCESS_CODE, msg="获取菜单操作成功", data=action)


@router.delete(
    "/{action_id}",
    dependencies=[Depends(get_current_user_id)],
    description="删除操作",
    response_model=BaseResponse[Base],
)
@inject
async def delete_action(
    action_service: Annotated[ActionService, Depends(Provide["action_module.action_service"])],
    action_id: Annotated[int, Path(description="操作ID")],
):
    await action_service.delete_action(action_id)
    return BaseResponse[Base](code=SUCCESS_CODE, msg="删除操作成功", data={})


@router.put(
    "/{action_id}",
    description="编辑菜单操作",
    response_model=BaseResponse[ActionViewModel],
)
@inject
async def edit_action(
    action_service: Annotated[ActionService, Depends(Provide["action_module.action_service"])],
    current_user_id: Annotated[int, Depends(get_current_user_id)],
    action_id: Annotated[int, Path(description="操作ID")],
    edit_action_form: EditActionForm,
):
    kwargs = edit_action_form.model_dump(exclude_unset=True)
    kwargs.update({"update_by": current_user_id})

    action = await action_service.edit_action(action_id, **kwargs)
    return BaseResponse[ActionViewModel](code=SUCCESS_CODE, msg="更新菜单操作成功", data=action)
