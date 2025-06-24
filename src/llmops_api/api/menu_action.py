from typing import Annotated

from dependency_injector.wiring import Provide, inject
from fastapi import APIRouter, Depends, Path, Query

from llmops_api.base.response.base_response import BaseResponse
from llmops_api.base.view.model import ListViewModel
from llmops_api.const.constant import SUCCESS_CODE
from llmops_api.depends.auth import get_current_user_id
from llmops_api.form.menu_action import AddMenuActionForm
from llmops_api.service.action import ActionService
from llmops_api.view.action import ActionViewModel

router = APIRouter(
    prefix="/menu",
    tags=[
        "menu",
    ],
)


@router.get(
    "/{menu_id}/action",
    dependencies=[Depends(get_current_user_id)],
    description="获取菜单操作列表",
    response_model=BaseResponse[ListViewModel[ActionViewModel]],
)
@inject
async def menu_actions(
    action_service: Annotated[ActionService, Depends(Provide["action_module.action_service"])],
    menu_id: Annotated[int, Path(description="菜单ID")],
    query: Annotated[str, Query(description="查询参数")] = "",
):
    menu_list = await action_service.get_menu_actions(menu_id, query=query)
    return BaseResponse[ListViewModel[ActionViewModel]](
        code=SUCCESS_CODE, msg="获取菜单操作列表成功", data=menu_list
    )


@router.post(
    "/{menu_id}/action",
    description="添加菜单操作",
    response_model=BaseResponse[ActionViewModel],
)
@inject
async def add_menu_action(
    action_service: Annotated[ActionService, Depends(Provide["action_module.action_service"])],
    menu_id: Annotated[int, Path(description="菜单ID")],
    current_user_id: Annotated[int, Depends(get_current_user_id)],
    add_menu_action_form: AddMenuActionForm,
):
    action = add_menu_action_form.to_action()
    action.menu_id = menu_id
    action.create_by = current_user_id
    action_view = await action_service.add_menu_action(action)
    return BaseResponse[ActionViewModel](
        code=SUCCESS_CODE, msg="添加菜单操作成功", data=action_view
    )
