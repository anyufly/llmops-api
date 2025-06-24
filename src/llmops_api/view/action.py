from typing import Annotated

from pydantic import Field

from llmops_api.base.view.model import OperatorRecordModel
from llmops_api.enum.menu import ActionMethod


class ActionViewModel(OperatorRecordModel):
    id: Annotated[
        int,
        Field(description="操作ID"),
    ]

    name: Annotated[
        str,
        Field(description="操作名称"),
    ]

    title: Annotated[
        str,
        Field(description="操作标题"),
    ]

    path: Annotated[
        str,
        Field(description="操作对应接口路径"),
    ]

    method: Annotated[
        ActionMethod,
        Field(description="操作对应接口方法"),
    ]
