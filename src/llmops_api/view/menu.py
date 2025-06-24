from typing import Annotated, List, Optional

from pydantic import Field

from llmops_api.base.view.model import OperatorRecordModel
from llmops_api.base.view.relation import Relation
from llmops_api.enum.menu import MenuType
from llmops_api.view.action import ActionViewModel


class MenuViewModel(OperatorRecordModel):
    id: Annotated[
        int,
        Field(description="菜单ID"),
    ]

    name: Annotated[
        str,
        Field(description="菜单名称"),
    ]

    title: Annotated[
        str,
        Field(description="菜单标题"),
    ]

    path: Annotated[
        str,
        Field(description="菜单路径"),
    ]

    icon: Annotated[
        Optional[str],
        Field(description="菜单图标", default=None),
    ]

    icon_filled: Annotated[
        Optional[str],
        Field(description="菜单图标(filled)", default=None),
    ]

    menu_type: Annotated[
        MenuType,
        Field(description="菜单类型"),
    ]

    parent_id: Annotated[
        Optional[int],
        Field(
            description="父菜单ID",
            default=None,
        ),
    ]

    parent: Annotated[
        Optional["MenuViewModel"],
        Field(default=None, description="父菜单"),
        Relation(
            pydantic_model="self",
        ),
    ]

    children: Annotated[
        List["MenuViewModel"],
        Field(default_factory=list, description="子菜单列表"),
        Relation(
            pydantic_model="self",
        ),
    ]

    actions: Annotated[
        List[ActionViewModel],
        Field(default_factory=list, description="操作列表"),
        Relation(
            pydantic_model=ActionViewModel,
        ),
    ]
