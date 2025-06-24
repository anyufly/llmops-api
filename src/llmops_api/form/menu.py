from typing import Annotated, Optional

from pydantic import BaseModel, Field

from llmops_api.enum.menu import MenuType
from llmops_api.model.menu import Menu


class MenuQuery(BaseModel):
    query: Annotated[str, Field(default="", description="query")]
    menu_type: Annotated[Optional[MenuType], Field(default=None, description="菜单类型")]


class AddFirstLevelMenuForm(BaseModel):
    name: Annotated[str, Field(description="菜单名称")]
    title: Annotated[str, Field(description="菜单标题")]
    path: Annotated[str, Field(description="菜单路径")]
    icon: Annotated[Optional[str], Field(description="菜单图标", default=None)]
    icon_filled: Annotated[Optional[str], Field(description="菜单图标（filled）", default=None)]
    menu_type: Annotated[MenuType, Field(description="菜单类型")]

    def to_menu(self):
        return Menu(**self.model_dump())


class AddSecondLevelMenuForm(BaseModel):
    name: Annotated[str, Field(description="菜单名称")]
    title: Annotated[str, Field(description="菜单标题")]
    path: Annotated[str, Field(description="菜单路径")]

    def to_menu(self):
        return Menu(**self.model_dump())


class EditMenuForm(BaseModel):
    name: Annotated[Optional[str], Field(description="菜单名称", default=None)]
    title: Annotated[Optional[str], Field(description="菜单标题", default=None)]
    path: Annotated[Optional[str], Field(description="菜单路径", default=None)]
    icon: Annotated[Optional[str], Field(description="菜单图标", default=None)]
    icon_filled: Annotated[Optional[str], Field(description="菜单图标（filled）", default=None)]
    menu_type: Annotated[Optional[MenuType], Field(description="菜单类型", default=None)]
