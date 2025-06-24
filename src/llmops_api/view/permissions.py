from typing import Annotated, List

from pydantic import BaseModel, Field


class PermissionActionViewModel(BaseModel):
    action_name: Annotated[str, Field(description="操作名称")]
    action_path: Annotated[str, Field(description="操作对应后端接口路径")]
    action_method: Annotated[str, Field(description="操作对应后端接口方法")]


class PermissionViewModel(BaseModel):
    menu_id: Annotated[int, Field(description="菜单ID")]
    menu_path: Annotated[str, Field(description="菜单路径")]
    actions: Annotated[
        List[PermissionActionViewModel], Field(description="有权限的操作列表", default_factory=list)
    ]
    children: Annotated[
        List["PermissionViewModel"],
        Field(description="子菜单权限", default_factory=list),
    ]
