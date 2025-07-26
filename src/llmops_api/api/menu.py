from typing import Annotated

from dependency_injector.wiring import Provide, inject
from fastapi import APIRouter, Depends, Path, Query

from llmops_api.base.response.base_response import BaseResponse, Empty
from llmops_api.base.view.model import ListViewModel
from llmops_api.const.constant import SUCCESS_CODE
from llmops_api.depends.auth import get_current_user_id
from llmops_api.form.menu import (
    AddFirstLevelMenuForm,
    AddSecondLevelMenuForm,
    EditMenuForm,
    MenuQuery,
)
from llmops_api.service.menu import MenuService
from llmops_api.view.menu import MenuViewModel

router = APIRouter(
    prefix="/menu",
    tags=["menu"],
)


@router.get(
    "",
    description="菜单列表",
    response_model=BaseResponse[ListViewModel[MenuViewModel]],
    dependencies=[Depends(get_current_user_id)],
)
@inject
async def menu_list(
    menu_service: Annotated[MenuService, Depends(Provide["menu_module.menu_service"])],
    menu_query: Annotated[MenuQuery, Query()],
):
    menu_list = await menu_service.menu_list(menu_query)
    return BaseResponse[ListViewModel[MenuViewModel]](
        code=SUCCESS_CODE, msg="获取菜单列表成功", data=menu_list
    )


@router.get(
    "/{menu_id}",
    dependencies=[Depends(get_current_user_id)],
    response_model=BaseResponse[MenuViewModel],
    description="获取菜单详情",
)
@inject
async def get_menu(
    menu_service: Annotated[MenuService, Depends(Provide["menu_module.menu_service"])],
    menu_id: Annotated[int, Path(title="menu_id", description="菜单ID")],
):
    menu = await menu_service.get_menu(menu_id)
    return BaseResponse[MenuViewModel](code=SUCCESS_CODE, msg="获取菜单成功", data=menu)


@router.post(
    "",
    response_model=BaseResponse[MenuViewModel],
    description="添加一级菜单",
)
@inject
async def add_first_level_menu(
    menu_service: Annotated[MenuService, Depends(Provide["menu_module.menu_service"])],
    current_user_id: Annotated[int, Depends(get_current_user_id)],
    add_first_level_menu_form: AddFirstLevelMenuForm,
):
    menu = add_first_level_menu_form.to_menu()
    menu.create_by = current_user_id
    menu_view = await menu_service.add_menu(menu)

    return BaseResponse[MenuViewModel](code=SUCCESS_CODE, msg="添加一级菜单成功", data=menu_view)


@router.post(
    "/{parent_menu_id}",
    response_model=BaseResponse[MenuViewModel],
    description="添加二级菜单",
)
@inject
async def add_second_level_menu(
    menu_service: Annotated[MenuService, Depends(Provide["menu_module.menu_service"])],
    current_user_id: Annotated[int, Depends(get_current_user_id)],
    parent_menu_id: Annotated[int, Path(description="父菜单ID")],
    add_second_level_menu_form: AddSecondLevelMenuForm,
):
    menu = add_second_level_menu_form.to_menu()
    menu.create_by = current_user_id
    menu_view = await menu_service.add_child_menu(parent_menu_id, menu)
    return BaseResponse[MenuViewModel](code=SUCCESS_CODE, msg="添加二级菜单成功", data=menu_view)


@router.put(
    "/{menu_id}",
    response_model=BaseResponse[MenuViewModel],
    description="编辑菜单",
)
@inject
async def edit_menu(
    menu_service: Annotated[MenuService, Depends(Provide["menu_module.menu_service"])],
    current_user_id: Annotated[int, Depends(get_current_user_id)],
    menu_id: Annotated[int, Path(description="菜单ID")],
    edit_menu_form: EditMenuForm,
):
    kwargs = edit_menu_form.model_dump(exclude_unset=True)
    kwargs.update({"update_by": current_user_id})

    menu = await menu_service.edit_menu(menu_id, **kwargs)
    return BaseResponse[MenuViewModel](code=SUCCESS_CODE, msg="编辑菜单成功", data=menu)


@router.delete(
    "/{menu_id}",
    response_model=BaseResponse[Empty],
    description="删除菜单",
)
@inject
async def delete_menu(
    menu_service: Annotated[MenuService, Depends(Provide["menu_module.menu_service"])],
    current_user_id: Annotated[int, Depends(get_current_user_id)],
    menu_id: Annotated[int, Path(description="菜单ID")],
):
    await menu_service.delete_menu(menu_id, delete_by=current_user_id)
    return BaseResponse[Empty](code=SUCCESS_CODE, msg="删除菜单成功", data=Empty())
